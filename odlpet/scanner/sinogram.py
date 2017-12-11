"""
Utility functions to compute the sinogram offsets.
"""

import numpy as np


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
