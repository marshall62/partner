import partner
import os
import pytest


def test_config0 ():
    fname = os.path.dirname(os.path.realpath(__file__)) + '/files/notexist.csv'
    with pytest.raises(Exception):
        pairs = partner.readConfig(fname)

def test_config1 ():
    fname = os.path.dirname(os.path.realpath(__file__)) + '/files/empty_config.csv'
    pairs = partner.readConfig(fname)
    assert [] == pairs


def test_config2 ():
    fname = os.path.dirname(os.path.realpath(__file__)) + '/files/config.csv'
    pairs = partner.readConfig(fname)
    assert "David Marshall" == pairs[0][0]
    assert "Paula Nieman" == pairs[0][1]