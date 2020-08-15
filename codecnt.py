#!/usr/bin/python3
#coding:utf-8

import os

# the followed is: help and configuration information.

def loghelp():
    print('''
    count the number of lines of source files.

    usage:

    codecnt --help

        print help information, that is this text.

    codecnt file1 file2 ... dir1 dir2 ...

        count the number of lines of the source files.
    ''')

def support(path):
    '''what types of source files are supported.'''

    suffixes = [
        ".c"   , ".h" ,
        ".cpp" , ".cc", ".cxx", ".hh", ".hpp",
        ".mm"  , ".m" ,
        ".java", ".cs", ".lua", ".py",
    ]
    for it in suffixes:
        if len(path) > len(it) and path.endswith(it):
            return True
    return False

# the followed is: traverse directories and get all subfile items.

class fileform:
    def __init__(self, isfile, deep, path):
        # "True" means file, "False" means directory.
        self.isfile = isfile

        self.deep = deep
        self.path = path

    def name(self):
        return os.path.basename(self.path)

    def indent(self):
        return ". " * self.deep

def traverse(arr, deep, path):
    '''traverses directories and gets all subfile items.'''

    if os.path.isdir(path):
        fstat = fileform(False, deep, path)
        arr.append(fstat)

        # note: the return result of "listdir" is unordered.
        items = os.listdir(path)
        items.sort()

        for it in items:
            sub = os.path.join(path, it)
            traverse(arr, deep + 1, sub)

    elif os.path.isfile(path) and support(path):
        fstat = fileform(True, deep, path)
        arr.append(fstat)

# the followed is: count the number of lines of source file.

class filedata:
    def __init__(self):
        self.filenum = 0
        self.codeln  = 0
        self.emptyln = 0

    def __add__(self, that):
        result = filedata()
        result.filenum = self.filenum + that.filenum
        result.codeln  = self.codeln  + that.codeln
        result.emptyln = self.emptyln + that.emptyln
        return result

    def sumln(self):
        return self.codeln + self.emptyln

    def percent(self, val):
        if self.sumln() > 0:
            per = val * 100 // self.sumln()
            return per if per < 100 else 99
        else:
            return 0

def notblank(line):
    '''does this line not only contain blank characters.'''

    for i in line:
        if i != ' ' and i != '\t' and i != '\r' and i != '\n':
            return True
    return False

def stat(path):
    '''counts the number of lines of source file.'''

    fdata = filedata()
    fdata.filenum = 1

    with open(path, "r") as file:
        lines = file.readlines()
        for it in lines:
            if notblank(it):
                fdata.codeln += 1
            else:
                fdata.emptyln += 1

        # whether the last line is a blank line.
        if len(lines) > 0 and len(lines[-1]) > 0:
            if lines[-1][-1] == '\n':
                fdata.emptyln += 1

    return fdata

# the followed is: print statistics data.

def logpos(path):
    print("@ %s:\n" % path)

def loghead():
    print("| sum|  code  |  empty  |")
    print("|----|--------|---------|")

def logfile(fform, fdata):

    values  = (fdata.sumln() ,)
    values += (fdata.codeln  , fdata.percent(fdata.codeln ))
    values += (fdata.emptyln , fdata.percent(fdata.emptyln))
    values += (fform.indent(),)
    values += (fform.name()  ,)

    # ...."|sum|___code___|___empty___|"
    print("[%4d|%4d/%02d%%|%4d/%02d%% ] %s%s" % values)

def logdir(fform):
    # ...."|_sum|__code__|__empty__|"
    print("[                       ] %s%s/" % (fform.indent(), fform.name()))

def logsum(title, d):
    if len(title) > 0:
        print("%s:\n" % title)
    else:
        print("")

    print("file number:%9s"        % (format(d.filenum, ",")))
    print("total lines:%9s"        % (format(d.sumln(), ",")))
    print("code lines :%9s/%02d%%" % (format(d.codeln , ","), d.percent(d.codeln )))
    print("empty lines:%9s/%02d%%" % (format(d.emptyln, ","), d.percent(d.emptyln)))
    print("")

# the followed is: main().

def every(path):

    sum = filedata()
    arr = []
    traverse(arr, 0, path)

    acc = 0
    for it in arr:
        # print one header every 20 lines.
        if acc % 20 == 0:
            loghead()
        acc += 1

        if it.isfile:
            fdata = stat(it.path)
            logfile(it, fdata)
            sum += fdata
        else:
            logdir(it)

    return sum

def main(args):

    if len(args) == 0 or args.count("--help") != 0:
        loghelp()
        return

    sum = filedata()
    for it in args:
        logpos(it)
        ths = every(it)
        logsum("", ths)

        sum += ths

    if len(args) > 1:
        logsum("summary", sum)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
