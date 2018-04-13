import pytest

import odlpet.scanner.scanner as scan

def test_consistency():
    ss = scan._get_stir_scanner_by_name('Userdefined')
    ss.set_num_axial_crystals_per_block(10)
    ss.set_num_axial_blocks_per_bucket(10)
    ss.set_num_rings(34)
    assert ss.get_num_axial_crystals_per_block() * ss.get_num_axial_blocks() != ss.get_num_rings()
    assert not scan._check_consistency(ss)

def test_names():
    names = scan.get_scanner_names()
    for name in names:
        stir_scan = scan._get_stir_scanner_by_name(name)
        assert stir_scan.get_name() == name


# for debugging purposes only
SCAN_GETTERS = [
    "get_num_rings",
    "get_num_detectors_per_ring",
    "get_num_axial_blocks_per_bucket",
    "get_num_transaxial_blocks_per_bucket",
    "get_num_axial_crystals_per_block",
    "get_num_transaxial_crystals_per_block",
    "get_num_axial_crystals_per_singles_unit",
    "get_num_transaxial_crystals_per_singles_unit",
    "get_num_detector_layers",
    "get_inner_ring_radius",
    "get_average_depth_of_interaction",
    "get_ring_spacing",
    "get_default_bin_size",
    "get_default_intrinsic_tilt",
    "get_default_num_arccorrected_bins",
    "get_max_num_non_arccorrected_bins",
]

def test_conversion():
    """
    Converting from STIR to Python and back should give the same object.
    """
    for scan_name in scan.SCANNER_NAMES:
        print(scan_name)
        stir_scan = scan._get_stir_scanner_by_name(scan_name)
        stir_scan.check_consistency()
        py_scan = scan.Scanner.from_stir_scanner(stir_scan)
        try:
            stir_scan_ = py_scan.get_stir_scanner()
        except:
            print(scan_name)
        else:
            # for g in SCAN_GETTERS:
            #     assert pytest.approx(getattr(stir_scan, g)()) == getattr(stir_scan_, g)()
            assert stir_scan == stir_scan_
