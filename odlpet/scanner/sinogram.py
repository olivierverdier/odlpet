"""
Utility functions related to sinograms.
"""

import numpy as np
import odl


def get_segment_offset(segment_, info):
    mid = len(info)//2
    reordered = [info[mid]] + [val for pair in zip(info[mid+1:], info[mid-1::-1]) for val in pair]
    ar = np.array(reordered)
    if segment_ == 0:
        seg_offset = 0
    else:
        seg_offset = np.cumsum(ar[:,1])[segment_-1]
    return seg_offset

def segment_reordered_(segment):
    if segment == 0:
        return segment
    if segment > 0:
        return segment*2 - 1
    if segment < 0:
        return -2*segment

def get_offset(segment, axial, info):
    dinfo = dict(info)
    try:
        max_axial = dinfo[segment]
    except KeyError:
        raise ValueError("Segment {} not in {}".format(segment, list(dinfo.keys())))
    if not 0 <= axial < max_axial:
        raise ValueError("Segment {}: Axial offset violation: 0 <= {} < {}".format(segment, axial, max_axial))
    seg_offset = get_segment_offset(segment_reordered_(segment), info)
    return seg_offset + axial

def get_range_from_proj_data(proj_data, radius=1.):
    """
    Get an ODL codomain (range) from the projection data.

    The second coordinate is an angle.
    The last one is a tangential coordinate, normalised between -1 and 1.
    `radius`: units for the tangential coordinates
    """
    num_sinograms = proj_data.get_num_sinograms()
    num_views = proj_data.get_num_views()
    num_tans = proj_data.get_num_tangential_poss()
    shape = (num_sinograms, num_views, num_tans)
    min_pt = [0, 0, -radius]
    max_pt = [num_sinograms, np.pi, radius]
    data_sp = odl.discr.uniform_discr(min_pt=min_pt,
                            max_pt=max_pt,
                            shape=shape,
                            axis_labels=("(dz,z)", "φ", "s"),
                            dtype='float32')
    return data_sp
