#!/usr/bin/env python
"""Create a new admin user able to view the /reports endpoint."""
from getpass import getpass
import sys
import bcrypt
from partner import app, db
from partner.models import Instructor

def hash_password (pw):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(pw.encode(), salt)
    return hashed_pw

def create_instructor (email, pw):
    hashed_pw = hash_password(pw)
    inst = Instructor(
        email=email,
        password=hashed_pw)
    db.session.add(inst)
    db.session.commit()
    return inst

def create_users():
    """Main entry point for script."""
    with app.app_context():
        db.metadata.create_all(db.engine)
        if Instructor.query.all():
            print('Instructor already exists! Create another? (y/n):'),
            create = input()
            if create == 'n':
                return

        print('Enter email address: '),
        email = input()
        password = getpass()
        assert password == getpass('Password (again):')
        x = Instructor.query.filter_by(email=email).first()
        if x:
            ov = input("Instructor with that email already exists.  Overwrite?")
            if ov.lower() != 'yes':
                print("Not created")
                return
            else:
                hashed_pw = hash_password(password)
                x.password = hashed_pw
                db.session.commit()
                print(f"Instructor {email} updated")
                return
        else:
            create_instructor(email, password)
        print('Instructor added.')


if __name__ == '__main__':
    sys.exit(create_users())