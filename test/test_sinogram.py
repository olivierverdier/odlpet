import pytest
import stirextra
import numpy as np
from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

def test_sinogram():
    """
    Make sure that the sinogram offsets are correct.
    """
    scanner = mCT()
    compression = Compression(scanner)
    compression.max_num_segments = 3

    proj = compression.get_projector()

    phantom = proj.domain.element(np.random.randn(*proj.domain.shape))
    projections = proj(phantom)

    sinfo = compression.get_sinogram_info()

    seg_ind = np.random.randint(len(sinfo))
    segment = sinfo[seg_ind][0]
    ax_ind = np.random.randint(sinfo[seg_ind][1])

    print(sinfo, segment, ax_ind)

    offset = compression.get_offset(segment, ax_ind)
    computed = projections[offset].asarray()
    expected = stirextra.to_numpy(proj.proj_data.get_sinogram(ax_ind, segment))
    assert pytest.approx(computed) == expected


