import os
import time
from datetime import datetime


def print_hi(name):
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


if __name__ == '__main__':
    print_hi('PyCharm')

    print("Last modified: %s" % time.ctime(os.path.getmtime("test.txt")))
    print("Created: %s" % time.ctime(os.path.getctime("test.txt")))

    # gives the create time as a unix timestamp
    create_time = os.stat("test.txt").st_ctime

    # returns a datetime object
    create_datetime = datetime.fromtimestamp(create_time)

    # print the year
    print(create_datetime.strftime("%Y"))

