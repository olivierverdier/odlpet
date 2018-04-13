from os import path
import pytest
import odl
from odlpet.stir.io import volume_from_file, projector_from_file
from odlpet.stir.space import space_from_stir_domain
from odlpet.scanner.compression import get_range_from_proj_data
from odlpet.stir.bindings import ForwardProjectorByBinWrapper
import stir, stirextra

base = path.join(path.dirname(path.abspath(__file__)), path.pardir, 'examples', 'tomo', 'data', 'stir')


def test_load():
    volume_file = str(path.join(base, 'initial.hv'))
    vol = volume_from_file(volume_file)
    stir_vol = stir.FloatVoxelsOnCartesianGrid.read_from_file(volume_file)
    assert pytest.approx(vol.asarray(), stirextra.to_numpy(stir_vol))


def _projector_from_file(volume_file, projection_file):
    """Create a STIR projector from given template files.

    Old implementation, for test purposes only.
    """
    volume = stir.FloatVoxelsOnCartesianGrid.read_from_file(volume_file)
    recon_sp = space_from_stir_domain(volume)

    proj_data_in = stir.ProjData.read_from_file(projection_file)
    proj_data = stir.ProjDataInMemory(proj_data_in.get_exam_info(),
                                      proj_data_in.get_proj_data_info())


    data_sp = get_range_from_proj_data(proj_data)

    return ForwardProjectorByBinWrapper(recon_sp, data_sp, volume, proj_data)


def test_file_run():
    """
    Test that loading from file runs without errors.
    """
    # Load STIR input files with data

    volume_file = str(path.join(base, 'initial.hv'))
    projection_file = str(path.join(base, 'small.hs'))

    # Make STIR projector
    proj = projector_from_file(volume_file, projection_file)

    # Create Shepp-Logan phantom
    vol = odl.phantom.shepp_logan(proj.domain, modified=True)

    # Project and show
    result = proj(vol)

    proj_ = _projector_from_file(volume_file, projection_file)

    # check that both projection operators are the same
    assert proj.domain == proj_.domain
    assert proj.range.shape == proj_.range.shape
