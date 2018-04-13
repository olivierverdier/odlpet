from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression
import odlpet.scanner.scanner as scan
import stir
import pytest
import numpy as np

def test_domain():
    # TODO: add a real test
    s = mCT()
    c = Compression(s)
    domain = c.get_stir_domain()
    domain = c.get_stir_domain(1.)
    domain = c.get_stir_domain(sizes=[2,3,4])
    domain = c.get_stir_domain(offset=[2.,3.,1])

from pathlib import Path

def test_data_codomain():
    """
    Test that a projector can be obtained from loaded data.
    """
    header_path = Path(__file__).parent / 'data' / 'small.hs'
    print(header_path)
    proj_data_in = stir.ProjData.read_from_file(header_path.as_posix())
    stir_data = stir.ProjDataInMemory(proj_data_in.get_exam_info(),
                                      proj_data_in.get_proj_data_info())
    stir_data_info = stir_data.get_proj_data_info()
    stir_scanner = stir_data_info.get_scanner()
    scanner = scan.Scanner.from_stir_scanner(stir_scanner)
    comp = Compression(scanner)
    proj = comp.get_projector(stir_proj_data_info=stir_data_info)
    # correct shape
    assert proj.range.shape == stir_data.to_array().shape()
    # simple check that the projector actually computes something:
    dummy_data = proj(proj.domain.zero())
    assert pytest.approx(dummy_data.asarray()) == proj.range.zero().asarray()


def test_resolution_type():
    """
    Compresion defines a default resolution, check that the types are integers.
    """
    compression = Compression(mCT())
    assert isinstance(compression.num_non_arccor_bins, int)
    assert isinstance(compression.num_of_views, int)

def test_sinogram_resolution():
    """
    Possible to specify a sinogram resolution.
    """
    c = Compression(mCT())
    nb_tans = np.random.randint(1,10)
    c.num_non_arccor_bins = nb_tans
    nb_views = np.random.randint(1,10)
    c.num_of_views = nb_views
    proj = c.get_projector()
    resolution = proj.range.shape[-2:]
    assert resolution == (nb_views, nb_tans)


