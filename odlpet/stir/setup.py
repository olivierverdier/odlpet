
import odl

import numpy as np

from odl.discr.lp_discr import DiscreteLp, DiscreteLpElement
from odl.tomo.geometry import Flat2dDetector
from odl.tomo.util.utility import perpendicular_vector

import stir
import stirextra


#
#
# INTERFACE FUNCTIONS FROM ODL TO STIR
#

def stir_get_discretized_image_from_Cartesian_voxels(_voxels):

    # Number of voxels
    # This function returns [ x, y, z]
    # range_size = stir.Int3BasicCoordinate()
    # range_size[3] = np.int32(im_dim[0])  #: x
    # range_size[2] = np.int32(im_dim[1])  #: y
    # range_size[1] = np.int32(im_dim[2])  #: z

    ind_range = _voxels.get_index_range()

    # Voxel size
    # This function returns [ x, y, z]
    # voxel_size = stir.Float3BasicCoordinate()
    # voxel_size[3] = np.float32(vox_size[0])  #: z
    # voxel_size[2] = np.float32(vox_size[1])  #: y
    # voxel_size[1] = np.float32(vox_size[2])  #: x

    # Shift initial point relatively to 0,0,0
    # This function returns [ x, y, z]
    im_origin = stir.FloatCartesianCoordinate3D()
    im_origin[3] = np.float32(0.0)
    im_origin[2] = np.float32(0.0)
    im_origin[1] = np.float32(0.0)

    dic = stir.Float3DDiscretisedDensityOnCartesianGrid(ind_range,im_origin)
    dic.set_index_range(ind_range)
    dic.set_origin(im_origin)

    # domain = stir.FloatVoxelsOnCartesianGrid(ind_range, im_origin, voxel_size)
    dic.fill(np.float32(0.0))

    nx = dic.get_x_size()
    ny = dic.get_y_size()
    nz = dic.get_z_size()

    min_ind = dic.get_min_indices()
    max_ind = dic.get_max_indices()
    leng = dic.get_lengths()

    ori = dic.get_origin()
    minPH = dic.get_physical_coordinates_for_indices(dic.get_min_indices())
    maxPH = dic.get_physical_coordinates_for_indices(dic.get_max_indices())

    return dic

def stir_get_ODL_domain_which_honours_STIR_restrictions(_vox_num, _vox_size):
    """
    In the future a geometry should be imported to handle scanner alignment restrictions.
    Returns
    -------

    . warning: The resulted object will just be in accordance to the restrictions STIR opposes. The orientation
        of the axis is going to be as in ODL.
    .. warning:: STIR coordinates are currently related to the scanner, i.e. not to the patient (as in DICOM).
        For an image with zero offset, the origin is assumed to coincide with the centre of the first plane.
        I strongly suggest for the time being to let the origin default to (0,0,0) as STIR regards it.

    """

    range = [a*b for a,b in zip(_vox_num,_vox_size)]
    min_p = [-x / 2 for x in range]
    max_p = [a+b for a,b in zip(min_p,range)]

    min_p[2] = 0.0
    max_p[2] = range[2]

    return odl.uniform_discr(
            min_pt=min_p, max_pt=max_p, shape= _vox_num,
            dtype='float32')









def stir_get_STIR_domain_from_ODL(_discreteLP, _fill_value=0.0):
    """
    Interface function to get a STIR domain without caring about the classes names.

    Parameters
    ----------
    _discreteLP

    Returns
    -------

    """

    return create_empty_VoxelsOnCartesianGrid_from_DiscreteLP(_discreteLP, _fill_value)






def stir_get_ODL_domain_from_STIR(_voxels):
    """
    Interface function to get an ODL domain without caring about the classes names.

    Parameters
    ----------
    _voxelsF

    Returns
    -------

    """
    return create_DiscreteLP_from_STIR_VoxelsOnCartesianGrid(_voxels)

def stir_get_STIR_image_from_ODL_Vector(_domain, _data):
    """
    This function can be used to get a STIR phantom (emmition or attenuation
    data) from an ODL vector.

    Parameters
    ----------
    _data

    Returns
    -------

    """
    if not isinstance( _domain, DiscreteLp):
            raise TypeError('An ODL DiscreteLP is required as first input')

    if not isinstance( _data, DiscreteLpElement):
            raise TypeError('An ODL DiscreteLPVector is required as second input')

    stir_image = stir_get_STIR_domain_from_ODL(_domain)

    stir_operate_STIR_and_ODL_vectors(stir_image, _data, '+')

    return stir_image


