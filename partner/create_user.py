#!/usr/bin/env python
"""Create a new admin user able to view the /reports endpoint."""
from getpass import getpass
import sys
import bcrypt
from partner import app, db
from partner.models import User

def create_user (email, pw):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(pw.encode(), salt)
    user = User(
        email=email,
        password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return user

def create_users():
    """Main entry point for script."""
    with app.app_context():
        db.metadata.create_all(db.engine)
        if User.query.all():
            print('A user already exists! Create another? (y/n):'),
            create = input()
            if create == 'n':
                return

        print('Enter email address: '),
        email = input()
        password = getpass()
        assert password == getpass('Password (again):')
        create_user(email, password)
        print('User added.')


if __name__ == '__main__':
    sys.exit(create_users())