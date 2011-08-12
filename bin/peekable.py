class peekable(object):
    """Makes an iterator peekable.  
    
    Adapted from http://code.activestate.com/recipes/499379-groupbysorted/

        Example usage:

        >>> n = peekable(range(7))
        >>> n.next()
        0
        >>> n.peek()
        1
        >>> n.peek(2)
        [2, 3]
        >>> n.peek()
        4
        >>> n.next()
        1
        >>> n.next(2)
        [2, 3]
        >>> n.next()
        4
        >>> for i in n:
        ...     print i
        ... 
        5
        6
        7
"""

    _None = [] # Watch out - this is mutable 

    def __init__(self, iterable):
        self._iterable = iter(iterable)
        self._buf = self._None[:] # caches result when peek is called
        self._pointer = -1 # index var that points to current peek position

    def __iter__(self):
        return self

    def _is_empty(self):
        return self._buf == self._None

    def peek(self, lookahead=1):
        """x.peek() -> get next value but don't increment iterator

        Raises StopIteration when peeking past end of iterable

        """
        self._pointer += lookahead

        for z in range(self._pointer + 1 - len(self._buf)):
            self._buf.append(self._iterable.next())
            
        if lookahead == 1:
            return self._buf[self._pointer]
        else:
            return self._buf[self._pointer+1 - lookahead:self._pointer+1]

    def next(self, lookahead=1):
        """x.next() -> the next value, or raise StopIteration"""
        def nnext():
            if self._is_empty():
                return self._iterable.next()
            ret = self._buf.pop(0)
            self._pointer = -1
            return ret

        if lookahead == 1:
            return nnext()
        else:
            return [nnext() for x in range(lookahead)]
        
    def buf(self):
        return self._buf


if __name__ == '__main__':
    def test():
        print 'n = peekable(range(10))'
        n = peekable(range(10))

        for x in range(3):
            print "n.next()"
            print n.next()
            print "n.peek()"
            print n.peek()
            print "n.peek(2)"
            print n.peek(2)
            print "n.peek()"
            print n.peek()
            print '        buf:', n._buf
            print 

        print 'n.next(2)'
        print n.next(2)
        print "peek()"
        print n.peek()

        print "for i in n"
        for i in n:
            print i

    test()
