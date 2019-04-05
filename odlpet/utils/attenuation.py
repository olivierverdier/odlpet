import numpy as np

def get_attenuation_multiplicator(operator, attenuation_volume):
    """
    Compute an attenuation multiplicator for a given attenuation volume in cm^{-1}.
    """
    pixel_size = operator.domain.cell_sides[1]
    atn_proj = operator(attenuation_volume)
    return np.exp(-atn_proj*pixel_size/10)

def attenuation_conversion(volume, kvp='120'):
    """
    Implements the mapping defined in
        Carney, J. P., Townsend, D. W., Rappoport, V. and Bendriem, B. (2006),
        Method for transforming CT images for attenuation correction in PET/CT imaging.
        Med. Phys., 33: 976-983.
        doi:10.1118/1.2174132
    """
    return _piecewise_affine_attenuation_conversion(volume, **KVP_DICT[str(kvp)])

KVP_DICT = {
    "80":
    {
        "a": 3.64e-5,
        "b": 6.261e-2,
        "breakpoint": 50,
    },
    "100":
    {
        "a": 4.43e-5,
        "b": 5.44e-2,
        "breakpoint": 52,
    },
    "110":
    {
        "a": 4.92e-5,
        "b": 4.88e-2,
        "breakpoint": 43,
    },
    "120":
    {
        "a": 5.1e-5,
        "b": 4.71e-2,
        "breakpoint": 47,
    },
    "130":
    {
        "a": 5.51e-5,
        "b": 4.24e-2,
        "breakpoint": 37,
    },
    "140":
    {
        "a": 5.64e-5,
        "b": 4.08e-2,
        "breakpoint": 30,
    },
}

def _piecewise_affine_attenuation_conversion(volume, breakpoint, a, b):
    attenuation = np.zeros_like(volume, dtype=np.float)
    #volume_ = volume - 24
    volume_ = volume
    small = volume_ < breakpoint
    attenuation[small] = (volume_[small])*(9.6e-5)
    attenuation[~small] = a*(volume_[~small]) + b
    attenuation[attenuation < 0] = 0
    return attenuation

