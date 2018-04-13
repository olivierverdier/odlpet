from odl.discr import uniform_discr

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

    return uniform_discr(
            min_pt=vol_min, max_pt=vol_max, shape=vox_num,
            dtype='float32')
