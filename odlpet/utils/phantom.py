import numpy as np
import odl.phantom

def cylinders_from_ellipses(ellipses):
    """Create 3d cylinders from ellipses.
    Adapted from odl/phantom/phantom_utils.py
    """
    ellipses = np.asarray(ellipses)
    ellipsoids = np.zeros((ellipses.shape[0], 10))
    ellipsoids[:, [0, 2, 3, 5, 6, 7]] = ellipses
    ellipsoids[:, 1] = 100000.0
    return ellipsoids

def derenzo(space):
    vol = odl.phantom.ellipsoid_phantom(
        space,
        cylinders_from_ellipses(odl.phantom.emission._derenzo_sources_2d()))
    return vol

