from odlpet.stir.verbosity import StirVerbosity
from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

def test_memory_run():
    """
    Check that a simple setup runs without errors.
    """
    scanner = mCT()
    compression = Compression(scanner)
    proj = compression.get_projector(stir_domain=compression.get_stir_domain(zoom=.1))
    with StirVerbosity(1):
        result = proj(proj.domain.one())

def test_simple_run():
    scanner = mCT()
    compression = Compression(scanner)
    proj = compression.get_projector(stir_domain=compression.get_stir_domain(zoom=.1))
    result = proj(proj.domain.one())