def stir_operate_STIR_and_ODL_vectors(_stir_data, _odl_data, _operator):
    """
    This function can perform some simple operations, Only addition and
    multiplication are currently available.

    Parameters
    ----------
    _stir_data
    _odl_data
    _operator

    Returns
    -------

    """
    if not isinstance( _odl_data, DiscreteLpElement) or not isinstance( _stir_data, stir.FloatVoxelsOnCartesianGrid):
            raise TypeError('The first input should be the STIR data'
                            'and the second value should be ODL Vector')

    stir_min_ind = _stir_data.get_min_indices()
    stir_max_ind = _stir_data.get_max_indices()

    odl_array = _odl_data.asarray().astype(np.float32)
    trans_phantom_array = stir_transform_array_to_STIR_orientation(odl_array)

    odl_max_ind = trans_phantom_array.shape


    stir_array = stirextra.to_numpy(_stir_data)

    if _operator is '+':
        res = np.add(stir_array, trans_phantom_array)
    elif _operator is '*':
        res = np.multiply(stir_array, trans_phantom_array)

    _stir_data.fill(res.flat)


def stir_get_STIR_data_as_array(_stir_data):
    """
    A wrapper to the stir.extra function
    Parameters
    ----------
    _stir_data

    Returns
    -------

    """
    return stirextra.to_numpy(_stir_data)


def stir_unified_display_function(_display_me, _in_this_grid, _title=""):
    """
    This is a helper function. STIR, ODL and NumPy used different functions to display images.
    I created this function, in order to avoid flips and rotates.
    It which calls odl.utils.graphics.show_discrete_data.

    Parameters
    ----------
    _display_me: A NumPy array.

    _in_this_grid: A suitable grid

    _title: A title for the figure

    Returns
    -------
    A matplotlib.pyplot figure
    """

    import matplotlib.pyplot as plt

    from odl.util.graphics import show_discrete_data

    grid = get_2D_grid_from_domain(_in_this_grid)

    fig = plt.figure()
    show_discrete_data(_display_me, grid, fig = fig)
    fig.canvas.set_window_title(_title)

#
#
# FUNCTIONS FROM STIR TO ODL
#

#
#
# TRANSFORM FUNCTIONS
#

def stir_transform_array_to_STIR_orientation(_this):
    """
    This is transformation function. The input is a numpy array from a DiscreteLPVector and returns
    an array which can be used to fill a STIR image and maintain structure.
    Parameters
    ----------
    _this: A numpy array,a DiscreteLP or a DiscreteLPVector

    Returns
    -------
    A NumPy array compatible to STIR

    . warning: Right now only transformation of numpy arrays is supported.

    """

    if isinstance( _this, np.ndarray):
        _this_array = np.rot90(_this,-1)
        _this_array = np.fliplr(_this)
        # STIR indices are [z, y, x]
        _this_array = np.swapaxes(_this,0,2)

        # I have to copy in order to transform the actual data
        return _this_array.copy()
    elif isinstance(_this, DiscreteLp):
        # Currently I don't know how to transform so
        # we can return a new object with the correct orientation
        # TODO: This is half implemented
        im_dim, vox_size, vol_min, vol_max = get_volume_geometry(_data)



        odl.uniform_discr(
            min_corner=vol_min, max_corner=vol_max, nsamples=vox_num,
            dtype='float32')
    elif isinstance(_this, DiscreteLpElement):
        # TODO: Implement it in the near future.
        pass
    else:
        raise ValueError('Unsupported input object')



def stir_transform_array_to_STIR_orientation_reverse(_this_array):
    # _this_array = np.rot90(_this_array,-1)
    # _this_array = np.fliplr(_this_array)
    # # STIR indices are [z, y, x]
    # _this_array = np.swapaxes(_this_array,0,2)
    #
    # # I have to copy in order to transform the actual data
    # return _this_array.copy()

    pass


#
#
# HELPERS
#

def get_volume_geometry(discr_reco):
    """
    This is a helper function which returns the total size and voxel number of a
    discretised object.

    Parameters
    ----------
    discr_reco: A discretised ODL object

    Returns
    -------

    """
    vol_shp = discr_reco.partition.shape
    voxel_size = discr_reco.cell_sides

    min_point = discr_reco.partition.min_pt
    max_point = discr_reco.partition.max_pt

    return np.asarray(vol_shp, dtype=np.int32), np.asarray(voxel_size, dtype=np.float32), np.asarray(min_point, dtype=np.float32), np.asarray(max_point, dtype=np.float32)



