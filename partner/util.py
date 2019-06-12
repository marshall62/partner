import time

def get_cur_date (sep="/", yy_format=True):
    mm = time.strftime("%m")
    dd = time.strftime("%d")
    if yy_format:
        y = time.strftime("%y") #yy
    else:
        y = time.strftime("%Y")  #yyyy
    return sep.join([mm, dd, y])