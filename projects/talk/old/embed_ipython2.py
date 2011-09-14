b = [3,4]

from embed_ipython import *

print 'embed_ipython2: start interactive shell'
ipshell()
print 'embed_ipython2: close interactive shell'

def a():
    c = 1
    print c
    print "The shell stores variables from the namespace where is called"
    print "... and resumes where we last left off"
    ipshell()

a()
