from odlpet.scanner.scanner import mCT, Scanner
from odlpet.scanner.compression import Compression
from odlpet.scanner.sinogram import get_shape_from_proj_data
import stir
import pytest
import numpy as np

def test_domain():
    from odlpet.stir.space import space_from_stir_domain
    s = mCT()
    c = Compression(s)
    domain = c.get_stir_domain()
    space = space_from_stir_domain(domain)
    shape = space.shape
    smin, smax = space.min_pt, space.max_pt

    domain_z = c.get_stir_domain(zoom=2.)
    space_z = space_from_stir_domain(domain_z)
    assert pytest.approx(space_z.min_pt) == smin
    # assert pytest.approx(space_z.max_pt) == smax
    assert space_z.shape[0] == shape[0]
    for i in [1,2]:
        assert space_z.shape[i] // 2 == shape[i] - 1

    new_shape = (2,3,4)
    domain_s = c.get_stir_domain(sizes=new_shape)
    space_s = space_from_stir_domain(domain_s)
    assert space_s.shape == new_shape

    offset = [10.,30.,20.]
    domain_o = c.get_stir_domain(offset=offset)
    space_o = space_from_stir_domain(domain_o)
    assert space_o.shape == shape
    assert pytest.approx(space_o.min_pt - smin) == offset
    assert pytest.approx(space_o.max_pt - smax) == offset

from pathlib import Path

def test_data_codomain():
    """
    Test that a projector can be obtained from loaded data.
    """
    header_path = Path(__file__).parent / 'data' / 'small.hs'
    print(header_path)
    stir_data = stir.ProjData.read_from_file(header_path.as_posix())
    stir_data_info = stir_data.get_proj_data_info()
    comp = Compression.from_stir_proj_data_info(stir_data_info)
    proj = comp.get_projector(stir_proj_data_info=stir_data_info)
    # correct shape
    assert proj.range.shape == get_shape_from_proj_data(stir_data)

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

def test_domain_labels():
    c = Compression(Scanner())
    proj = c.get_projector()
    labels = proj.domain.axis_labels
    assert labels == ('z', 'y', 'x')

def test_default_scanner():
    c = Compression()
    c.num_of_views = 10
    c.num_non_arccor_bins = 11
    c.scanner.num_rings = 2
    proj = c.get_projector()


def test_double_adjoint():
    """
    The adjoint of the adjoint of the forward operator should be the adjoint.
    """
    c = Compression(Scanner())
    proj = c.get_projector()
    adjoint = proj.adjoint
    assert proj.adjoint.adjoint.domain.shape == proj.domain.shape
    assert proj.adjoint.adjoint.range.shape == proj.range.shape

