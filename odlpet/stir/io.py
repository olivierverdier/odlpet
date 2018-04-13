import stir, stirextra
import odl

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

def space_from_stir_domain(_voxels):
    """
    This function tries to transform the VoxelsOnCartesianGrid to
    DicreteLP.

    Parameters
    ----------
    _voxels: A VoxelsOnCartesianGrid Object

    Returns
    -------
    An ODL DiscreteLP object with characteristics of the VoxelsOnCartesianGrid
    """

    stir_vox_max = _voxels.get_max_indices()
    stir_vox_min = _voxels.get_min_indices()
    vox_num = [stir_vox_max[1] - stir_vox_min[1] +1,
               stir_vox_max[2] - stir_vox_min[2] +1,
               stir_vox_max[3] - stir_vox_min[3] +1]

    stir_vol_max = _voxels.get_physical_coordinates_for_indices(_voxels.get_max_indices())
    stir_vol_min = _voxels.get_physical_coordinates_for_indices(_voxels.get_min_indices())

    stir_vox_size = _voxels.get_voxel_size()

    vol_max = [stir_vol_max[1]+stir_vox_size[1], stir_vol_max[2]+stir_vox_size[2],stir_vol_max[3]+stir_vox_size[3]]
    vol_min = [stir_vol_min[1], stir_vol_min[2],stir_vol_min[3]]

    return odl.uniform_discr(
            min_pt=vol_min, max_pt=vol_max, shape=vox_num,
            dtype='float32')

def projector_from_file(volume_file, projection_file):
    """
    Convenience function to create a projector from a volume and projection
    header files.
    """
    from ..scanner.scanner import _scanner_from_stir
    from ..scanner.compression import Compression
    stir_domain = stir_domain_from_file(volume_file)
    proj_data = stir.ProjData.read_from_file(projection_file)
    proj_data_info = proj_data.get_proj_data_info()
    scanner = _scanner_from_stir(proj_data_info.get_scanner())
    comp = Compression(scanner)
    proj = comp.get_projector(stir_domain=stir_domain,
                       stir_proj_data_info=proj_data_info)
    return proj


