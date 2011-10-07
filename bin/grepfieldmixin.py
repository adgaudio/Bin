
#factory
def make(inst, cls):
    """Given an instance and a class object,
    add methods from cls to the instance and
    return new instance with the added methods"""
    class X(inst.__class__, cls):
        pass
    # Rename class so it's clear we've added methods
    X.__name__ = '%s_%s' % (inst.__class__.__name__, cls.__name__)
    return X(inst)

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
        return self._grep(value, self, parent)

    def _grep(self, value, seq, parent):
        """Depth-first search for value in seq and nested-seqs
           Return flattened list of elements containing value.
           if parent=True, return parent seq containing value"""

        # Initialize return value
        rv = make([], GrepFieldMixin)

        for x in seq:
            match = False
            # Did we find an exact match?
            if value == x:
                if parent:
                    rv.append(seq)
                    break
                else:
                    rv.append(x)

            try: #continue if cannot perform these ops
                iter(x) ; value in x ; len(x)
            except: continue

            # Strings: now do we have a match?
            try:
                if value in x and isinstance(x, str):
                    match = True
                # Edge condition
                if len(x) == 1 and isinstance(x[0], str) and value in x[0]:
                    x = x[0]
                    match = True
            except: pass

            if match: #DUPLICATE CODE AS ABOVE!
                if parent:
                    rv.append(seq)
                    break
                else:
                    rv.append(x)
            # Recurse over relevant sub-seqs
            elif len(x) > 1:
                rv.extend(self._grep(value, x,  parent))
        return rv


if __name__ == '__main__':

    """Embarassingly ugly tests"""

    def testgrep():
        a = [1, 'hih', 'aaa', 'bbb', 'cab', 'dad', [1, 2, 'anested', [2, ['anothera', 5], 1], {'a':1, 4:'a'}], 4, [5, 1], 'aend']
        c = make(a, GrepFieldMixin)
        print 'input:', c
        d = True
        r1 = c.grep('a')  == ['aaa', 'cab', 'dad', 'anested', 'anothera', 'a', 'aend'] or c.grep('a')
        r2 = c.grep(2)    == [2, 2] or c.grep(2)
        r3 = c.grep(1)    == [1, 1, 1, 1] or c.grep(1)
        r4 = c.grep('ab') == ['cab'] or c.grep('ab')
        r5 = make([['c'], 1], GrepFieldMixin).grep('c') == ['c'] or  make([['c'], 1], GrepFieldMixin).grep('c')
        result = all(x == True for x in [r1, r2, r3, r4, r5])
        print 'passed test grep():', result
        if not result:
            print "failures:"
            print r1
            print r2
            print r3
            print r4
            print r5

    def testfields():
        a = (['col1', 'col2', 'col3'], [1, 2, 3], (1,2,3))
        c = make(a, GrepFieldMixin)
        print 'passed test fields():', c.fields(0,2) == [['col1', 'col3'], [1, 3], [1, 3]]
        c = make((lambda : 1, ['a', 'b']) + c + (1,), GrepFieldMixin)
        print 'passsed test anyfields():', c.anyfields(0, 2) == [['col1', 'col3'], [1, 3], [1, 3]]
        return c.anyfields(0, 2)
    def testcombined():
        a = make([[1,2,3], ['a','b','c'], ['A', 'B', 'C']], GrepFieldMixin)
        print 'pass test .fields().grep()', a.fields(0,1).grep('B') == ['B']
    testgrep()
    testfields()
    testcombined()
