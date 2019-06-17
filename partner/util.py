import time
import datetime

def get_cur_date (sep="/", yy_format=True):
    mm = time.strftime("%m")
    dd = time.strftime("%d")
    if yy_format:
        y = time.strftime("%y") #yy
    else:
        y = time.strftime("%Y")  #yyyy
    return sep.join([mm, dd, y])

def parse_date (mmddyyyy):
    parts = mmddyyyy.split('/')
    y = int(parts[2])
    m = int(parts[0])
    d = int(parts[1])
    return datetime.date(year=y, month=m, day=d)

def is_in_past (dt):
    today = datetime.date.today()
    return today.toordinal() > dt.toordinal()

def is_today (dt):
    today = datetime.date.today()
    return today.toordinal() == dt.toordinal()

def today ():
    return datetime.date.today()

def to_mdy (date):
    return date.strftime("%m/%d/%Y")