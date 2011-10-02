#!/usr/bin/env python

"""A whole new style of python and bash scripting!
By wrapping your (python) scripts with this file,
you can take advantage of the ipython syntax and
its full feature set.  This means really good integration
with bash code, ability to use lazy syntax,
and things like accessing output history, directory history, etc"""

import sys
from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell


def execute():
    """supports pure python or ipython-bash style syntax.
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

