from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

def test_domain():
    # TODO: add a real test
    s = mCT()
    c = Compression(s)
    domain = c.get_stir_domain()
    domain = c.get_stir_domain(1.)
    domain = c.get_stir_domain(sizes=[2,3,4])
    domain = c.get_stir_domain(offset=[2.,3.,1])
