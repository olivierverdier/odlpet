from odl.operator import Operator

class SlicingProjectionOperator(Operator):
    """
    Projection operator defined from a slice.
    """
    def __init__(self, domain, codomain=None, slicing=None):
        if codomain is None:
            # very inefficient way to obtain the codomain
            codomain = domain.zero()[slicing].space
        super(SlicingProjectionOperator, self).__init__(domain, codomain, linear=True)
        self.__slicing = slicing

    @property
    def slicing(self):
        return self.__slicing

    def _call(self, x):
        return x[self.slicing]

    @property
    def adjoint(self):
        return SlicingInjectionOperator(self.range, self.domain, self.slicing)

class SlicingInjectionOperator(Operator):
    """
    Injection operator defined by a slice.
    """
    def __init__(self, domain, codomain, slicing):
        super(SlicingInjectionOperator, self).__init__(domain, codomain, linear=True)
        self.__slicing = slicing

    @property
    def slicing(self):
        return self.__slicing

    def _call(self, x):
        out = self.range.zero()
        out[self.slicing] = x
        return out

    @property
    def adjoint(self):
        return SlicingProjectionOperator(self.range, self.domain, self.slicing)

