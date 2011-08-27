#!/usr/bin/env python

"""Simple util to format css if its hard to read"""

import os, sys
import re
from pprint import pprint

def parse(file):
    a = open(file, 'r').read()

    a = a.replace('\n', '')
    a = a.replace('\r', '')
    a = a.replace('\t', '')
    a = re.sub(r'[ ]+', ' ', a)

    o = re.compile(r'(;)')
    a = re.sub(o, r'\1\n    ', a)

    p = re.compile(r'([,])')
    a = re.sub(p, r'\1\n', a)

    q = re.compile(r'([{])')
    a = re.sub(q, r'\n\1\n    ', a)

    r = re.compile(r'([}])')
    a = re.sub(r, r'\n\1\n\n', a)

    a = re.sub(r'\n[ ]+\n','\n', a) #hack fix extra newline after semicolon
    print(a)

if __name__ == '__main__':
    try:
        parse(sys.argv[1])
    except:
        print "syntax: %s <css_file>" % os.path.basename(__file__)
        sys.exit(1)
