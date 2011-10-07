#!/usr/bin/env python

"""A whole new style of python and bash scripting!
By wrapping your (python) scripts with this file,
you can take advantage of the ipython syntax and
its full feature set.  This means really good integration
with bash code, ability to use lazy syntax,
and things like accessing output history, directory history, etc"""

from IPython.frontend.terminal.interactiveshell import TerminalInteractiveShell


def execute(file_, verbose = 0, stop_on_error = 1, store_history = 0):
    """ Read and execute lines of code in given open file.
    Supports pure python or ipython-bash style syntax,
    multi-line code, and the IPython feature set
    """
    shell = TerminalInteractiveShell()

    c = shell.get_ipython()
    c.instance() # initialize ipython config

    raw_cells = file_.readlines()
    exception = None

    while raw_cells:
        # Extract smallest possible executable block of code from raw source
        is_completed = c.input_splitter.push(raw_cells.pop(0))
        while not is_completed:
            is_completed = c.input_splitter.push(raw_cells.pop(0))

        cell, raw_cell = c.input_splitter.source_raw_reset()
        # Transform cell into syntactically correct python
        cell = c.prefilter_manager.prefilter_lines(cell) + '\n'

        # If we are storing script in/out history
        if store_history:
            c.history_manager.store_inputs(c.execution_count,
                                              cell, raw_cell)
        # Compile to byte code
        code = compile(cell, 'cellname', 'exec')
        if verbose:
            print '========'
            print 'executing:', cell
            print '========'
        outflag = c.run_code(code)

        if stop_on_error and outflag:
            c.exit()
            break

if __name__ == '__main__':
    import sys
    file_ = open(sys.argv[1], 'r')
    execute(file_)
