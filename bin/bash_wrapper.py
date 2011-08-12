#!/usr/bin/env python

import subprocess
import sys, os
import datetime
import re

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
    
    def save(self, iterable):
        """Store contents of given iterable, such as a pipe or file"""
        result = []
        try:
            while True:
                result.append(next(iterable))
        except StopIteration:
            return result
    
    def strip_bash_func(self, iterable):
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


    def strip_comments(self, iterable):
        """Strip comments, #, from given lines of code"""
        result = []
        for l in iterable:
            if '#' not in l:
                result.append(l)
            if '#' not in self.strip_quotes(l):
                result.append(l)
            print 'HAS comment', l
        return result
    
    def strip_quotes(self, line):
        """remove content between quotes"""
        l = line[:]
        getCounts = lambda l:(l.count("'"),l.count('"'))
        def try_(code):
            try:
                return eval(code)
            except ValueError:
                return -1

        s,d = getCounts()
        if s > 0 or d > 0:
            #Get open and close of first quote
            di = try_('''l.index('"'')''')
            si = try_('''l.index("'")''')
            if di > si:
                openquote=di#double quote comes first
                closequote = try_('l.index(d,di + 1)')
            else:
                openquote = si#single quote comes first
                closequote = try_('l.index(s,si + 1)')
            l = l[:openquote] + l[closequote:]
        if sum(getCounts()) == 0:
            return l
        if closequote == -1:
            raise AttributeError("reached EOL before closing quote") #todo
        self.strip_quotes(l)


    def split2dict(self, vars, delimiter='='):
        """Given list of bash env vars and a delimiter, 
        parse values by delimeter and return dict"""
        d = {}
        vars, funcs = self.strip_bash_func(vars)

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
        return d
    
    def wrap(self, bashfile, writer=sys.stdout): 
        """Given filepath to bash script, execute commands and write output"""
        f = open(bashfile, 'r').readlines()
        env = os.environ.copy()

        # If no output wanted at all
        class NullOut: write=lambda *x:None
        if not writer:
            writer = NullOut()

        f = self.strip_comments(f)
        cmds, funcs = self.strip_bash_funcs(f)
        # Run commands
        for cmd in cmds: 
            cmd = cmd.strip()
            # Handle empty strings and comments
            if cmd == '' or cmd.startswith('#'): continue
            timestart, timeend, stdout, env = \
                self.execute(cmd, env, 1 if writer else 0)
            
            writer.write(self.report(cmd, timestart, timeend, stdout))

    def execute(self, cmd, env, stderr_okay=False):
        """Given bash cmd as string and bash environment,
        Execute bash cmd and return output, updated env, and start/end time
        """
        marker = "____BASHWRAPPER_SPLITONTHIS____"
        cmd = cmd + " ; echo %s ; set" % marker
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
        #hack:
        #del env['SHELLOPTS']
        print env
        print env.keys()
        return (timestart, timeend, stdout, env)

    def report(self, cmd, timestart, timeend, stdout=''):
        """Return pretty print version"""
        if stdout:
            stdout = "STDOUT:\n%s" % ''.join(stdout)
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
