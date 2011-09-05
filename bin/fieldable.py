class SequenceFactory(object):
    def __init__(self):
        self.seq = None

    def make(self, seq):
        self.seq = seq
        class X(self.seq.__class__):
            fields = self.fields
            grep = self.grep
        X.__name__ = 'extended_%s' % self.seq.__class__.__name__
        return X(self.seq)

    def fields(self, *cols):
        b = SequenceFactory().make([])
        for y in self.seq:
            b.append([])
            for x in cols:
                b[-1].append(y[x])
        return b

    def grep(self, value):
        def grepp(value, seq):
            """Depth-first search for value in seq and sub-seqs
               Return list of elements containing value"""
            b = SequenceFactory().make([])
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
        return grepp(value, self.seq)

if __name__ == '__main__':
    def testgrep():
        a = [1, 'hih', 'aaa', 'bbb', 'cab', 'dad', [1, 2, 'anested', [2, ['anothera', 5], 1], {'a':1, 4:'a'}], 4, [5, 1], 'aend']
        c = SequenceFactory().make(a)
        print c
        d = True
        d = d and c.grep('a') == ['aaa', 'cab', 'dad', 'anested', 'anothera', 'a', 'aend']
        d = d and c.grep(2) == [2, 2]
        d = d and c.grep(1) == [1, 1, 1, 1]
        d = d and c.grep('ab') == ['cab']
        print c.grep('ab')
        print 'passed greptest:', d

    def testfields():
        a = (['col1', 'col2', 'col3'], [1, 2, 3], (1,2,3))
        c = SequenceFactory().make(a)
        print 'passed fieldstest:', c.fields(0,2) == [['col1', 'col3'], [1, 3], [1, 3]]
    testgrep()
    testfields()
