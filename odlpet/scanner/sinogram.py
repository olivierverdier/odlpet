"""
Utility functions to compute the sinogram offsets.
"""

import numpy as np


def get_offset_(segment_, axial, info):
    mid = len(info)//2
    reordered = [info[mid]] + [val for pair in zip(info[mid+1:], info[mid-1::-1]) for val in pair]
    ar = np.array(reordered)
    if segment_ == 0:
        seg_offset = 0
    else:
        seg_offset = np.cumsum(ar[:,1])[segment_-1]
    return seg_offset + axial

def segment_reordered_(segment):
    if segment == 0:
        return segment
    if segment > 0:
        return segment*2 - 1
    if segment < 0:
        return -2*segment

def get_offset(segment, axial, info):
    return get_offset_(segment_reordered_(segment), axial, info)
