from stir import Scanner as _Scanner, Succeeded as _Succeeded
import numpy as np

class Scanner:

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
    average_depth_of_inter = 0

    max_num_non_arc_cor_bins = None
    default_non_arc_cor_bins = None

    # some less reasonable default values
    num_dets_per_ring = 512
    det_radius = 102
    ring_spacing = 1.35
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

        for (sa, pa, ty) in ACCESSOR_MAPPING:
            getattr(scanner, "set_"+sa)(ty(getattr(self, pa)))

        if _check_consistency(scanner):
            return scanner
        else:
            raise ValueError('Something is wrong in the scanner geometry.')

    @classmethod
    def from_stir_scanner(cls, stir_scanner):
        """
        Convert a STIR scanner to a Scanner object.
        """
        scanner = Scanner()
        for (sa, pa, ty) in ACCESSOR_MAPPING:
            setattr(scanner, pa, getattr(stir_scanner, "get_"+sa)())

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
    # if name not in SCANNER_NAMES:
        # raise ValueError("No default scanner of name {}".format(name))
    stir_scanner = _Scanner.get_scanner_from_name(name)
    return stir_scanner

def _check_consistency(_scanner):
    return _scanner.check_consistency() == _Succeeded(_Succeeded.yes)

def _get_scanner_names():
    all_names = _Scanner.list_all_names()
    names = [name_.split(',')[0].rstrip() for name_ in all_names.split('\n')[:-1]]
    return names

SCANNER_NAMES = _get_scanner_names()

# a mapping between STIR and Python accessors, as well as the corresponding type
ACCESSOR_MAPPING = [
    ("num_rings", "num_rings", np.int32),
    ("num_detectors_per_ring", "num_dets_per_ring", np.int32),
    ("default_bin_size", "voxel_size_xy", np.float32),
    ("default_num_arccorrected_bins", "default_non_arc_cor_bins", np.int32),
    ("intrinsic_azimuthal_tilt", "intrinsic_tilt", np.float32),
    ("inner_ring_radius", "det_radius", np.float32),
    ("ring_spacing", "ring_spacing", np.float32),
    ("average_depth_of_interaction", "average_depth_of_inter", np.float32),
    ("max_num_non_arccorrected_bins", "max_num_non_arc_cor_bins", np.int32),
    ("num_axial_blocks_per_bucket", "axials_blocks_per_bucket", np.int32),
    ("num_transaxial_blocks_per_bucket", "trans_blocks_per_bucket", np.int32),
    ("num_axial_crystals_per_block", "axial_crystals_per_block", np.int32),
    ("num_transaxial_crystals_per_block", "trans_crystals_per_block", np.int32),
    ("num_axial_crystals_per_singles_unit", "axial_crystals_per_singles_unit", np.int32),
    ("num_transaxial_crystals_per_singles_unit", "trans_crystals_per_singles_unit", np.int32),
    ("num_detector_layers", "num_detector_layers", np.int32),
]

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
