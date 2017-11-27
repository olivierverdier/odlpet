import numpy as np
import numpy.testing as npt

import os.path

from odlpet.stir.setup import (
    stir_get_ODL_domain_which_honours_STIR_restrictions,
    stir_get_STIR_domain_from_ODL,
    stir_get_ODL_domain_from_STIR,
    stir_get_STIR_geometry,
    stir_get_projection_data_info,
    stir_get_projection_data,
)
from odlpet.stir.bindings import stir_projector_from_memory
from odlpet.scanner.scanner import mCT
import odlpet.utils.phantom

def test_regression():
    """
    Check that the projector gives the same fixed result stored in a file.
    """
    discr_dom_odl = stir_get_ODL_domain_which_honours_STIR_restrictions([2**6, 2**6, 15], [2.05941, 2.05941, 3.125])

    stir_domain = stir_get_STIR_domain_from_ODL(discr_dom_odl, 0.0)

    scanner = mCT()

    stir_scanner = scanner.get_stir_scanner()

    span_num = 1
    max_num_segments = 3
    num_of_views = scanner.num_dets_per_ring / 2
    num_non_arccor_bins = scanner.num_dets_per_ring / 2
    data_arc_corrected = False
    proj_info = stir_get_projection_data_info(stir_scanner, span_num, max_num_segments, num_of_views, num_non_arccor_bins, data_arc_corrected, stir_domain)

    initialize_to_zero = True
    proj_data = stir_get_projection_data(proj_info, initialize_to_zero)

    dummy_discr_dom_odl = stir_get_ODL_domain_from_STIR(stir_domain)


    proj = stir_projector_from_memory(dummy_discr_dom_odl, stir_domain, proj_data, proj_info)

    phantom = odlpet.utils.phantom.derenzo(proj.domain)

    projections = proj(phantom)

    here = os.path.dirname(__file__)
    data_path = os.path.join(here, "data", "projections.npy")
    print(data_path)
    expected = np.load(data_path)

    print("Difference:", np.max(np.abs(projections.asarray() - expected)))
    npt.assert_allclose(projections.asarray(), expected)

