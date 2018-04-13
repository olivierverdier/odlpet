# Copyright 2014-2017 The ODL contributors
#
# This file is part of ODL.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.

"""Back-end for STIR: Software for Tomographic Reconstruction.

Back and forward projectors for PET.

`ForwardProjectorByBinWrapper` and `BackProjectorByBinWrapper` are general
objects of STIR projectors and back-projectors, these can be used to wrap a
given projector.


References
----------
See the `STIR webpage`_ for more information and the `STIR doc`_ for info on
the STIR classes used here.

.. _STIR webpage: http://stir.sourceforge.net
.. _STIR doc: http://stir.sourceforge.net/documentation/doxy/html/
"""

import stir, stirextra


from odl.operator import Operator


import numpy as np



class ForwardProjectorByBinWrapper(Operator):

    """A forward projector using STIR.

    Uses "ForwardProjectorByBinUsingProjMatrixByBin" as a projector.
    """

    def __init__(self, domain, range, volume, proj_data,
                 _proj_info=None,
                 projector=None, adjoint=None):
        """Initialize a new instance.

        Parameters
        ----------
        domain : `DiscreteLp`
            Volume of the projection. Needs to have the same shape as
            ``volume.shape()``.
        range : `DiscreteLp`
            Projection space. Needs to have the same shape as
            ``proj_data.to_array().shape()``.
        volume : ``stir.FloatVoxelsOnCartesianGrid``
            Stir volume to use in the forward projection
        proj_data : ``stir.ProjData``
            Stir description of the projection.
        projector : ``stir.ForwardProjectorByBin``, optional
            A pre-initialized projector.
        adjoint : `BackProjectorByBinWrapper`, optional
            A pre-initialized adjoint.
        """
        # Check data sizes
        if domain.shape != volume.shape():
            raise ValueError('domain.shape {} does not equal volume shape {}'
                             ''.format(domain.shape, volume.shape()))
        # TODO: improve
        proj_shape = proj_data.to_array().shape()
        if range.shape != proj_shape:
            raise ValueError('range.shape {} does not equal proj shape {}'
                             ''.format(range.shape, proj_shape))

        # Set domain, range etc
        super().__init__(domain, range, linear=True)

        # Read template of the projection
        self.proj_data = proj_data
        if _proj_info is None:
            self.proj_data_info = proj_data.get_proj_data_info()
        else:
            self.proj_data_info = _proj_info
        self.volume = volume

        # Create forward projection by matrix
        if projector is None:
            self.proj_matrix = stir.ProjMatrixByBinUsingRayTracing()
            self.proj_matrix.set_do_symmetry_90degrees_min_phi(True)
            self.proj_matrix.set_do_symmetry_180degrees_min_phi(True)
            self.proj_matrix.set_do_symmetry_swap_s(True)
            self.proj_matrix.set_do_symmetry_swap_segment(True)
            self.proj_matrix.set_num_tangential_LORs(np.int32(1))

            self.proj_matrix.set_up(self.proj_data_info, self.volume)


            self.projector = stir.ForwardProjectorByBinUsingProjMatrixByBin(self.proj_matrix)

            self.projector.set_up(self.proj_data_info, self.volume)

            # If no adjoint was given, we initialize a projector here to
            # save time.
            if adjoint is None:
                back_projector = stir.BackProjectorByBinUsingProjMatrixByBin(
                    self.proj_matrix)
                back_projector.set_up(self.proj_data_info,
                                       self.volume)
        else:
            # If user wants to provide both a projector and a back-projector,
            # he should wrap the back projector in an Operator
            self.projector = projector
            back_projector = None

        # Pre-create an adjoint to save time
        if adjoint is None:
            self._adjoint = BackProjectorByBinWrapper(
                self.range, self.domain, self.volume, self.proj_data,
                back_projector, self)
        else:
            self._adjoint = adjoint

    def _call(self, volume, out):
        """Forward project a volume."""
        # Set volume data
        self.volume.fill(volume.asarray().flat)

        # project
        res = call_with_stir_buffer(self.projector.forward_project, self.volume, self.proj_data, volume)

        # make ODL data
        out[:] = res

    @property
    def adjoint(self):
        """Back-projector associated with this operator."""
        return self._adjoint


class BackProjectorByBinWrapper(Operator):

    """A back projector using STIR."""

    def __init__(self, domain, range, volume, proj_data,
                 back_projector=None, adjoint=None):
        """Initialize a new instance.

        Parameters
        ----------
        domain : `DiscreteLp`
            Projection space. Needs to have the same shape as
            ``proj_data.to_array().shape()``.
        range : `DiscreteLp`
            Volume of the projection. Needs to have the same shape as
            ``volume.shape()``.
        volume : ``stir.FloatVoxelsOnCartesianGrid``
            Stir volume to use in the forward projection
        proj_data : ``stir.ProjData``
            Stir description of the projection.
        back_projector : ``stir.BackProjectorByBin``, optional
            A pre-initialized back-projector.
        adjoint : `ForwardProjectorByBinWrapper`, optional
            A pre-initialized adjoint.

        Notes
        -----
        See `STIR doc`_ for info on the STIR classes.

        References
        ----------
        .. _STIR doc: http://stir.sourceforge.net/documentation/doxy/html/
        """
        # Check data sizes
        if range.shape != volume.shape():
            raise ValueError('`range.shape` {} does not equal volume shape {}'
                             ''.format(range.shape, volume.shape()))
        # TODO: improve
        proj_shape = proj_data.to_array().shape()
        if domain.shape != proj_shape:
            raise ValueError('`domain.shape` {} does not equal proj shape {}'
                             ''.format(range.shape, proj_shape))

        # Set range domain
        super().__init__(domain, range, True)

        # Read template of the projection
        self.proj_data = proj_data
        self.proj_data_info = proj_data.get_proj_data_info()
        self.volume = volume

        # Create forward projection by matrix
        if back_projector is None:
            proj_matrix = stir.ProjMatrixByBinUsingRayTracing()

            self.back_projector = stir.BackProjectorByBinUsingProjMatrixByBin(
                proj_matrix)
            self.back_projector.set_up(self.proj_data.get_proj_data_info(),
                                       self.volume)

            if adjoint is None:
                projector = stir.ForwardProjectorByBinUsingProjMatrixByBin(
                    proj_matrix)
                projector.set_up(self.proj_data_info, self.volume)

        else:
            self.back_projector = back_projector
            projector = None

        # Pre-create an adjoint to save time
        if adjoint is None:
            self._adjoint = ForwardProjectorByBinWrapper(
                self.range, self.domain, self.volume, self.proj_data,
                projector, self)
        else:
            self._adjoint = adjoint

    def _call(self, projections, out):
        """Back project."""
        res = call_with_stir_buffer(self.back_projector.back_project, self.proj_data, self.volume, projections, clear_buffer=True)

        # make ODL data
        out[:] = res

def call_with_stir_buffer(function, b_in, b_out, v_in, clear_buffer=False):
    b_in.fill(v_in.asarray().flat)
    if clear_buffer:
        b_out.fill(0)
    function(b_out, b_in)
    return stirextra.to_numpy(b_out)

