from partner.models import Instructor
import bcrypt

if __name__ == '__main__':
    email = input("Enter email:")
    pw = input("Enter pw:").encode()
    user = Instructor.query.filter_by(email=email).first_or_404()
    if user:
        if bcrypt.checkpw(pw, user.password):
            print("Correct")
        else:
            print("Incorrect")