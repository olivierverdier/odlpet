"""Example PET reconstruction using STIR.

This example computes projections from the ODL Shepp-Logan phantom
and uses them as input data for reconstruction in STIR. Definition
of the acquisition geometry and computations are done entirely in STIR,
where the communication between ODL and STIR is realized with files
via hard disk.

Note that running this example requires an installation of
`STIR <http://stir.sourceforge.net/>`_ and its Python bindings.
"""

from odl.tomo.backends.stir_setup import (
    stir_get_ODL_domain_which_honours_STIR_restrictions,
    stir_get_STIR_domain_from_ODL,
    stir_get_STIR_geometry,
    stir_get_projection_data_info,
    stir_get_projection_data,
    stir_get_ODL_domain_from_STIR)
from odl.tomo.backends.stir_bindings import stir_projector_from_memory

# Temporal edit to account for the stuff.


# N.E. Replace the call to this function by creating a new ODL space and
# transform it to STIR domain.
#
# New ODL domain
# N.E. At a later point we are going to define a scanner with ring spacing 4.16
# therefore the z voxel size must be a divisor of that size.
discr_dom_odl = stir_get_ODL_domain_which_honours_STIR_restrictions([64, 64, 15], [2.05941, 2.05941, 3.125])

stir_domain = stir_get_STIR_domain_from_ODL(discr_dom_odl, 0.0)

# Instead of calling a hs file we are going to initialise a projector, based on a scanner,

#
# This would correspond to the mCT scanner
#
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

# Create a PET geometry (ODL object) which is similar
# to the one that STIR will create using these values
# geom = odl.tomo.stir_get_ODL_geometry_which_honours_STIR_restrictions(det_nx_mm, det_ny_mm,
#                                                                       num_rings, num_dets_per_ring,
#                                                                       det_radius)

# Now create the STIR geometry
stir_scanner = stir_get_STIR_geometry(num_rings, num_dets_per_ring,
                                               det_radius, ring_spacing,
                                               average_depth_of_inter,
                                               voxel_size_xy,
                                               axial_crystals_per_block, trans_crystals_per_block,
                                               axials_blocks_per_bucket, trans_blocks_per_bucket,
                                               axial_crystals_per_singles_unit, trans_crystals_per_singles_unit,
                                               num_detector_layers, intrinsic_tilt)



# Parameters usefull to the projector setup

# Axial compression (Span)
# Reduction of the number of sinograms at different ring dierences
# as shown in STIR glossary.
# Span is a number used by CTI to say how much axial
# compression has been used.  It is always an odd number.
# Higher span, more axial compression.  Span 1 means no axial
# compression.
span_num = 1

# The segment is an index of the ring difference.
# In 2D PET there is only one segment = 0
# In 3D PET segment = 0 refers to direct sinograms
# The maximum number of segment can be 2*NUM_RINGS - 1
# Setting the followin variable to -1 implies : maximum possible
max_num_segments = 3

# If the views is less than half the number of detectors defined in
#  the Scanner then we subsample the scanner angular positions.
# If it is larger we are going to have empty cells in the sinogram
num_of_views = num_dets_per_ring / 2

# The number of tangestial positions refers to the last sinogram
# coordinate which is going to be the LOS's distance from the center
# of the FOV. Normally this would be the number of default_non_arc_bins
num_non_arccor_bins = num_dets_per_ring / 2

# A boolean if the data have been arccorrected during acquisition
# or in preprocessing. Anyways, STIR will not do that for you, but needs
# to know.
data_arc_corrected = False


# Now lets create the proper projector info
proj_info = stir_get_projection_data_info(stir_scanner, span_num,
                                                   max_num_segments, num_of_views,
                                                   num_non_arccor_bins, data_arc_corrected,
                                                   stir_domain)

#
# Now lets create the projector data space (range)
# or any empty sinogram
#
initialize_to_zero = True
proj_data = stir_get_projection_data(proj_info, initialize_to_zero)

#
# Let's do something with all this stuff.
#
#

#
# I don't enough time to develope all the transformations, therefore I define the
# dummies discr_dom and phantom which are ODL objects oriented as STIR need them to be.
#
#

# A DiscreteLP domain which has the STIR orientation
dummy_discr_dom_odl = stir_get_ODL_domain_from_STIR(stir_domain)


# Initialize the forward projector
proj = stir_projector_from_memory(dummy_discr_dom_odl,
                                                                  stir_domain,
                                                                  proj_data,
                                                                  proj_info)


# Create Shepp-Logan phantom
from odl.phantom import shepp_logan

# odl_phantom = shepp_logan(discr_dom_odl, modified=True)
vol = shepp_logan(proj.domain, modified=True)

# Project data. Note that this delegates computations to STIR.
projections = proj(vol)

# Reconstruct using the STIR forward projector in the ODL reconstruction scheme

from odl.solvers import landweber

# Calculate operator norm required for Landweber's method
op_norm_est_squared = proj.adjoint(projections).norm() / vol.norm()
omega = 0.5 / op_norm_est_squared

recon = proj.domain.zero()
landweber(proj, recon, projections, niter=50, omega=omega)
recon.show()
