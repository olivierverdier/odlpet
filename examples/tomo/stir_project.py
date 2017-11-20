"""Example for PET projection and back-projection using STIR.

This example computes projection data and the back-projection of that
data using the Shepp-Logan phantom in ODL as input. Definition
of the acquisition geometry and computations are done entirely in STIR,
where the communication between ODL and STIR is realized with files
via hard disk.

Note that running this example requires an installation of
`STIR <http://stir.sourceforge.net/>`_ and its Python bindings.
"""

from os import path
import stir
import odl

from odlpet.stir.bindings import stir_projector_from_file

# Load STIR input files with data
base = path.join(path.dirname(path.abspath(__file__)), 'data', 'stir')

volume_file = str(path.join(base, 'initial.hv'))
projection_file = str(path.join(base, 'small.hs'))

# Make STIR projector
proj = stir_projector_from_file(volume_file, projection_file)

# Create Shepp-Logan phantom
vol = odl.phantom.shepp_logan(proj.domain, modified=True)

# Project and show
result = proj(vol)
result.show()

# Also show back-projection
back_projected = proj.adjoint(result)
back_projected.show()
