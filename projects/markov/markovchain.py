#!/usr/bin/env python
import random
DEBUG=0
class MarkovChain:
    """Generates Markov Chain given list of input files input(s)."""
    def run(self, fp, lookback, result_size):
        """Generates Markov Chain given list of input files input(s), 
        , num elements to look back on, and num elements to output."""
        #seq = self.readFile(fp)
        seq = self.readFileForChars(fp)
        seq = seq[0:len(seq) - len(seq) % lookback + 1]
        if DEBUG: self.seq = seq
        
        return self.run2(seq, lookback, result_size)
        
    def run2(self, seq, lookback, result_size, seed=None):
        """Generates Markov Chain given iterable sequence, 
        num elements to look back, num elements to output, and seed (tuple)
        Return list of randomly generated output"""
        mapping = self.makeChain(seq, lookback)
        if not seed:
            seed = tuple(seq[x] for x in range(lookback))
        result = self.gen(mapping, seed, lookback, result_size)
        return result
        
    def readFile(self, paths):
        """Given list of filepath(s), return list of all words in file(s)"""
        words = []
        for fp in paths:
            f = open(fp, 'r')
            words.extend(f.read().replace('\n',' ').split())
            f.close()
            return words

    def readFileForChars(self, paths):
        """Given list of filepath(s), return list of all chars in file(s)"""
        chars = []
        for fp in paths:
            f = open(fp, 'r')
            chars.extend([x for x in f.read()])
            f.close()
        return chars
        
    def makeChain(self, seq, lookback):
        """Given a sequence and an int.
        Return Markov Chain as a dictionary  
        
        EX:  
        assuming seq = [1,2,3,4,2,3,99] and lookback = 2,
        make dict, { (None,1):2, (1,2):[3], (2,3):[4,99], ... }
        """
        mapping = {}
        i = -1 * lookback 
        while i < len(seq) -lookback - 1:
            #create key and value for dict
            i += 1
            if i <= 0: 
                ii = 0
                key = (None,)*abs(i)
            else: 
                ii = i
                key = ()
            key += tuple(seq[ii:i+lookback + 1],) # the +1 is the v in {k:v}
                
            if DEBUG:
                if len(key) - 1 != lookback:
                    raise Exception("bad key length: %s" % key)

            #add key:value to mapping
            try:
                mapping[ key[0:-1] ].append(key[-1])
            except KeyError:
                mapping[ key[0:-1] ] = [key[-1]]
        return mapping

    def gen(self, mapping, seed, lookback, size):
        """Given dict  (tuple):[list] elements, 
           a seed (key in dict), 
           and a desired output size
        Return list of random elements
        """
        key = seed
        result = [x for x in key]
        i=0
        while i < size:
            el2 = self.findNext(key[i:i+lookback], mapping)
            key += (el2,)
            i += 1
            result.append(el2)
        return result

    def findNext(self, key, mapping):
        """Given a tuple (aka key) and dict where keys are tuples,
        Choose dict value by matching given key with closest key in mapping.
        ie. if key = (1,2,3,4) not in mapping, 
            then set each key = key[1:] and try matching again
        """
        i = -1
        keys = []
        while len(keys) == 0 and i < len(key) - 1:
            i += 1
            keys = [x for x in mapping.keys() if x[i:] == key[i:]]
            if DEBUG:
                if len(x[i:]) != len(key[i:]):
                    import pdb ; pdb.set_trace()
                if len(keys) == 0:
                    print "Didn't find matching key for ", key[i:], 'i=', i
        if DEBUG:
            print 'key', key[i:]
            print 'keys', len(keys), keys
            
        if keys == []:
            key = random.choice(mapping.keys())
            if DEBUG:
                if key[-1] == self.seq[-1]:
                    print "Last element in sequence doesn't have anything that typically comes after it.  You should use a larger input file"
                else:
                    raise Exception('Bug: Created key not in in mapping! %s' % key)
        else:
            key = keys[random.randint(0, len(keys)-1)]                
        el = random.choice(mapping[key])
        return el
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Creates Markov Chain for a sequence of space separated data in given text file")
    parser.add_argument('filepaths',
                        help="Space separated list of filepath(s) containing text file of space separated data",                     
                        nargs='+',
                        )
    parser.add_argument('--lookback', '-l', 
                        help="Given seq [1,2,3,4], defines how long to chain elements will be.  ie If lookback=2, makes {(1,2):3, (2,3):4}. If lookback=1, makes {(1,):2, (2,):3, ...}",
                        type=int,
                        default=3
                        )
    parser.add_argument('--size', '-s',
                        help="Given int, return that number of elements created by Markov Chain generator",
                        type=int,
                        default=50
                        )
                        
    args = parser.parse_args()
    a = MarkovChain().run(args.filepaths, args.lookback, args.size)
    print ''.join(a)