def create_empty_VoxelsOnCartesianGrid_from_DiscreteLP(_discr, _fill_value = 0.0):
    """
    This class defines multi-dimensional (numeric) arrays.
    This class implements multi-dimensional arrays which can have 'irregular' ranges.
    See IndexRange for a description of the ranges. Normal numeric operations are defined.
    In addition, two types of iterators are defined, one which iterators through the outer index,
    and one which iterates through all elements of the array.

    Array inherits its numeric operators from NumericVectorWithOffset.
    In particular this means that operator+= etc. potentially grow the object.
    However, as grow() is a virtual function,
    Array::grow is called, which initialises new elements first to 0.

    Parameters
    ----------
    _discr

    Returns
    -------
        A stir.FloatVoxelsOnCartesianGrid object of the aforementioned dimensions, filled with zeros
    """

    # dump1&2 are not going to be used from this function.
    im_dim, vox_size, dump1, dump2 = get_volume_geometry(_discr)

    # Number of voxels
    # This function returns [ x, y, z]
    min_indices = stir.Int3BasicCoordinate()

    min_indices[3] = np.int32(-im_dim[0]/2) #: x
    min_indices[2] = np.int32(-im_dim[1]/2) #: y
    min_indices[1] = np.int32(0) #: z

    # ind_range = stir.IndexRange3D(range_size)

    max_indices =  stir.Int3BasicCoordinate()

    max_indices[3] = min_indices[3] + np.int32(im_dim[0]) -1 #: x
    max_indices[2] = min_indices[2] + np.int32(im_dim[1]) -1 #: y
    max_indices[1] = min_indices[1] + np.int32(im_dim[2]) -1 #: z

    # This function returns [ x, y, z]
    voxel_size = stir.Float3BasicCoordinate()
    voxel_size[3] = np.float32(vox_size[0]) #: z
    voxel_size[2] = np.float32(vox_size[1]) #: y
    voxel_size[1] = np.float32(vox_size[2]) #: x


    # Shift initial point relatively to 0,0,0
    # This function returns [ x, y, z]
    im_origin = stir.FloatCartesianCoordinate3D()
    im_origin[3] = np.float32(0.0)
    im_origin[2] = np.float32(0.0)
    im_origin[1] = np.float32(0.0)

    first_pixel_offset_x = vox_size[0] * min_indices[3]
    first_pixel_offset_y = vox_size[1] * min_indices[2]
    first_pixel_offset_z = vox_size[2] * min_indices[1]

    im_origin[3] = first_pixel_offset_x - vox_size[0] * min_indices[3]
    im_origin[2] = first_pixel_offset_y - vox_size[0] * min_indices[2]
    im_origin[1] = first_pixel_offset_z - vox_size[0] * min_indices[1]

    range = stir.IndexRange3D(min_indices, max_indices)

    domain = stir.FloatVoxelsOnCartesianGrid( range , im_origin, voxel_size)
    domain.fill(np.float32(_fill_value))

    nx = domain.get_x_size()
    ny = domain.get_y_size()
    nz = domain.get_z_size()

    min_ind = domain.get_min_indices()
    max_ind = domain.get_max_indices()
    leng = domain.get_lengths()

    ori = domain.get_origin()
    minPH = domain.get_physical_coordinates_for_indices(domain.get_min_indices())
    maxPH = domain.get_physical_coordinates_for_indices(domain.get_max_indices())

    return domain

def space_from_voxels_origin(volume):
    """
    Original function inside bindings.
    This assumes that the min point is at the origin.
    """
    origin = volume.get_origin()
    grid_spacing = volume.get_grid_spacing()
    grid_shape = [volume.get_z_size(),
                  volume.get_y_size(),
                  volume.get_x_size()]
    min_pt = [origin[1], origin[2], origin[3]]
    max_pt = [origin[1] + grid_spacing[1] * grid_shape[0],
              origin[2] + grid_spacing[2] * grid_shape[1],
              origin[3] + grid_spacing[3] * grid_shape[2]]

    # reverse to handle STIR bug? See:
    # https://github.com/UCL/STIR/issues/7
    recon_sp = odl.uniform_discr(min_pt, max_pt, grid_shape,
                             dtype='float32')
    return recon_sp

def create_DiscreteLP_from_STIR_VoxelsOnCartesianGrid(_voxels):
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


def get_2D_grid_from_domain(_this_domain):
    """

    Parameters
    ----------
    _this_domain

    Returns
    -------

    """
    return  odl.uniform_grid([_this_domain.space.partition.min_pt[0], _this_domain.space.partition.min_pt[1]],
                        [_this_domain.space.partition.max_pt[0], _this_domain.space.partition.max_pt[1]], (2, 3))



