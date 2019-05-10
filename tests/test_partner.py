from partner import partner
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
    print(pairs)
    p1 = pairs[0][0]
    p2 = pairs[0][1]
    assert 1 == len(pairs)
    assert "David" == p1.fname
    assert "Paula" == p2.fname

def write_roster ():
    fname = os.path.dirname(os.path.realpath(__file__)) + '/files/rosterToday.csv'
    students = ["David Marshall 99944", "Paula Nieman 9933", "Walden Marshall 994843", "Jonathan Marshall 99483"]
    f = open(fname,"w")
    dt = partner.get_cur_date()
    f.write("First name,Nick name,Last name,ID number,"+ dt + "\n")
    for s in students:
        p = s.split()
        f.write("{},{},{},{},\n".format(p[0],'',p[1],p[2]))
    f.close()

# generate a roster with 4 students + todays date and read it to make sure 4 students in it
def test_roster ():
    write_roster()
    fname = os.path.dirname(os.path.realpath(__file__)) + '/files/rosterToday.csv'
    students = partner.readFile(fname)
    assert 4 == len(students)

def test_group_1 ():
    d = partner.Person("David","Marshall",None,"00")
    p = partner.Person("Paula","Nieman",None,"90")
    g = partner.Group([d,p])
    avoids = [[d,p]]
    assert True == g.hasPairToAvoid(avoids)

def test_group_2 ():
    d = partner.Person("David","Marshall",None,"00")
    p = partner.Person("Paula","Nieman",None,"90")
    x = partner.Person("Gomer","Pyle",None,"33")
    g = partner.Group([d,p])
    avoids = [[d,x]]
    assert False == g.hasPairToAvoid(avoids)

# make sure the pair to avoid is truly avoided.
def test_config2 ():
    fname = os.path.dirname(os.path.realpath(__file__)) + '/files/config.csv'
    pairsToAvoid = partner.readConfig(fname)
    write_roster()
    fname = os.path.dirname(os.path.realpath(__file__)) + '/files/rosterToday.csv'
    students = partner.readFile(fname)
    # generate groups 20 times to overcome shuffling of the 4 names
    for i in range(20):
        groups = partner.generateGroups(students, pairsToAvoid)
        for g in groups:
            assert False == g.hasPairToAvoid(pairsToAvoid)

