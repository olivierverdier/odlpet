import pytest

import odlpet.scanner.scanner as scan

def test_consistency():
    ss = scan._get_stir_scanner_by_name('Userdefined')
    ss.set_num_axial_crystals_per_block(10)
    ss.set_num_axial_blocks_per_bucket(10)
    ss.set_num_rings(34)
    assert ss.get_num_axial_crystals_per_block() * ss.get_num_axial_blocks() != ss.get_num_rings()
    assert not scan._check_consistency(ss)
    s = scan.Scanner.from_stir_scanner(ss)
    with pytest.raises(ValueError):
        s.get_stir_scanner()

def test_names():
    names = scan._get_scanner_names()
    for name in names:
        stir_scan = scan._get_stir_scanner_by_name(name)
        assert stir_scan.get_name() == name

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
            assert stir_scan == stir_scan_
