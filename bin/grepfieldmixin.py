from mixins import imake as make

class GrepFieldMixin(object):
    """additional methods for classes with __iter__,
    such as lists and tuples. modeled after IPython's SList.

    Dependency on make(instance, cls)
    """

    def fields(self, *indexes):
        """Return list containing given indexes in each nested sequence in iter(self)"""
        return self._fields(indexes)

    def anyfields(self, *indexes):
        """Return list containing given indexes in iter(self). Ignore errors
        when iterating over non-iterable or non-existent elements"""
        return self._fields(indexes, errors_ok=True)

    def _fields(self, indexes, errors_ok=False):
        """
        Given a tuple of indexes
        Return a 'return_type' containing given indexes of
        the nested seqs in iter(self).

        If errors_ok=True, ignores errors where self
        has asymmetric nested sequences or non-iterable elements.
        """
        # initialize return value with GrepFieldMixin
        rv = make([], GrepFieldMixin)

        # create subsequences containing given indexes
        for elem in self:
            sublist = make([], GrepFieldMixin)
            try:
                for i in indexes:
                    sublist.append(elem[i])
            except Exception, e:
                if errors_ok and \
                        (isinstance(e, TypeError) or isinstance(e, IndexError)):
                    continue
                raise
            #print 'sublist', sublist # debug

            rv.append(sublist)
        return rv

    def grep(self, value, parent=0):
        """Grep for value in self.
        if parent=True, return sequence value was found in"""
        return self._grep(value, self, parent)

    def _grep(self, value, seq, parent):
        """Depth-first search for value in seq and nested-seqs
           Return flattened list of elements containing value.
           if parent=True, return parent seq containing value"""

        # Initialize return value
        rv = make([], GrepFieldMixin)

        for x in seq:
            append = False
            recurse = True

            # Did we find an exact match?
            if value == x:
                append = True
            try:
                # Strings: is val in string?
                match = False
                if isinstance(x, str) and value in x:
                    append = True
                # Match on edge condition
                if len(x) == 1:
                    if isinstance(x, str) and value in x[0] or value == x[0]:
                        x = x[0]
                        append = True
                        recurse = False
            except Exception, e:
                pass # likely not iterable or 'value in x' not possible

            if append:
                if parent:
                    rv.append(seq)
                    break
                else:
                    rv.append(x)
                    continue

            # Recurse over relevant sub-seqs
            if hasattr(x, '__iter__') and recurse:
                rv.extend(self._grep(value, x,  parent))
        return rv


if __name__ == '__main__':

    def testgrep():
        """
        >>> a = make([['c'], [1]], GrepFieldMixin)
        >>> a.grep('c')
        ['c']
        >>> a.grep(1)
        [1]
        >>> a = [['a'], [[[1]]], 1, 'abc', (x for x in 'bab'), [1, 2, 'ab', [1, ['anothera', 5, 1], 1], {'akey':1, 1:'avalue'}], 'a']
        >>> a = make(a, GrepFieldMixin)
        >>> a.grep(1)
        [1, 1, 1, 1, 1, 1, 1]
        >>> a.grep('a')
        ['a', 'abc', 'ab', 'anothera', 'akey', 'a']
        >>>
        """
        pass #doctest

    def testfields():
        """
        >>> a = (['col1', 'col2', 'col3'], [1, [[2]], [{3:3}]], (1,2,3))
        >>> c = make(a, GrepFieldMixin)
        >>> c.fields(0,2)
        [['col1', 'col3'], [1, [{3: 3}]], [1, 3]]
        >>> c = make((lambda : 1, ['a', 'b']) + c + (1,), GrepFieldMixin)
        >>> c.anyfields(0, 2)
        [['col1', 'col3'], [1, [{3: 3}]], [1, 3]]
        >>>
        """
        pass #doctest

    def testcombined():
        """
        >>> a = make([[1,2,3], ['a','b','c'], ['A', 'B', 'C']], GrepFieldMixin)
        >>> a.fields(0,1).grep('B')
        ['B']
        """
    print "Running doctests"
    import doctest
    print doctest.testmod()

