#!/usr/bin/env python

"""A whole new style of bash scripting!
By wrapping your (python) scripts with this file,
you can take advantage of ipython syntax.
This means really good integration with bash code,
ability to use lazy syntax, and full ipython interactive
interpreter capabilities"""

import sys
#import __builtin__
#from IPython.core.interactiveshell import InteractiveShell #Base class of TerminalInteractiveShell
#from IPython.frontend.terminal.interactiveshell import *
from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell


def execute():
    """supports pure python or ipython-bash style syntax.

    BUG: to take advantage of ipython special/lazy syntax,
        you need to explicitly call it.
          ie. all bash cmds need to start with '!'
          ie. must explicitly call %autocall and other syntax-related magics
          /zip [1,2], [3,4]  ... NOT ... zip [1,2], [3,4]
    """

    shell = TerminalInteractiveShell()

    c = shell.get_ipython()
    c.instance() # initialize ipython config

    raw_cell = open(sys.argv[1], 'r').readlines()
    exception = None
    while raw_cell:
        is_completed = c.input_splitter.push(raw_cell.pop(0))
        while not is_completed:
            is_completed = c.input_splitter.push(raw_cell.pop(0))

        try:
            cell = c.input_splitter.source_reset()
            cell = c.prefilter_manager.prefilter_lines(cell) + '\n'
            code = compile(cell, 'cellname', 'exec')

            #print '========'
            #print 'executing:', cell
            #print '========'
            c.run_code(code)
        except Exception, e:
            raise
            import ipdb ; ipdb.set_trace()

execute()

