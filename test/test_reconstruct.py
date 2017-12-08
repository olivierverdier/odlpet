import pytest

import numpy as np

from odlpet.stir.bindings import stir_projector_from_memory
from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

import odlpet.utils.phantom

from odlpet.stir.setup import (
    stir_get_ODL_domain_which_honours_STIR_restrictions,
    stir_get_STIR_domain_from_ODL,
    stir_get_ODL_domain_from_STIR,
)
from odlpet.stir.bindings import stir_projector_from_memory
from odlpet.scanner.scanner import mCT

def test_purity():
    """
    The STIR projector seems to have side effects
    """
    discr_dom_odl = stir_get_ODL_domain_which_honours_STIR_restrictions([2**5, 2**5, 15], [2.05941, 2.05941, 3.125])

    stir_domain = stir_get_STIR_domain_from_ODL(discr_dom_odl, 0.0)

    scanner = mCT()
    compression = Compression(scanner)
    compression.max_num_segments = 3

    dummy_discr_dom_odl = stir_get_ODL_domain_from_STIR(stir_domain)

    proj = stir_projector_from_memory(dummy_discr_dom_odl, stir_domain, compression)

    phantom = proj.domain.one()

    ms = []
    for i in range(2):
        back_proj = proj.adjoint(proj.range.one())
        s_min = np.min(back_proj)
        s_max = np.max(back_proj)
        ms.append((s_min, s_max))
    # print(ms)
    assert pytest.approx(ms[0]) == ms[1]

