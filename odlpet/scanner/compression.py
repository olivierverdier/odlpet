import stir
import numpy as np
from ..stir.io import space_from_stir_domain
from ..stir.bindings import ForwardProjectorByBinWrapper
from .sinogram import get_offset, get_range_from_proj_data
from .scanner import Scanner

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
        self.max_num_segments = None
        # max_num_segments = 2*scanner.num_rings - 1

        # If the views is less than half the number of detectors defined in
        #  the Scanner then we subsample the scanner angular positions.
        # If it is larger we are going to have empty cells in the sinogram
        self.num_of_views = scanner.num_dets_per_ring // 2

        # The number of tangestial positions refers to the last sinogram
        # coordinate which is going to be the LOS's distance from the center
        # of the FOV. Normally this would be the number of default_non_arc_bins
        self.num_non_arccor_bins = scanner.num_dets_per_ring // 2

        # A boolean if the data have been arccorrected during acquisition
        # or in preprocessing. Anyways, STIR will not do that for you, but needs
        # to know.
        self.data_arc_corrected = False

    @classmethod
    def from_stir_proj_data_info(cls, proj_data_info):
        """
        Convenience method to obtain a compression object from projection data info.
        Note that the compression properties are still the default ones,
        not the ones corresponding to the projection data info.
        """
        scanner = Scanner.from_stir_scanner(proj_data_info.get_scanner())
        return cls(scanner)

    def get_stir_proj_data(self, stir_proj_data_info=None, initialize_to_zero=True):
        if stir_proj_data_info is None:
            stir_proj_data_info = self.get_stir_proj_data_info()
        exam_info = stir.ExamInfo()
        proj_data = stir.ProjDataInMemory(exam_info, stir_proj_data_info, initialize_to_zero)
        return proj_data

    def get_stir_domain(self, zoom=1., sizes=None, offset=None):
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

    def _get_sinogram_info(self):
        proj_info = self.get_stir_proj_data_info()
        segments = list(range(proj_info.get_min_segment_num(), proj_info.get_max_segment_num()+1))
        segment_sizes = [proj_info.get_max_axial_pos_num(s)+1 - proj_info.get_min_axial_pos_num(s) for s in segments]
        return list(zip(segments, segment_sizes))

    def get_offset(self, segment, axial):
        info = self._get_sinogram_info()
        return get_offset(segment, axial, info)


    def get_projector(self, stir_domain=None, stir_proj_data_info=None):
        if stir_domain is None:
            stir_domain = self.get_stir_domain()

        stir_proj_data = self.get_stir_proj_data(stir_proj_data_info)

        recon_sp = space_from_stir_domain(stir_domain)
        data_sp = get_range_from_proj_data(stir_proj_data, radius=self.scanner.det_radius)

        return ForwardProjectorByBinWrapper(recon_sp, data_sp, stir_domain, stir_proj_data)

    def get_default_num_tangential(self):
        if self.data_arc_corrected:
            num_bins = self.scanner.default_non_arc_cor_bins
        else:
            num_bins = self.scanner.max_num_non_arc_cor_bins
        return num_bins

    def get_num_tangential(self):
        if self.num_non_arccor_bins is None:
            result = self.get_default_num_tangential()
        else:
            result = self.num_non_arccor_bins
        return result

    def get_default_max_diff_ring(self):
        return self.scanner.num_rings - 1

    def get_max_ring_diff(self):
        # TODO: add this in initialisation method
        if self.max_num_segments is None:
            return self.get_default_max_diff_ring()
        else:
            return self.max_num_segments

    def get_stir_proj_data_info(self):
        _stir_scanner = self.scanner.get_stir_scanner()
        proj_data_info = stir.ProjDataInfo.ProjDataInfoCTI(
            _stir_scanner,
            self.span_num,
            self.get_max_ring_diff(),
            self.num_of_views,
            self.get_num_tangential(),
            self.data_arc_corrected)
        return proj_data_info



