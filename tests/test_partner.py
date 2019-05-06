import pytest
import partner

def test_config0 ():
    fname = '/home/marshall/dev/partner/tests/files/notexist.csv'
    with pytest.raises(Exception):
        pairs = partner.readConfig(fname)

def test_config1 ():
    fname = '/home/marshall/dev/partner/tests/files/empty_config.csv'
    pairs = partner.readConfig(fname)
    assert [] == pairs

def test_config2 ():
    fname = '/home/marshall/dev/partner/tests/files/config.csv'
    pairs = partner.readConfig(fname)
    assert "David Marshall" == pairs[0][0]
    assert "Paula Nieman" == pairs[0][1]