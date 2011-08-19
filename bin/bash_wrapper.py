#)!/usr/bin/env python

import subprocess
import sys, os
import datetime
import re
import shlex

from peekable import peekable

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
    
    def wrap(self, bashfile, writer=sys.stdout): 
        """Given filepath to bash script, execute commands and write output"""
        f = open(bashfile, 'r').readlines()
        env = os.environ.copy()

        # If no output wanted at all
        class NullOut: write=lambda *x:None
        if not writer:
            writer = NullOut()

        # Run commands
        for cmd,cmd2 in zip(self.parseFile(f), f):
            # Handle empty strings and comments
            if cmd == '': continue
            timestart, timeend, stdout, env = \
                    self.execute(cmd, env, 1 if writer else 0)
            writer.write(self.report(cmd2, timestart, timeend, stdout))

    def execute(self, cmd, env, stderr_okay=False):
        """Given bash cmd as string and bash environment,
        Execute bash cmd and return output, updated env, and start/end time
        """
        marker = "____BASHWRAPPER_SPLITONTHIS____"
        cmd += " ; echo %s ; set" % marker
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
        i = stdout.index(marker+'\n')
        env_ = stdout[i+1:]
        stdout = stdout[:i]

        if not stderr_okay and stderr != []:
            stdout = ''.join(stdout)
            if len(stdout) > 60:
                stdout = (stdout[:60] + "...TRUNCATED") 
            msg2 =('\n---CMD:%s\n---STDOUT:%s\n---STDERR:%s' % (
                cmd, stdout, ''.join(stderr)))
            raise Exception(msg2)

        env = self.split2dict(env_)
        return (timestart, timeend, stdout, env)

    def report(self, cmd, timestart, timeend, stdout=''):
        """Return pretty print version"""
        if stdout:
            stdout = "STDOUT:\n%s" % ''.join(stdout)
        
        colors = {1: '\x1b[1;37m',
         2: '\x1b[1;36m',
         3: '\x1b[1;34m',
         51: '\x1b[1;33m',
         52: '\x1b[0;31m',
         53: '\x1b[1;31m',
         257: '\x1b[1;32m',
         258: '\x1b[1;33m',
         '__allownew': True,
         'normal': '\x1b[0m'}

        return  """
    %s=====================================
    CMD: %s
    TIME STARTED: %s
    TIME ENDED: %s
    =====================================
    %s%s""" % (colors[2], cmd,
             timestart,
             timeend, colors['normal'],
             stdout) 
        

    ######
    #UTIL FUNCTIONS
    ######
    def parseFile(self, f, get_funcs=False):
        cmds, funcs = self.strip_bash_funcs(f)
        g = []
        f_ = iter(f)
        for cmd in f_: 
            print cmd
            lex = shlex.shlex(cmd)
            lex.wordchars = "$ " + lex.wordchars
            lex.whitespace = '\t\r\n'
            try:
                cmd = list(lex)
            except ValueError, e:
                print 'raising'
                import pdb ; pdb.set_trace()
                if e.message == 'No closing quotation':
                    cmd = cmd + f_.next()
                    cmd = list(shlex.shlex(cmd))
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
        vars_, funcs = self.parseFile(vars, get_funcs=True)

        vars, funcs = self.strip_bash_funcs(vars)

        for pair in vars:
            pair = pair.strip()
            # hacks
            if pair == '':     continue
            if delimiter not in pair:
                print 'WARNING: skipping env variable:', pair
                continue

            k,v = pair.split(delimiter, 1)
            # subprocess escapes quotes unnecessarily
            v = re.sub(r'''['"](.*?)["']''', r'\1' ,v)
            d[k] = v
        import pdb ; pdb.set_trace()
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
    a = BashWrapper()
    a.wrap(sys.argv[1])
    # a.wrap(sys.argv[1], writer=None) #for example
