from os import path
import odl



from odlpet.stir.bindings import stir_projector_from_memory, stir_projector_from_file
from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

def test_memory_run():
    """
    Check that a simple setup runs without errors.
    """
    scanner = mCT()
    compression = Compression(scanner)
    proj = compression.get_projector(stir_domain=compression.get_stir_domain(zoom=1))
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

def test_simple_run():
    scanner = mCT()
    compression = Compression(scanner)
    proj = compression.get_projector()
    result = proj(proj.domain.one())

# TODO: test that loading from file or memory gives the same result.
