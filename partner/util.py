import time
from typing import Dict
from datetime import date

def get_cur_date (sep="/", yy_format=True) -> str:
    mm = time.strftime("%m")
    dd = time.strftime("%d")
    if yy_format:
        y = time.strftime("%y") #yy
    else:
        y = time.strftime("%Y")  #yyyy
    return sep.join([mm, dd, y])

def parse_date (mmddyyyy: str) -> date:
    parts = mmddyyyy.split('/')
    y = int(parts[2])
    m = int(parts[0])
    d = int(parts[1])
    return date(year=y, month=m, day=d)

def is_in_past (dt: date):
    today = date.today()
    return today.toordinal() > dt.toordinal()

def is_today (dt: date):
    today = date.today()
    return today.toordinal() == dt.toordinal()

def today () -> date:
    return date.today()

def get_current_year ():
    return today().year

def get_term (dt: date) -> str:
    if dt.month < 6:
        return 'spring'
    else:
        return 'fall'

def get_current_term () -> str:
    t = today()
    return get_term(t)

def mdy_to_date (mdy: str) -> date:
    m,d,y = mdy.split('/')
    return date(month=int(m), day=int(d), year=int(y))

def date_to_mdy (d: date) -> str:
    return d.strftime("%m/%d/%Y")

def str_to_dict (s: str) -> Dict[str, str]:
    d = {}
    for pair in str.split(','):
        k,v = pair.split(':')
        d[k.strip()] = v.strip()
    return d

# convert yyyy-mm-ddTHH:mm:ss to datetime.date
def jsdate_to_date (s: str) -> date:
    y,m,d = s.split('T')[0].split('-')
    return date(month=int(m), day=int(d), year=int(y))

def str_to_date (s: str) -> date:
    if 'T' in s:
        return jsdate_to_date(s)
    else:
        return mdy_to_date(s)
