import stir, stirextra
from ..scanner.compression import Compression
from .space import space_from_stir_domain


def stir_domain_from_file(volume_file):
    return stir.FloatVoxelsOnCartesianGrid.read_from_file(volume_file)

def volume_from_voxels(_voxels):
    space = space_from_stir_domain(_voxels)
    arr = stirextra.to_numpy(_voxels)
    element = space.element(arr)
    return element

def volume_from_file(volume_file):
    return volume_from_voxels(stir_domain_from_file(volume_file))

def space_from_file(volume_file):
    _voxels = stir_domain_from_file(volume_file)
    return space_from_stir_domain(_voxels)

def projector_from_file(volume_file, projection_file):
    """
    Convenience function to create a projector from a volume and projection
    header files.
    """
    stir_domain = stir_domain_from_file(volume_file)
    proj_data = stir.ProjData.read_from_file(projection_file)
    proj_data_info = proj_data.get_proj_data_info()
    comp = Compression.from_stir_proj_data_info(proj_data_info)
    proj = comp.get_projector(stir_domain=stir_domain,
                       stir_proj_data_info=proj_data_info)
    return proj


