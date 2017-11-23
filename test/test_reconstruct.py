import pytest

import numpy as np

from odlpet.stir.bindings import stir_projector_from_memory
from odlpet.scanner.scanner import mCT

import odlpet.utils.phantom

from odlpet.stir.setup import (
    stir_get_ODL_domain_which_honours_STIR_restrictions,
    stir_get_STIR_domain_from_ODL,
    stir_get_ODL_domain_from_STIR,
    stir_get_projection_data_info,
    stir_get_projection_data,
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

    stir_scanner = scanner.get_stir_scanner()

    span_num = 1
    max_num_segments = 3
    num_of_views = scanner.num_dets_per_ring / 2
    num_non_arccor_bins = scanner.num_dets_per_ring / 2
    data_arc_corrected = False
    proj_info = stir_get_projection_data_info(stir_scanner, span_num,
                                                    max_num_segments, num_of_views,
                                                    num_non_arccor_bins, data_arc_corrected,
                                                    stir_domain)

    initialize_to_zero = True
    proj_data = stir_get_projection_data(proj_info, initialize_to_zero)

    dummy_discr_dom_odl = stir_get_ODL_domain_from_STIR(stir_domain)

    proj = stir_projector_from_memory(dummy_discr_dom_odl, stir_domain, proj_data, proj_info)

    phantom = odlpet.utils.phantom.derenzo(proj.domain)
    # phantom = proj.domain.one()

    import odl

    ms = []
    for i in range(2):
        back_proj = proj.adjoint(proj.range.one())
        s_min = np.min(back_proj)
        s_max = np.max(back_proj)
        recon = proj.domain.one()
        proj(recon)
        ms.append((s_min, s_max))
    print(ms)
    assert pytest.approx(ms[0]) == ms[1]

