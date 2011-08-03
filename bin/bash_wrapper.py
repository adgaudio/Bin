#!/usr/bin/env python

import subprocess
import sys, os
import datetime


def getEnv(string, delimiter='\n', subdelimiter='='):
    """Given string and delimiters, 
    parse values by delimeter and return dict"""
    d = {}
    for pair in string.split(delimiter):
        pair = pair.strip()

        if pair == '':     continue
        if subdelimiter not in pair:
            print 'skipping'
            continue

        k,v = pair.split(subdelimiter, 1)
        d[k] = str(v)
    return d



# Establish vars
f = open(sys.argv[1], 'r').readlines()
if len(sys.argv) == 3:
    log_summary = open(sys.argv[2], 'w')
    log_expanded = open(sys.argv[3], 'w')
else:
    log_summary = sys.stdout
    class NullOut: write=lambda *x:None
    log_expanded = NullOut()
lastenv = os.environ.copy()
marker = "____BASHWRAPPER_SPLITONTHIS____"
    
# Run commands
for cmd in f: 
    if cmd == '' or cmd.startswith('#'): continue 
    cmd = cmd.strip() + "; echo %s ; set" % marker 
    msg = """
=====================================
CMD: %s
TIME: %s
=====================================
"""
    msg = msg % (cmd.strip(), datetime.datetime.now().isoformat()) 

    log_summary.write(msg)
    log_expanded.write(msg)
    
    shell = subprocess.Popen(cmd, 
                             shell=True, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             env=lastenv)
    result = shell.communicate()
    output = result[0].split(marker, 1)

    if result[1] != '':
        msg2 =('\n---STDOUT:%s\n---STDERR:%s' % (str(output[0]), str(result[1]))) 
        raise Exception(msg2)
    lastenv = getEnv(output[1])
    import pdb ; pdb.set_trace()    
    log_expanded.write("""
STDOUT:
%s""" % output[0])
