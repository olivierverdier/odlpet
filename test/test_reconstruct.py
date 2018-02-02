import pytest

import numpy as np

from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

import odlpet.utils.phantom


def test_purity():
    """
    The STIR projector seems to have side effects
    """
    scanner = mCT()
    compression = Compression(scanner)
    compression.max_num_segments = 3

    proj = compression.get_projector()

    phantom = proj.domain.one()

    ms = []
    for i in range(2):
        back_proj = proj.adjoint(proj.range.one())
        s_min = np.min(back_proj)
        s_max = np.max(back_proj)
        ms.append((s_min, s_max))
    # print(ms)
    assert pytest.approx(ms[0]) == ms[1]

