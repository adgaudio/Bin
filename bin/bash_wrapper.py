#!/usr/bin/env python

#
# By: Alex D. Gaudio   --   www.alexgaudio.com
#

import subprocess
import sys, os
import datetime
import re
import shlex

from peekable import peekable

colors = {1: '\x1b[1;37m',
         2: '\x1b[1;36m',#light blue
         3: '\x1b[1;34m',
         51: '\x1b[1;33m',
         52: '\x1b[0;31m',#red
         53: '\x1b[1;31m',#red bold
         257: '\x1b[1;32m',
         258: '\x1b[1;33m',
         '__allownew': True,
         'normal': '\x1b[0m'}


class BashWrapper(object):
    """Wrap a simple bash script to provide:
           1. Workflow: If you want, stop execution if stderr is returned
           2. Logging: Specify an object with a write method 
              (like sys.stdout, or an open file)
           3. Pretty print resulting output

        Gotchas:
            1. script can't have code blocks (if, for, while, etc), 
               but it can use variables.  A work-around until this gets 
               fixed would be to call a separate file containing the function
               from the main bash script.

            2. The readonly bash env vars, like SHELLOPTS, cannot be changed, 
               and the value of SHELLOPTS is set at BashWrapper runtime.
               This "feature/problem" of the subprocess module means the "set" 
               cmd won't be effectiv.  
               NOTE: you can use the "set" cmd in scripts the bash script calls
    """
    def __init__(self):
        pass
    
    def wrap(self, bashfile, writer=sys.stdout, stderr_okay=False): 
        """Given filepath to bash script, execute commands and write output.
        stderr_okay determines whether to raise exception on stderr"""
        f = open(bashfile, 'r').readlines()
        env = os.environ.copy()

        # If no output wanted at all
        class NullOut: 
            write=lambda *x:None
            close=lambda *x:None
        if not writer:
            writer = NullOut()

        # Run commands
        for cmd in self.parseFile(f):
            # Handle empty strings and comments
            if cmd == '': continue
            timestart, timeend, stdout, env = \
                    self.execute(cmd, env, stderr_okay)
            writer.write(self.report(cmd, timestart, timeend, stdout))
        if writer!=sys.stdout:
            writer.close()

    def execute(self, cmd, env, stderr_okay=False):
        """Given bash cmd as string and bash environment,
        Execute bash cmd and return output, updated env, and start/end time
        """
        marker = "____BASHWRAPPER_SPLITONTHIS____"
        cmd += " ; echo %s ; set" % (marker)
        timestart = datetime.datetime.now()
        shell = subprocess.Popen(cmd,
                                 shell=True, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 env=env)
        stdout = self.save(shell.stdout)
        stderr = self.save(shell.stderr)
        timeend = datetime.datetime.now()

        # Manage workflow: fail if stderr_ok == False
        if not stderr_okay and stderr != []:
            stdout = ''.join(stdout)
            if len(stdout) > 60:
                stdout = (stdout[:60] + "...TRUNCATED") 
            msg2 =('\n---CMD:%s\n---STDOUT:%s\n---STDERR:%s' % (
                cmd, stdout, ''.join(stderr)))
            raise Exception(msg2)

        i = stdout.index(marker+'\n')
        env_ = stdout[i+1:]
        stdout = stdout[:i]
        env = self.split2dict(env_)
        #hack
        try:
            del env['SHELLOPTS'] # shellopts is readonly bash var
        except KeyError:
            pass
        return (timestart, timeend, stdout, env)

    def report(self, cmd, timestart, timeend, stdout):
        """Return pretty print version"""
        if stdout:
            stdout = "STDOUT:\n%s" % ''.join(stdout)
        else: stdout = "<no stdout>"
        return  """
    %s=====================================
    CMD: %s
    TIME STARTED: %s
    TIME ENDED: %s
    =====================================
    %s%s
""" % (colors[2], cmd,
             timestart,
             timeend, colors['normal'],
             stdout) 
        

    ######
    #UTIL FUNCTIONS
    ######
    def parseFile(self, f, get_funcs=False):
        cmds, funcs = self.strip_bash_funcs(f)
        g = []
        # Strip comments using shlex
        f_ = iter(f)
        for cmd in f_: 
            lex = shlex.shlex(cmd)
            # hacks: shlex does weird things with quotations and variables
            lex.wordchars = "$ " + lex.wordchars
            lex.whitespace = '\t\r\n'
            try:
                cmd = list(lex)
            except ValueError, e:
                if e.message == 'No closing quotation':
                    try:
                        cmd = cmd + f_.next()
                        cmd = list(shlex.shlex(cmd))
                    except ValueError or StopIteration:
                        pass # don't use shlex when it fails
                else: 
                    raise
            g.append(''.join(cmd))
        if get_funcs:
            return g, funcs
        else:
            return g

    def save(self, iterable):
        """Store contents of given iterable, such as a pipe or file"""
        result = []
        try:
            while True:
                result.append(next(iterable))
        except StopIteration:
            return result
    
    def split2dict(self, vars, delimiter='='):
        """Given list of bash env vars and a delimiter, 
        parse values by delimeter and return dict"""
        d = {}
        #vars, funcs = self.parseFile(vars, get_funcs=True) # todo: bugfix: use parseFile like this to take care of multiline env vars
        vars, funcs = self.strip_bash_funcs(vars)
        for pair in vars:
            pair = pair.strip()
            # hacks
            if pair == '':     continue
            if delimiter not in pair:
                print '%sBashWrapper WARNING: skipping env variable:%s' % (colors[53], pair)
                continue

            k,v = pair.split(delimiter, 1)
            # subprocess escapes quotes unnecessarily
            v = re.sub(r'''['"](.*?)["']''', r'\1' ,v)
            d[k] = v
        return d
    
    def strip_bash_funcs(self, iterable):
        """Strip bash functions from given lines of bash code
        Return a list with no functions a 2nd list of the missing functions"""
        it = []
        funcs = []
        peek = peekable(iterable)
        for elt in peek:
            if '()' in elt and (elt.strip().endswith('{') or 
                        peek.peek().strip().startswith('{')):
                funcs.append([])
                while '}' not in elt:
                    elt = elt.next()
                    funcs[-1].append(elt)
            it.append(elt)
        return it, funcs

if __name__ == '__main__':  
    import argparse
    
    parser = argparse.ArgumentParser(
            description='Wraps a bash script in python to provide '
                        'workflow, logging, and formatted output')
    parser.add_argument('filename', action="store")
    parser.add_argument('log_file', action="store", nargs="?", default=sys.stdout)
    c = parser.parse_args(sys.argv[1:])

    if c.log_file != sys.stdout:
        c.log_file = open(c.log_file,'w')
    a = BashWrapper()
    a.wrap(c.filename, c.log_file)
    # a.wrap(sys.argv[1], writer=None) #for example
