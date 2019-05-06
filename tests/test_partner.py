import partner
import os
import pytest

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'files',
)

@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'notexist.csv'))
def test_config0 (datafiles):
    fname = datafiles[0]
    with pytest.raises(Exception):
        pairs = partner.readConfig(fname)

@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'empty_config.csv'))
def test_config1 (datafiles):
    fname = datafiles[0]
    pairs = partner.readConfig(fname)
    assert [] == pairs

@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'config.csv'))
def test_config2 (datafiles):
    fname = datafiles[0]
    pairs = partner.readConfig(fname)
    assert "David Marshall" == pairs[0][0]
    assert "Paula Nieman" == pairs[0][1]