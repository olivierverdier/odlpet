from os import path
import odl


from odlpet.stir.setup import (
    stir_get_ODL_domain_which_honours_STIR_restrictions,
    stir_get_STIR_domain_from_ODL,
    stir_get_ODL_domain_from_STIR,
)

from odlpet.stir.bindings import stir_projector_from_memory, stir_projector_from_file
from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

def test_memory_run():
    """
    Check that a simple setup runs without errors.
    """
    discr_dom_odl = stir_get_ODL_domain_which_honours_STIR_restrictions([2**6, 2**6, 15], [2.05941, 2.05941, 3.125])
    stir_domain = stir_get_STIR_domain_from_ODL(discr_dom_odl, 0.0)
    scanner = mCT()
    compression = Compression(scanner)
    dummy_discr_dom_odl = stir_get_ODL_domain_from_STIR(stir_domain)
    proj = stir_projector_from_memory(dummy_discr_dom_odl, stir_domain, compression)
    result = proj(proj.domain.one())

def test_file_run():
    """
    Test that loading from file runs without errors.
    """
    # Load STIR input files with data
    base = path.join(path.dirname(path.abspath(__file__)), path.pardir, 'examples', 'tomo', 'data', 'stir')

    volume_file = str(path.join(base, 'initial.hv'))
    projection_file = str(path.join(base, 'small.hs'))

    # Make STIR projector
    proj = stir_projector_from_file(volume_file, projection_file)

    # Create Shepp-Logan phantom
    vol = odl.phantom.shepp_logan(proj.domain, modified=True)

    # Project and show
    result = proj(vol)

# TODO: test that loading from file or memory gives the same result.
