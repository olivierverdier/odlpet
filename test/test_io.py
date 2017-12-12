from os import path
import pytest
from odlpet.stir.io import volume_from_file
import stir, stirextra

base = path.join(path.dirname(path.abspath(__file__)), path.pardir, 'examples', 'tomo', 'data', 'stir')


def test_load():
    volume_file = str(path.join(base, 'initial.hv'))
    vol = volume_from_file(volume_file)
    stir_vol = stir.FloatVoxelsOnCartesianGrid.read_from_file(volume_file)
    assert pytest.approx(vol.asarray(), stirextra.to_numpy(stir_vol))
