#!/usr/bin/env python

import subprocess
import sys, os
import datetime

class BashWrapper(object):
    """Wrap a simple bash script to provide:
           1. Workflow: By default, stop execution if stderr is returned
           2. Logging: Specify an object with a write method 
              (like sys.stdout, or an open file)

       Gotchas: script can't have code blocks (if, for, while, etc), 
                but it can use variables
    """
    def __init__(self):
        pass
    
    def split2dict(self, string, delimiter='\n', subdelimiter='='):
        """Given string (of bash env vars) and delimiters, 
        parse values by delimeter and return dict"""
        d = {}
        for pair in string.split(delimiter):
            pair = pair.strip()

            if pair == '':     continue
            if subdelimiter not in pair:
                print 'WARNING: skipping env variable:', pair
                continue

            k,v = pair.split(subdelimiter, 1)
            d[k] = str(v)
        return d
    
    def wrap(self, bashfile, writer=sys.stdout): 
	"""Given filepath to bash script, execute commands and write output"""
        f = open(bashfile, 'r').readlines()
        env = os.environ.copy()

        # If no output wanted at all
        class NullOut: write=lambda *x:None
        if not writer:
            writer = NullOut()

        # Run commands
        for cmd in f: 
            if cmd == '' or cmd.startswith('#'): continue
            
            timestart, timeend, stdout, env = \
                self.execute(cmd, env, writer)
            
            writer.write(self.report(cmd, timestart, timeend, stdout))

    def execute(self, cmd, env, stderr_okay=False):
	"""Given bash cmd as string and bash environment,
	   Execute bash cmd and return output, updated env, and start/end time
	"""
        marker = "____BASHWRAPPER_SPLITONTHIS____"
        cmd = cmd.strip() + "; echo %s ; set" % marker

        timestart = datetime.datetime.now()
        shell = subprocess.Popen(cmd, 
                                 shell=True, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 env=env)
        result = shell.communicate()
        timeend = datetime.datetime.now()
        output = result[0].split(marker, 1)
        
        if not stderr_okay:
            if result[1] != '':
                if len(str(output[0])) > 50:
                    output[0]='%s...TRUNCATED' % str(
                        output[0][:50])
                msg2 =('\n---STDOUT:%s\n---STDERR:%s' % (
                        str(output[0])[:50], str(result[1]))) 
                raise Exception(msg2)

        env = self.split2dict(output[1])
        #hack:
        del env['SHELLOPTS']

        return (timestart, timeend, output[0], env)

    def report(self, cmd, timestart, timeend, stdout=''):
        """Return pretty print version"""
	if stdout:
            stdout = "STDOUT:\n%s" % stdout
        return  """
    =====================================
    CMD: %s
    TIME STARTED: %s
    TIME ENDED: %s
    =====================================
    %s""" % (cmd.strip(), 
             timestart,
             timeend,
             stdout) 
        
if __name__ == '__main__':
    a = BashWrapper()
    a.wrap(sys.argv[1])
    # a.wrap(sys.argv[1], writer=None) #for example
