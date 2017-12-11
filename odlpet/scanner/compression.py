import stir
import numpy as np
from odl.discr import uniform_discr
from ..stir.setup import create_DiscreteLP_from_STIR_VoxelsOnCartesianGrid
from ..stir.bindings import ForwardProjectorByBinWrapper

class Compression:
    def __init__(self, scanner):
        """
        Scanner: a pypet scanner.
        """
        self.scanner = scanner
        # Axial compression (Span)
        # Reduction of the number of sinograms at different ring dierences
        # as shown in STIR glossary.
        # Span is a number used by CTI to say how much axial
        # compression has been used.  It is always an odd number.
        # Higher span, more axial compression.  Span 1 means no axial
        # compression.
        self.span_num = 1

        # The segment is an index of the ring difference.
        # In 2D PET there is only one segment = 0
        # In 3D PET segment = 0 refers to direct sinograms
        # The maximum number of segment can be 2*NUM_RINGS - 1
        # Setting the followin variable to -1 implies : maximum possible
        # max_num_segments = 3
        self.max_num_segments = -1
        # max_num_segments = 2*scanner.num_rings - 1

        # If the views is less than half the number of detectors defined in
        #  the Scanner then we subsample the scanner angular positions.
        # If it is larger we are going to have empty cells in the sinogram
        self.num_of_views = scanner.num_dets_per_ring / 2

        # The number of tangestial positions refers to the last sinogram
        # coordinate which is going to be the LOS's distance from the center
        # of the FOV. Normally this would be the number of default_non_arc_bins
        self.num_non_arccor_bins = scanner.num_dets_per_ring / 2

        # A boolean if the data have been arccorrected during acquisition
        # or in preprocessing. Anyways, STIR will not do that for you, but needs
        # to know.
        self.data_arc_corrected = False

    def get_stir_proj_data_info(self):
        proj_info = stir_get_projection_data_info(
            self.scanner.get_stir_scanner(),
            self.span_num,
            self.max_num_segments,
            self.num_of_views,
            self.num_non_arccor_bins,
            self.data_arc_corrected)
        return proj_info

    def get_stir_proj_data(self, initialize_to_zero=True):
        proj_data = stir_get_projection_data(self.get_stir_proj_data_info(), initialize_to_zero)
        return proj_data

    def get_range(self):
        """
        Get an ODL codomain (range) from the projection data.
        """
        return get_range_from_proj_data(self.get_stir_proj_data())

    def get_domain(self, zoom=1., sizes=None, offset=None):
        """
        In the stir-wise way of reconstruction usually the projdata info creates a suitable domain
        When sizes.x() is -1, a default size in x is found by taking the diameter
        of the FOV spanned by the projection data. Similar for sizes.y().
        When sizes.z() is -1, a default size in z is found by taking the number of planes as

        $N_0$ when segment 0 is axially compressed,
        $2N_0-1$ when segment 0 is not axially compressed,

        where $N_0$ is the number of sinograms in segment 0.

        Actual index ranges start from 0 for z, but from -(x_size_used/2) for x (and similar for y).

        x,y grid spacing are set to the proj_data_info_ptr->get_scanner_ptr()->get_default_bin_size()/zoom.
        This is to make sure that the voxel size is independent on if arc-correction is used or not.
        If the default bin size is 0, the sampling distance in s (for bin 0) is used.

        z grid spacing is set to half the scanner ring distance.
        Parameters
        ----------
        _proj_info
        _size
        _offset

        Returns
        -------

        .warning :: Currently it doen't seem to be working. The z size is initialised but the x and y are not
        .todo :: File a bug report

        """
        if sizes is None:
            sizes = [-1,-1,-1]
        sizes_ = stir.IntCartesianCoordinate3D(*sizes)

        if offset is None:
            offset = [0.,0.,0.]
        offset_ = stir.FloatCartesianCoordinate3D(*offset)

        proj_info = self.get_stir_proj_data_info()

        return stir.FloatVoxelsOnCartesianGrid(proj_info, np.float32(zoom), offset_, sizes_)

    def get_sinogram_info(self):
        proj_info = self.get_stir_proj_data_info()
        segments = list(range(proj_info.get_min_segment_num(), proj_info.get_max_segment_num()+1))
        segment_sizes = [proj_info.get_max_axial_pos_num(s)+1 - proj_info.get_min_axial_pos_num(s) for s in segments]
        return list(zip(segments, segment_sizes))

    def get_offset(self, segment, axial):
        info = self.get_sinogram_info()
        from .sinogram import get_offset
        return get_offset(segment, axial, info)


    def get_projector(self, domain=None):
        if domain is None:
            domain = self.get_domain()

        recon_sp = create_DiscreteLP_from_STIR_VoxelsOnCartesianGrid(domain)

        return ForwardProjectorByBinWrapper(recon_sp, self.get_range(), domain, self.get_stir_proj_data())

def get_range_from_proj_data(proj_data):
    # TODO: set correct projection space. Currently, a default grid with
    # stride (1, 1, 1) is used.
    proj_shape = proj_data.to_array().shape()
    data_sp = uniform_discr([0, 0, 0], proj_shape, proj_shape, dtype='float32')
    return data_sp

def stir_get_projection_data_info(_stir_scanner, _span_num,
                                  _max_num_segments, _num_of_views,
                                  _num_non_arccor_bins, _data_arc_corrected):
    """
    ... more documentation needed ...
    Parameters
    ----------
    _stir_scanner
    _span_num
    _max_num_segments
    _num_of_views
    _num_non_arccor_bins
    _data_arc_corrected

    Returns
    -------

    """
    num_rings = _stir_scanner.get_num_rings()

    span_num = np.int32(_span_num)
    if _max_num_segments == -1:
        max_ring_diff = np.int32(num_rings -1)
    else:
        max_ring_diff = np.int32(_max_num_segments)

    num_of_views = np.int32(_num_of_views)
    if _data_arc_corrected:
        num_bins = np.int32(_stir_scanner.get_default_num_arccorrected_bins())
    else:
        num_bins = np.int32(_stir_scanner.get_max_num_non_arccorrected_bins())

    return stir.ProjDataInfo.ProjDataInfoCTI(_stir_scanner, span_num,
                                             max_ring_diff, num_of_views,
                                             num_bins, _data_arc_corrected)





def stir_get_projection_data(_projdata_info,
                             _zeros):
    """
    Initialize a ProjData object based on the ProjDataInfo
    Parameters
    ----------
    _projdata_info
    _zeros

    Returns
    -------

    """

    exam_info = get_examination_info()

    return stir.ProjDataInMemory(exam_info, _projdata_info, _zeros)

def get_examination_info():
    """
    Unless you do motion correction or list-mode reconstruction, default it to [0,1]
    And don't bother more.
    In think that a time frame [0, 1] - corresponds to one bed position
    in a generic way and STIR will ignore it,

    Parameters
    ----------
    _time_frame

    Returns
    -------

    """
    _time_frame = [0.0, 1.0]

    time_starts = np.array([_time_frame[0]], dtype=np.float64)
    time_ends = np.array([_time_frame[1]], dtype=np.float64)

    time_frame_def = stir.TimeFrameDefinitions(time_starts, time_ends)

    exam_info = stir.ExamInfo()
    exam_info.set_time_frame_definitions(time_frame_def)

    return exam_info

