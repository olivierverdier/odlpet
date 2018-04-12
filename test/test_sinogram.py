import pytest
import stirextra
import numpy as np
from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression
from odlpet.scanner.sinogram import get_shape_from_proj_data
import stir

def get_projections(scanner):
    compression = Compression(scanner)
    compression.max_num_segments = 3

    proj = compression.get_projector()

    phantom = proj.domain.element(np.random.randn(*proj.domain.shape))
    projections = proj(phantom)
    return compression, proj, projections

def test_sinogram():
    """
    Make sure that the sinogram offsets are correct.
    """
    scanner = mCT()
    compression, proj, projections = get_projections(scanner)

    sinfo = compression._get_sinogram_info()

    seg_ind = np.random.randint(len(sinfo))
    segment = sinfo[seg_ind][0]
    ax_ind = np.random.randint(sinfo[seg_ind][1])


    offset = compression.get_offset(segment, ax_ind)
    computed = projections[offset].asarray()
    expected = stirextra.to_numpy(proj.proj_data.get_sinogram(ax_ind, segment))
    assert pytest.approx(computed) == expected

def test_wrong_sinogram():
    """
    Bound controls for sinograms (wrong segment or wrong axial coordinate)
    """
    scanner = mCT()
    compression, proj, projections = get_projections(scanner)
    sinfo = compression._get_sinogram_info()
    segments = [si[0] for si in sinfo]
    maxax = [si[1] for si in sinfo]
    min_seg = np.min(segments)
    max_seg = np.max(segments)
    with pytest.raises(ValueError):
        compression.get_offset(min_seg - 1, 0)
    with pytest.raises(ValueError):
        compression.get_offset(max_seg + 1, 0)
    for s,a in sinfo:
        with pytest.raises(ValueError):
            compression.get_offset(s, a+1)


def test_shape():
    s = stir.Scanner.get_scanner_from_name("ECAT 962")
    projdatainfo = stir.ProjDataInfo.ProjDataInfoCTI(s,3,9,8,6)
    projdata = stir.ProjDataInMemory(stir.ExamInfo(), projdatainfo)
    shape = get_shape_from_proj_data(projdata)
    assert shape == projdata.to_array().shape()
