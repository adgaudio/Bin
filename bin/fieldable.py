class fieldablefactory(object):
    def __init__(self, sequence):
        self.seq = sequence
        self = sequence

    def make(self):
        class fieldable(self.seq.__class__):
            fields = self.fields
            grep = self.grep
        return fieldable(self.seq)

    def fields(self, *cols):
        b = []
        for y in self.seq:
            b.append([])
            for x in cols:
                b[-1].append(y[x])
        return b

    def grep(self, value, seq=self.seq):
        b = []
        for x in seq:
            if value in x:
                b.append(x)
            else:
                try:
                    self.grep(value,x)
                except Exception, e:
                    print e, value, x


a = ['hih', 'aaa', 'bbb', 'cccc', 'ddd']
b = fieldablefactory(a)
c = b.make()
print c

