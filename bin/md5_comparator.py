#!/bin/env python

import sys
import hashlib
DEBUG=False

class Md5Checker:
      def __init__(self, args):
            print 'Comparing these files: \n{0}\n----'.format(
                  '\n'.join(x for x in args))
                                    
            y = self.checksum(args[0])
            isequal = map(lambda x:x==y, 
                          (self.checksum(f) for f in args[1:]))
            
            if DEBUG: print isequal
            if all(isequal): print "Equal"
            else: print "Not equal"
            return
      
      def checksum(self, f):
            md5 = hashlib.md5()
            md5.update(open(f).read())
            return md5.hexdigest()

if __name__ == '__main__':
   a = Md5Checker(sys.argv[1:])

