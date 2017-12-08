import stir
import numpy as np

def stir_get_STIR_geometry(_num_rings, _num_dets_per_ring,
                           _det_radius, _ring_spacing,
                           _average_depth_of_inter,
                           _voxel_size_xy,
                           _axial_crystals_per_block = 1, _trans_crystals_per_block= 1,
                           _axials_blocks_per_bucket = 1, _trans_blocks_per_bucket = 1,
                           _axial_crystals_per_singles_unit = 1, _trans_crystals_per_singles_unit = 1,
                           _num_detector_layers = 1, _intrinsic_tilt = 0):

    # Roughly speaking number of detectors on the diameter
    # bin_size = (_det_radius*2) / (_num_dets_per_ring/2)
    max_num_non_arc_cor_bins = int(_num_dets_per_ring/2)

    # TODO: use "Userdefined" instead? (should not change much)
    scanner = stir.Scanner.get_scanner_from_name('')

    scanner.set_num_rings(np.int32(_num_rings))
    scanner.set_num_detectors_per_ring(np.int32(_num_dets_per_ring))
    scanner.set_default_bin_size(np.float32(_voxel_size_xy))
    scanner.set_default_num_arccorrected_bins(np.int32(max_num_non_arc_cor_bins))
    scanner.set_default_intrinsic_tilt(np.float32(_intrinsic_tilt))
    scanner.set_inner_ring_radius(np.float32(_det_radius))
    scanner.set_ring_spacing(np.float32(_ring_spacing))
    scanner.set_average_depth_of_interaction(np.float32(_average_depth_of_inter))
    scanner.set_max_num_non_arccorrected_bins(np.int32(max_num_non_arc_cor_bins))
    scanner.set_num_axial_blocks_per_bucket(np.int32(_axials_blocks_per_bucket))
    scanner.set_num_transaxial_blocks_per_bucket(np.int32(_trans_blocks_per_bucket))
    scanner.set_num_axial_crystals_per_block(np.int32(_axial_crystals_per_block))
    scanner.set_num_transaxial_crystals_per_block(np.int32(_trans_crystals_per_block))
    scanner.set_num_axial_crystals_per_singles_unit(np.int32(_axial_crystals_per_singles_unit))
    scanner.set_num_transaxial_crystals_per_singles_unit(np.int32(_trans_crystals_per_singles_unit))
    scanner.set_num_detector_layers(np.int32(_num_detector_layers))

    if scanner.check_consistency():
        return scanner
    else:
        raise TypeError('Something is wrong in the scanner geometry.')


class Scanner():

    def get_stir_scanner(self):

        # Now create the STIR geometry
        stir_scanner = stir_get_STIR_geometry(
            self.num_rings,
            self.num_dets_per_ring,
            self.det_radius,
            self.ring_spacing,
            self.average_depth_of_inter,
            self.voxel_size_xy,
            self.axial_crystals_per_block,
            self.trans_crystals_per_block,
            self.axials_blocks_per_bucket,
            self.trans_blocks_per_bucket,
            self.axial_crystals_per_singles_unit,
            self.trans_crystals_per_singles_unit,
            self.num_detector_layers,
            self.intrinsic_tilt)

        return stir_scanner

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
