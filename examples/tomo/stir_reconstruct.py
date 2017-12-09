"""Example PET reconstruction using STIR.

This example computes projections from the ODL Shepp-Logan phantom
and uses them as input data for reconstruction in STIR. Definition
of the acquisition geometry and computations are done entirely in STIR,
where the communication between ODL and STIR is realized with files
via hard disk.

Note that running this example requires an installation of
`STIR <http://stir.sourceforge.net/>`_ and its Python bindings.
"""

from odlpet.stir.setup import (
    stir_get_ODL_domain_which_honours_STIR_restrictions,
    stir_get_STIR_domain_from_ODL,
    stir_get_ODL_domain_from_STIR,
)
from odlpet.stir.bindings import stir_projector_from_memory, StirVerbosity
from odlpet.scanner.scanner import mCT
from odlpet.scanner.compression import Compression

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
scanner = mCT()

# Create a PET geometry (ODL object) which is similar
# to the one that STIR will create using these values
# geom = odl.tomo.stir_get_ODL_geometry_which_honours_STIR_restrictions(det_nx_mm, det_ny_mm,
#                                                                       num_rings, num_dets_per_ring,
#                                                                       det_radius)


compression = Compression(scanner)

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
proj = stir_projector_from_memory(dummy_discr_dom_odl, stir_domain, compression)


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

# recon = proj.domain.zero()
# landweber(proj, recon, projections, niter=50, omega=omega)
# recon.show()
