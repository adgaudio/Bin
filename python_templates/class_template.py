#!/bin/env python 

import os.path, sys

DEBUG = 1

class NAME:
    
    def __init__(self):
        pass
    def run(self):
        pass

def syntax(progname):
    print """
syntax:  %s 
""" % progname

if __name__ == '__main__':
    args = sys.argv
    progname = os.path.basename(args.pop())
    
    print syntax(progname)
    sys.exit(1)
