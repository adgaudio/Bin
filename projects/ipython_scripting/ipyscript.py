#!/usr/bin/env python

"""A whole new style of python and bash scripting!
By wrapping your (python) scripts with this file,
you can take advantage of the ipython syntax and
its full feature set.  This means really good integration
with bash code, ability to use lazy syntax,
and things like accessing output history, directory history, etc"""

from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell


def execute(file_, verbose=0):
    """ Read and execute lines of code in given open file.
    Supports pure python or ipython-bash style syntax,
    multi-line code, and the IPython feature set
    """
    shell = TerminalInteractiveShell()

    c = shell.get_ipython()
    c.instance() # initialize ipython config

    raw_cell = file_.readlines()
    exception = None

    while raw_cell:
        # Extract smallest possible executable block of code from raw source
        is_completed = c.input_splitter.push(raw_cell.pop(0))
        while not is_completed:
            is_completed = c.input_splitter.push(raw_cell.pop(0))

        try:
            cell = c.input_splitter.source_reset()
            # Transform cell into syntactically correct python
            cell = c.prefilter_manager.prefilter_lines(cell) + '\n'
            # Compile to byte code
            code = compile(cell, 'cellname', 'exec')

            if verbose:
                print '========'
                print 'executing:', cell
                print '========'
            c.run_code(code)
        except Exception, e:
            raise
            import ipdb ; ipdb.set_trace()

if __name__ == '__main__':
    import sys
    file_ = open(sys.argv[1], 'r')
    execute(file_)
