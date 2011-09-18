#functions to add to a list, tuple, or similar sequence
def fields(cls, *cols):
    b = make([])
    for y in cls:
        b.append([])
        for x in cols:
            b[-1].append(y[x])
    return b

def grep(cls, value):
    def grepp(value, seq):
        """Depth-first search for value in seq and sub-seqs
           Return list of elements containing value"""
        b = make([])
        for x in seq:
            if value == x:
                b.append(x)
                continue
            try: #hack tests
                iter(x) ; value in x ; len(x)
            except: continue
            if value in x and isinstance(x, str):
                b.append(x) #don't iterate further over strings
            elif len(x) > 1:
                b.extend(grepp(value, x))
        return b
    return grepp(value, cls)

#factory
def make(seq):
    class X(seq.__class__):
        fields = fields
        grep = grep
        a = 1
    X.__name__ = 'extended_%s' % seq.__class__.__name__
    return X(seq)

if __name__ == '__main__':
    def testgrep():
        a = [1, 'hih', 'aaa', 'bbb', 'cab', 'dad', [1, 2, 'anested', [2, ['anothera', 5], 1], {'a':1, 4:'a'}], 4, [5, 1], 'aend']
        c = make(a)
        print 'input:', c
        d = True
        d = d and c.grep('a') == ['aaa', 'cab', 'dad', 'anested', 'anothera', 'a', 'aend']
        d = d and c.grep(2) == [2, 2]
        d = d and c.grep(1) == [1, 1, 1, 1]
        d = d and c.grep('ab') == ['cab']
        print 'passed greptest:', d

    def testfields():
        a = (['col1', 'col2', 'col3'], [1, 2, 3], (1,2,3))
        c = make(a)
        print 'passed fieldstest:', c.fields(0,2) == [['col1', 'col3'], [1, 3], [1, 3]]
    testgrep()
    testfields()
