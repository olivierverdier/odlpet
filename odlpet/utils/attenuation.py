import numpy as np

def get_attenuation_multiplicator(operator, attenuation_volume):
    """
    Compute an attenuation multiplicator for a given attenuation volume in cm^{-1}.
    """
    pixel_size = operator.domain.cell_sides[1]
    atn_proj = operator(attenuation_volume)
    return np.exp(-atn_proj*pixel_size/10)
