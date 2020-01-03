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

def get_current_year ():
    return today().year

def get_term (dt):
    if dt.month < 6:
        return 'spring'
    else:
        return 'fall'

def get_current_term ():
    t = today() #type: datetime.date
    return get_term(t)

def mdy_to_date (mdy):
    m,d,y = mdy.split('/')
    return datetime.date(month=int(m), day=int(d), year=int(y))

def date_to_mdy (date):
    return date.strftime("%m/%d/%Y")

def str_to_dict (str):
    d = {}
    for pair in str.split(','):
        k,v = pair.split(':')
        d[k.strip()] = v.strip()
    return d

# convert yyyy-mm-ddTHH:mm:ss to datetime.date
def jsdate_to_date (str):
    y,m,d = str.split('T')[0].split('-')
    return datetime.date(month=int(m), day=int(d), year=int(y))

def str_to_date (str):
    if 'T' in str:
        return jsdate_to_date(str)
    else:
        return mdy_to_date(str)
