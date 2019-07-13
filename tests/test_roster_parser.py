import os
from rosters.RosterParser import RosterParser
class TestRosterParser:

    def test_file_simplify (self):
        source = os.path.dirname(os.path.realpath(__file__)) + '/files/new_classlist.csv'
        dest = os.path.dirname(os.path.realpath(__file__)) + '/files/simple_new_classlist.csv'
        p = RosterParser()
        p.clean_file(source, dest)
        assert True
