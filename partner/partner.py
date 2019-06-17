__author__ = 'david'
import urllib.request
import random
import time
import csv
from partner.Person import Person

GROUP_SIZE = 2

# Banner no longer correctly downloads spreadsheets so I changed the program to work off
# sheets obtained from exporting the gradebook from moodle.  Have to login to each lab
# goto Administration Grade Administration Export and get as open doc spreadsheet
# This program is run AFTER calling attendance with the CSV spreadsheet.  Steps for doing this:
#  o Insert a Column with todays date in row 1 formated like 9/26/2016
#  o Call attendance and mark "a" in this column if a student is absent.
#  o Run this program and give it the correct lab.
#   It will generate partnerships based on who is present.

# STUDENT_NAME_COLS = ['Student Name*']  # Column header for student name from Banner spreadsheet
name_map = {"first": "First name",  "nick": "Nick name", "last": "Last name", "id": "ID number"}



# folder = "C:\\Users\\david\\Google Drive\\Smith\\Spring17\\"
folder="rosters/"
partners_folder = "partners_out/"

f1=  "lab4_w1.csv"
f2=  "lab1_w3.csv"
f3=  "lab3_th1.csv"
f4=  "lab2_th3.csv"

config = folder + "pairs2avoid.csv"

class MissingDateHeaderException (Exception):
    pass


class Group:

    def __init__ (self, members):
        self.members = members

    def hasPerson(self, person):
        for m in self.members:
            # using fuzzy equals because the pairs2avoid file sometimes uses nick names like first names
            if m.fuzzy_equals(person):
                return True
        return False

    def hasPairToAvoid (self, pairsToAvoid):
        for pair in pairsToAvoid:
            person1 = pair[0]
            person2 = pair[1]
            if self.hasPerson(person1) and self.hasPerson(person2):
                return True
        return False

    def add_member (self, member):
        self.members.append(member)


    def __str__ (self):
        s = ""
        for m in self.members:
            s += m.__str__() + "..."
        return s[0:-3]    # eliminate trailing ...

    def to_dict (self):
        d = {}
        d['group'] = self
        d['members'] = [p.to_dict() for p in self.members]
        return d

    def to_csv (self):
        line = ""
        for p in self.members:
            line += p.to_csv() + ","
        return line[0:-1] # remove trailing ,


# get the various cells that contain the person and return it
def get_person_from_row (row):
    fn = row[name_map["first"]].strip()
    ln = row[name_map["last"]].strip()
    nn = row[name_map["nick"]].strip()
    id = row[name_map["id"]].strip()
    return Person(fn,ln,nn,id)

def get_cur_date (sep="/", yy_format=True):
    mm = time.strftime("%m")
    dd = time.strftime("%d")
    if yy_format:
        y = time.strftime("%y") #yy
    else:
        y = time.strftime("%Y")  #yyyy
    return sep.join([mm, dd, y])


#  Return a list of present students.
def readFile (f):
    present_students = []
    # The first line of the CSV file has the headers which become the keys of a dict for each row read in
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            person = get_person_from_row(row)
            isAbsent = check_row_absence(row)
            if not isAbsent:
                present_students.append(person)
    return present_students

def check_row_absence (row):
    # sometimes the col header is mm/dd/yy and sometimes mm/dd/yyyy depending on spreadsheet auto-formatting.
    d_yy =  date_col = get_cur_date(yy_format=True)
    d_yyyy = date_col = get_cur_date(yy_format=False)
    if type(row.get(d_yy, False)) == str:
        val= row[d_yy]
    elif type(row.get(d_yyyy,False)) == str:
        val= row[d_yyyy]
    else:
        raise MissingDateHeaderException("Cannot find the date " + d_yy + " or " + d_yyyy + " at the top of the file")
    return val.strip().upper().startswith("A")

# Read a config file that has pairs of students to avoid.
# A line is like:  Marshall, David A | Nieman, Paula which means these two people should not be put in a group
# Returns a list of lists where each sublist contains 2 person objects
def readConfig (fname):
    file = open(fname,"r")
    lines = file.readlines();
    pairs = []
    for line in lines:
        pair = line.split(',') # line is fname1 lname1, fname2 lname2
        p1 = pair[0].split()
        p2 = pair[1].split()
        person1 = Person(p1[0].strip(),p1[1].strip(), None, None)
        person2 = Person(p2[0].strip(),p2[1].strip(), None, None)
        pairs.append([person1, person2])
    return pairs


def generateGroups (student_list, pairsToAvoid):
   random.shuffle(student_list)

   groups = []
   for i in range(0,len(student_list), GROUP_SIZE):
       # if the remaining students in the list aren't enough to create a group, put in the last group
       if len(student_list[i:]) < GROUP_SIZE:
           g = groups[-1]
           for j in range(i,len(student_list)):
               g.add_member(student_list[j])
       else:
           g = Group(student_list[i:i+GROUP_SIZE])
           # If this group contains a pair to avoid, start over.
           if g.hasPairToAvoid(pairsToAvoid):
               return generateGroups(student_list, pairsToAvoid)
           groups.append(g)
   return groups



def printGroups (groups):
    for g in groups:
        print(g)

def saveGroups (groups, lab_name):
    lab_name = lab_name.split('.')[0]
    file_name = partners_folder + lab_name + "_partners_" + get_cur_date("_") + ".csv"
    f = open(file_name,"w")
    for g in groups:
        f.write(g.to_csv() + "\n")
    f.close()
    print("Saved groups in file " + file_name)


def getLabNum():
    n = input("Enter lab # (1:W-1, 2: W-3, 3 Th-1, 4 Th-3, q quit):").strip()
    return n

# Given the url of the roster and the column number of the attendance (optional)
# produce a list of pairs
def main ():
    # get a list of pairs to avoid making
    pairsToAvoid = readConfig(config)
    while True:
        command = getLabNum()
        if command.strip().lower() == 'q':
            print("Bye")
            break
        elif command not in ['1','2','3','4']:
            print("Error: Enter 1,2,3,4")
            continue
        lab_name = eval("f"+command) # a global variable above is refed from the string built from lN
        print(lab_name)
        try:
            students = readFile(folder+lab_name)
        except MissingDateHeaderException as exc:
            print(exc)
            continue
        groups = generateGroups(students, pairsToAvoid)
        printGroups(groups)
        saveGroups(groups, lab_name)


if __name__ == "__main__":
    main()
