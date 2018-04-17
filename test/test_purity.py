import pytest

import numpy as np

from odlpet.scanner.scanner import Scanner
from odlpet.scanner.compression import Compression

import odlpet.utils.phantom


def test_purity():
    """
    The STIR projector seems to have side effects
    """
    compression = Compression(Scanner())
    compression.num_non_arccor_bins = 10
    compression.num_of_views = 10

    proj = compression.get_projector(stir_domain=compression.get_stir_domain(zoom=.5))

    phantom = proj.domain.one()

    ms = []
    for i in range(2):
        back_proj = proj.adjoint(proj.range.one())
        s_min = np.min(back_proj)
        s_max = np.max(back_proj)
        ms.append((s_min, s_max))
    # print(ms)
    assert pytest.approx(ms[0]) == ms[1]

