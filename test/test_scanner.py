import stir

import odlpet.scanner.scanner as scan

def test_consistency():
    ss = stir.Scanner.get_scanner_from_name('Userdefined')
    ss.set_num_axial_crystals_per_block(10)
    ss.set_num_axial_blocks_per_bucket(10)
    ss.set_num_rings(34)
    assert ss.get_num_axial_crystals_per_block() * ss.get_num_axial_blocks() != ss.get_num_rings()
    assert not scan._check_consistency(ss)

def test_names():
    names = scan.get_scanner_names()
    for name in names:
        stir_scan = stir.Scanner.get_scanner_from_name(name)
        assert stir_scan.get_name() == name
