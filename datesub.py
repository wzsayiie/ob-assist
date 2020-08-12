#!/usr/bin/python3
#coding:utf-8

# the following is: help information.

def help():
    return '''
    calculate the number of days between two dates.

    usage:

    datesub --help

        print the help information, that is this text.

    datesub 2010.1.1 2020.6.30

        calculate the number of days between "2010.1.1" and "2020.6.30".

    datesub --ignore-weekend 2010.1.1 2020.6.30

        calculate the number of days between "2010.1.1" and "2020.6.30",
        ignore saturday and sunday.
    '''

# the following is: the handling process of date.

def leap(year):
    '''if the year is a leap year, returns true.'''
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def monthdays(year, month):
    '''returns the number of days in the month.'''

    arr = [0,
        31, 28, 31, 30, 31, 30,
        31, 31, 30, 31, 30, 31,
    ]
    if leap(year) and month == 2:
        return 29
    else:
        return arr[month]

def serial(year, month, day):
    '''january 1, 1 ad is the first day, calculates which day this date is.'''

    val = 0

    for i in range(1, year):
        val += 366 if leap(i) else 365
    for i in range(1, month):
        val += monthdays(year, i)
    val += day

    return val

def weekday(day):
    '''what day of week is the day. if monday returns 1, if sunday returns 0.'''
    return day % 7

def legal(year, month, day):
    '''is this a legal date.'''
    return  1 <= year and 1 <= month <= 12 and 1 <= day <= monthdays(year, month)

# the following is: calculate ho many days between two dates.

def workingdays(begin, count):
    '''starting with the week day "begin", how many working days in the next "count" days.'''

    arr = []

    if   begin == 0: arr = [0, 0, 1, 2, 3, 4, 5]
    elif begin == 1: arr = [0, 1, 2, 3, 4, 5, 5]
    elif begin == 2: arr = [0, 1, 2, 3, 4, 4, 4]
    elif begin == 3: arr = [0, 1, 2, 3, 3, 3, 4]
    elif begin == 4: arr = [0, 1, 2, 2, 2, 3, 4]
    elif begin == 5: arr = [0, 1, 1, 1, 2, 3, 4]
    elif begin == 6: arr = [0, 0, 0, 1, 2, 3, 4]

    return arr[count]

def sub(begin, end, weekend):
    '''calculates how many days between two serial number,
    the parameter "weekend" indicates whether saturday and sunday are included.'''

    days = end - begin

    if not weekend:
        #
        #    |<- weeks ->||left|
        #    xxx........xxoooooo
        #   ^             ^    ^
        #   |             |    |
        # begin         split end
        #
        # the week day of "begin + 1" and "split" are same.
        #
        weeks = days // 7
        left  = days %  7
        split = weekday(begin + 1)
        days  = 5 * weeks + workingdays(split, left)

    return days

# the following is: convert string to date.

def pick(str, idx):
    '''reads an integer from a string.'''

    num = 0

    while idx < len(str):
        ch = str[idx]
        if '0' <= ch <= '9':
            num = num * 10 + ord(ch) - ord('0')
            idx += 1
        elif ch == '.':
            idx += 1
            break
        else:
            # illegal char appeared.
            idx += 1
            num = 0
            break

    return num, idx

def convert(str):
    '''parses a string as a date and calculates its serial number.'''

    year , next = pick(str, 0)
    month, next = pick(str, next)
    day  , next = pick(str, next)

    if next == len(str) and legal(year, month, day):
        return serial(year, month, day)
    else:
        return 0

# the following is: analyze the command line arguments.

class intent:
    help  = 1
    calc  = 2
    error = 3

class task:

    def __init__(self):
        self.intent  = intent.help
        self.error   = ""
        self.weekend = True
        self.begin   = 0
        self.end     = 0

    def sethelp(self):
        self.help = intent.help

    def setfatal(self, error):
        self.intent = intent.error
        self.error = error

    def setpoint(self, point):
        self.intent = intent.calc
        if self.begin == 0:
            self.begin = point
        else:
            self.end = point

    def full(self, weekend):
        self.weekend = weekend

    def ready(self):
        return self.begin > 0 and self.end > 0

def parse(args):
    '''parses command line arguments and analyses the user intent.'''

    job = task()

    for it in args:
        if it.startswith("--"):
            if it == "--ignore-weekend":
                job.full(False)
            elif it == "--help":
                job.sethelp()
                break
            else:
                job.setfatal("unknown option '%s'." % it)
                break

        elif not job.ready():
            point = convert(it)
            if point == 0:
                job.setfatal("invalid date string '%s'." % it)
                break
            else:
                job.setpoint(point)

        else:
            job.setfatal("redundant parameter '%s'." % it)
            break

    if job.intent == intent.calc and not job.ready():
        job.setfatal("no enough parameters.")

    return job

# the following is: main().

def main(args):
    job = parse(args)

    if job.intent == intent.calc:
        print("%d" % sub(job.begin, job.end, job.weekend))

    elif job.intent == intent.help:
        print("%s" % help())

    elif job.intent == intent.error:
        print("error: %s" % job.error)

    else:
        print("error: internal error.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
