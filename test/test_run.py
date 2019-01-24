from odlpet.stir.verbosity import StirVerbosity
from odlpet import Scanner, Compression

def test_memory_run():
    """
    Check that a simple setup runs without errors.
    """
    compression = Compression(Scanner())
    proj = compression.get_projector(stir_domain=compression.get_stir_domain(zoom=.1))
    with StirVerbosity(1):
        result = proj(proj.domain.one())

def test_simple_run():
    compression = Compression(Scanner())
    proj = compression.get_projector(stir_domain=compression.get_stir_domain(zoom=.1))
    result = proj(proj.domain.one())
