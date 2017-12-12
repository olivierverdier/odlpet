import stir, stirextra
from .setup import create_DiscreteLP_from_STIR_VoxelsOnCartesianGrid

def voxels_from_file(volume_file):
    return stir.FloatVoxelsOnCartesianGrid.read_from_file(volume_file)

def volume_from_voxels(_voxels):
    space = create_DiscreteLP_from_STIR_VoxelsOnCartesianGrid(_voxels)
    arr = stirextra.to_numpy(_voxels)
    element = space.element(arr)
    return element

def volume_from_file(volume_file):
    return volume_from_voxels(voxels_from_file(volume_file))

def space_from_file(volume_file):
    _voxels = voxels_from_file(volume_file)
    return create_DiscreteLP_from_STIR_VoxelsOnCartesianGrid(_voxels)
