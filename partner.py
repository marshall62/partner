__author__ = 'david'
import urllib.request
import random
import time
import csv

GROUP_SIZE = 2
# The roster is downloaded from Banner web as an Excel file that is then changed to CSV format.
# This program is run AFTER calling attendance with the CSV spreadsheet.  Steps for doing this:
#  o Insert a Column with todays date in row 1 formated like 9/26/2016
#  o Call attendance and mark "a" in this column if a student is absent.
#  o Run this program and give it the correct lab.
#   It will generate partnerships based on who is present.

STUDENT_NAME_COL = 'Student Name*'  # Column header for student name from Banner spreadsheet

l1="https://docs.google.com/spreadsheets/d/1tF4cAwW7POoX53g04ndN9oPOgvpFloNQysFcmCsh0AM/pub?output=csv"
l2="https://docs.google.com/spreadsheets/d/1ti1zxHCzzwI2fcnOBALljz4oGInrspWt1BS0xETDuHE/pub?output=csv"
l3="https://docs.google.com/spreadsheets/d/1oOwCW3zifrGJvWWTiDn9CZZ-9BeBQmG64i56Vj0C7G4/pub?output=csv"
l4="https://docs.google.com/spreadsheets/d/1oZPgfFMBPF28rLikrGfnXxlDCS_58H9uVnLLkTxKnHI/pub?output=csv"

# folder = "C:\\Users\\david\\Google Drive\\Smith\\Spring17\\"
folder=""
f1= folder+ "lab4-w1.csv"
f2= folder+ "lab1-w3.csv"
f3= folder+ "lab2-t1.csv"
f4= folder+ "lab3-t3.csv"

config = folder + "config.csv"



class Group:

    def __init__ (self, members):
        self.members = members

    # return whether the person (given as "lname, fname initial" is in the group
    # Nota Bene:  This means the names in the config.csv need to be entered almost exactly as they are in
    # in the class list (I say almost because I typically enter nicknames like Marshall, David A (Dave-o)  which
    # will only use a startswith test if the config uses Marshall, David A so the Dave-o won't cause a mismatch
    def hasPerson(self, person):
        for m in self.members:
            member = m.split(',')
            personToAvoid = person.split(',')
            if member[0].startswith(personToAvoid[0]) and member[1].startswith(personToAvoid[1]):
                return True
        return False

    def hasPairToAvoid (self, pairsToAvoid):
        found = True
        for pair in pairsToAvoid:
            p1 = pair[0]  # a name like "Marshall, David A"
            p2 = pair[1]
            if self.hasPerson(p1) and self.hasPerson(p2):
                return True
        return False


    def __str__ (self):
        s = ""
        for m in self.members:
            person = m.split(',') # names are backward like Marshall, David
            person = person[1] + " " + person[0]
            s += person+ "..."
        return s[0:-3]    # eliminate trailing ...

# Given the list of headers and a string, return the index of the header that matches the string
def getCol (headers, str):
    for i in range(0,len(headers)):
        if headers[i].lower().startswith(str.lower()):
            return i
    return -1

# return the index of the column for the student name
def getNameCol (headers):
    n= getCol(headers, STUDENT_NAME_COL) # This is what is in the Col header from Banner download
    # ln= getCol(headers, "last name")
    return n

# Assumes that a column exists with today's date as the header (in m/d/yyyy format )
# return the index of this column
def getCurDateCol (headers):
    mm = time.strftime("%m")
    m = int(mm)
    dd = time.strftime("%d")
    d = int(dd)
    yyyy = time.strftime("%Y")
    dt = "%d/%d/%s" % (m,d,yyyy)
    dtix= getCol(headers,dt)
    return dtix

#  Return a list of the student names.  Omit students that have been marked absent today.
def readFile (f):
    
    names = []
    # The first line of the CSV file has the headers we care about and then there are two lines
    # that can be skipped before the students begin
    with open(f, 'r') as f:
        reader = csv.reader(f)
        i=0
        for row in reader:
            #print("ROW", row)
            # dates for attendance are in row 0
            if i == 0:
                dix =getCurDateCol(row)
                nix=getNameCol(row)
            else:
                name = row[nix].strip()
                if len(name.strip()) == 0:
                    continue
                absent = False
                if dix != -1 :
                    absent = row[dix].strip().startswith("a") or row[dix].strip().startswith("A")
                if not absent:
                    names.append(name)
            i += 1
    return names

# Read a config file that has pairs of students to avoid.
# A line is like:  Marshall, David A | Nieman, Paula which means these two people should not be put in a group
# Returns a list of lists like [["Marshall, David A", "Nieman, Paula"], [],... ]
def readConfig (fname):
    file = open(fname,"r")
    lines = file.readlines();
    pairs = []
    for line in lines:
        pair = line.split('|')
        pairs.append(pair)
    return pairs

#  Return a list of the student names.  Omit students that have been marked absent today.
def readFileFromWeb (url):
    tempfile = "roster.csv"
    f = open(tempfile,"w")
    f.close()
    urllib.request.urlretrieve(url,tempfile)
    names = []
    # The first line of the CSV file has the headers we care about and then there are two lines
    # that can be skipped before the students begin
    with open(tempfile, 'r') as f:
        reader = csv.reader(f)
        i=0
        for row in reader:
            #print("ROW", row)
            # dates for attendance are in row 0
            if i == 0:
                dix =getCurDateCol(row)
                nix=getNameCol(row)
            else:
                name = row[nix].strip() + " " + row[nix].strip()
                if len(name.strip()) == 0:
                    continue
                absent = False
                if dix != -1 :
                    absent = row[dix].strip().startswith("a") or row[dix].strip().startswith("A")
                if not absent:
                    names.append(name)
            i += 1
    return names




def generateGroups (listOfNames, pairsToAvoid):
   random.shuffle(listOfNames)

   groups = []
   for i in range(0,len(listOfNames), GROUP_SIZE):

       g = Group(listOfNames[i:i+GROUP_SIZE])
       # If this group contains a pair to avoid, start over.
       if g.hasPairToAvoid(pairsToAvoid):
           return generateGroups(listOfNames, pairsToAvoid)
       groups.append(g)
   return groups



def printGroups (groups):
    for g in groups:
        print(g)

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
        if command == 'q':
            break

        labURL = eval("f"+command) # a global variable above is refed from the string built from lN
        print(labURL)
        #url = input("URL of roster:")
        students = readFile(labURL)
        groups = generateGroups(students, pairsToAvoid)
        printGroups(groups)

main()
