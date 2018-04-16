from stir import Scanner as _Scanner, Succeeded as _Succeeded
import numpy as np

class Scanner():

    # some reasonable default values
    num_rings = 1
    intrinsic_tilt = 0.
    num_detector_layers = 1
    trans_blocks_per_bucket = 0
    axials_blocks_per_bucket = 0
    trans_crystals_per_block = 0
    axial_crystals_per_block = 0
    trans_crystals_per_singles_unit = -1
    axial_crystals_per_singles_unit = -1

    max_num_non_arc_cor_bins = None
    default_non_arc_cor_bins = None

    # some less reasonable default values
    num_dets_per_ring = 512
    det_radius = 102
    ring_spacing = 1.35
    average_depth_of_inter = .7
    voxel_size_xy = 0.3

    def get_stir_scanner(self):
        """
        Return a STIR scanner object corresponding to this object.
        """

        # TODO: should be moved to proper accessor methods
        if self.max_num_non_arc_cor_bins is None:
            # Roughly speaking number of detectors on the diameter
            # bin_size = (self.det_radius*2) / (self.num_dets_per_ring/2)
            self.max_num_non_arc_cor_bins = int(self.num_dets_per_ring/2)

        if self.default_non_arc_cor_bins is None:
            self.default_non_arc_cor_bins = self.max_num_non_arc_cor_bins

        scanner = _get_stir_scanner_by_name('Userdefined')

        scanner.set_num_rings(np.int32(self.num_rings))
        scanner.set_num_detectors_per_ring(np.int32(self.num_dets_per_ring))
        scanner.set_default_bin_size(np.float32(self.voxel_size_xy))
        scanner.set_default_num_arccorrected_bins(np.int32(self.default_non_arc_cor_bins))
        scanner.set_default_intrinsic_tilt(np.float32(self.intrinsic_tilt))
        scanner.set_inner_ring_radius(np.float32(self.det_radius))
        scanner.set_ring_spacing(np.float32(self.ring_spacing))
        scanner.set_average_depth_of_interaction(np.float32(self.average_depth_of_inter))
        scanner.set_max_num_non_arccorrected_bins(np.int32(self.max_num_non_arc_cor_bins))
        scanner.set_num_axial_blocks_per_bucket(np.int32(self.axials_blocks_per_bucket))
        scanner.set_num_transaxial_blocks_per_bucket(np.int32(self.trans_blocks_per_bucket))
        scanner.set_num_axial_crystals_per_block(np.int32(self.axial_crystals_per_block))
        scanner.set_num_transaxial_crystals_per_block(np.int32(self.trans_crystals_per_block))
        scanner.set_num_axial_crystals_per_singles_unit(np.int32(self.axial_crystals_per_singles_unit))
        scanner.set_num_transaxial_crystals_per_singles_unit(np.int32(self.trans_crystals_per_singles_unit))
        scanner.set_num_detector_layers(np.int32(self.num_detector_layers))

        if _check_consistency(scanner):
            return scanner
        else:
            raise TypeError('Something is wrong in the scanner geometry.')

    @classmethod
    def from_stir_scanner(cls, stir_scanner):
        """
        Convert a STIR scanner to a Scanner object.
        """
        scanner = Scanner()
        scanner.num_rings = stir_scanner.get_num_rings()
        scanner.num_dets_per_ring = stir_scanner.get_num_detectors_per_ring()
        scanner.voxel_size_xy = stir_scanner.get_default_bin_size()
        scanner.default_non_arc_cor_bins = stir_scanner.get_default_num_arccorrected_bins()
        scanner.intrinsic_tilt = stir_scanner.get_default_intrinsic_tilt()
        scanner.det_radius = stir_scanner.get_inner_ring_radius()
        scanner.ring_spacing = stir_scanner.get_ring_spacing()
        scanner.average_depth_of_inter = stir_scanner.get_average_depth_of_interaction()
        scanner.max_num_non_arc_cor_bins = stir_scanner.get_max_num_non_arccorrected_bins()
        scanner.axials_blocks_per_bucket = stir_scanner.get_num_axial_blocks_per_bucket()
        scanner.trans_blocks_per_bucket = stir_scanner.get_num_transaxial_blocks_per_bucket()
        scanner.axial_crystals_per_block = stir_scanner.get_num_axial_crystals_per_block()
        scanner.trans_crystals_per_block = stir_scanner.get_num_transaxial_crystals_per_block()
        scanner.axial_crystals_per_singles_unit = stir_scanner.get_num_axial_crystals_per_singles_unit()
        scanner.trans_crystals_per_singles_unit = stir_scanner.get_num_transaxial_crystals_per_singles_unit()
        scanner.num_detector_layers = stir_scanner.get_num_detector_layers()
        return scanner




    @classmethod
    def from_name(cls, name):
        """
        Return a Scanner object from a named Scanner.
        """
        return cls.from_stir_scanner(_get_stir_scanner_by_name(name))


def _get_stir_scanner_by_name(name):
    """
    Get a STIR scanner by name.
    """
    if name not in SCANNER_NAMES:
        raise ValueError("No default scanner of name {}".format(name))
    stir_scanner = _Scanner.get_scanner_from_name(name)
    return stir_scanner

def _check_consistency(_scanner):
    return _scanner.check_consistency() == _Succeeded(_Succeeded.yes)

def _get_scanner_names():
    all_names = _Scanner.list_all_names()
    names = [name_.split(',')[0].rstrip() for name_ in all_names.split('\n')[:-1]]
    return names

SCANNER_NAMES = _get_scanner_names()

class mCT(Scanner):
    # Detector x size in mm - plus the ring difference
    det_nx_mm = 6.25
    # Detector y size in mm - plus the ring difference
    det_ny_mm = 6.25
    # Total number of rings
    num_rings = 8
    # Total number of detectors per ring
    num_dets_per_ring = 112
    # Inner radius of the scanner (crystal surface)
    det_radius = 57.5 # in mm

    #
    # Additional things that STIR would like to know
    #
    average_depth_of_inter = 7.0 # in mm
    ring_spacing = det_ny_mm
    voxel_size_xy = 1.65 # in mm
    axial_crystals_per_block = 8
    trans_crystals_per_block = 7
    axials_blocks_per_bucket = 1
    trans_blocks_per_bucket = 16
    axial_crystals_per_singles_unit = 8
    trans_crystals_per_singles_unit = 0
    num_detector_layers = 1
    intrinsic_tilt = 0.0
