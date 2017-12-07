
from odlpet.stir.setup import (
    stir_get_projection_data,
    stir_get_projection_data_info,
)

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

    def get_stir_proj_data_info(self, stir_domain):
        proj_info = stir_get_projection_data_info(
            self.scanner.get_stir_scanner(),
            self.span_num,
            self.max_num_segments,
            self.num_of_views,
            self.num_non_arccor_bins,
            self.data_arc_corrected,
            stir_domain)
        return proj_info

    def get_stir_proj_data(self, stir_domain, initialize_to_zero=True):
        proj_data = stir_get_projection_data(self.get_stir_proj_data_info(stir_domain), initialize_to_zero)
        return proj_data
