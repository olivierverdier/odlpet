from ..stir.setup import stir_get_STIR_geometry


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
