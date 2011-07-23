#!/usr/bin/env python
import sys
import hashlib
from multiprocessing import Pool

def md5Checker(args):
      """Asynchronously calculate md5 sums on a list of elements"""
      pool = Pool()
      hashes = [pool.apply_async(checksum, [x]) for x in args]
      y = hashes[0].get()
      isequal = [x.get() == y for x in hashes]
      return isequal

def checksum(f):
      """Perform md5 using hashlib on given object"""
      md5 = hashlib.md5()
      md5.update(f)
      return md5.hexdigest()

def readfiles(args):
      """Given list of filepaths,
      return list of strings containing file content"""
      return [open(a).read() for a in args]

def prettyprint(results):
      """Given list of (name, value) tuples, 
      Show name if value equals first tuple"""
      results = results[1:]
      indexes = [n for n,x in enumerate(results) if x[1]==True]
      
      msg = '----\n{equal}{matches}\n----'
      if len(results) == len(indexes): 
            equal = "Equal:"
      else:
            if indexes:
                  equal = "Not Equal, but these match first argument:"
            else: 
                  equal = "Not Equal"
            
      matches='\n    ' + '\n    '.join(
            x[0] for n,x in enumerate(results) if n in indexes)
      msg = msg.format(equal=equal, matches=matches)
      print(msg)

if __name__ == '__main__':
      prettyprint(zip(sys.argv[1:],
                      md5Checker(readfiles(sys.argv[1:]))))
             
