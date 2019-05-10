from partner import partner
import os
import pytest

def test_construct ():
    p = partner.Person("David","Marshall",None, "99384883") #type: partner.Person
    assert "David" == p.fname
    assert "Marshall" == p.lname
    assert "99384883" == p.id
