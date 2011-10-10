#!/usr/bin/env python
import random
DEBUG=0
class MarkovChain:
    """Generates Markov Chain given list of input files input(s)."""

    def run(self, fps, lookback, result_size, seed=None):
        """Implements a Markov Chain.

        Given list of filepaths with input data,
        num elements to look back, num elements to output,
        and optionally, a tuple with a start value

        Return list of randomly generated output"""

        seq = self.makeseq(fps, lookback, result_size)
        mapping = self.makeChain(seq, lookback)
        if not seed:
            seed = tuple(seq[x] for x in range(lookback))
        result = self.gen(mapping, seed, lookback, result_size)
        return result

    def makeseq(self, fps, lookback, result_size):
        """Parse data from given filepath(s),
        Return corresponding sequence.  """

        #seq = self.readFile(fp)
        seq = self.readFilesForChars(fps)

        # Trim last few elems of seq.
        #seq = seq[0:len(seq) - (len(seq) % lookback) + 1]

        if DEBUG: self.seq = seq
        return seq

    def readFile(self, paths):
        """Given list of filepath(s), return list of all words in file(s)"""
        words = []
        for fp in paths:
            f = open(fp, 'r')
            words.extend(f.read().replace('\n',' ').split())
            f.close()
            return words

    def readFilesForChars(self, paths):
        """Given list of filepath(s), return list of all chars in file(s)
        as a continuous stream."""
        chars = []
        for fp in paths:
            f = open(fp, 'r')
            chars.extend([x for x in f.read()])
            f.close()
        return chars

    def makeChain(self, seq, lookback):
        """Given a sequence and an int
        Return Markov Chain key:value representation

        EX:
        assuming seq = [1,2,3,4,2,3,99] and lookback = 2,
        make dict, { (None,1):2, (1,2):[3], (2,3):[4,99], ... }
        """

        mapping = {}
        i = -1 * lookback
        while i < len(seq) - lookback:
            #Create key and value for dict
            if i < 0:
                # Pre-populate key with None as necessary.
                # could also just start at i=0, but this way helps gen()
                ii = 0
                key = (None,)*abs(i)
            else:
                ii = i
                key = ()

            key += tuple(seq[ii:i+lookback])
            value = seq[i + lookback]

            if DEBUG:
                if len(key) != lookback:
                    raise Exception("bad key length: %s" % key)

            #add key:value to mapping
            try:
                mapping[key].append(value)
            except KeyError:
                mapping[key] = [value]
            i += 1
        return mapping

    def gen(self, mapping, seed, lookback, size, gaurantee_size=0):
        """Given dict  (tuple):[list] elements, a seed (key in dict),
        and a desired output size
        Return list of random elements

           Note: Size returned may be less than requested if the end-sequence
           is not in the mapping.
           Chance of hitting an end sequence increases with larger lookback.
        """
        key = seed
        result = [x for x in key]
        i=-1
        while i < size:
            i += 1
            if gaurantee_size:
                value = self.findNextAlways(key, mapping)
            else:
                value = self.findNext(key, mapping)
            result.append(value)
            key = key[1:] + (value,)
        return result

    def findNext(self, key, mapping):
        """Given a key (tuple) and mapping (dict where keys are tuples),
        Choose a value for given key.  Return None if key not in mapping
        """
        try:
            possiblevals = mapping[key]
        except KeyError:
            # generated key not in mapping because
            # we've reached the end-sequence and this end-sequence is unique
            # in the source
            return None
        return random.choice(possiblevals)

    def findNextAlways(self, key, mapping):
        """Given a key and mapping, return value for given key
        If key not in dict, reduce lookback (ie key length) and try again.

        ie. if key = (1,2,3,4) not in mapping,
            then set each key = key[1:] and try matching again
        """
        i = -1
        keys= []
        while len(keys) == 0 and i < len(key) - 1:
            i += 1
            keys = [x for x in mapping.keys() if x[i:] == key[i:]]

        key = random.choice(keys)
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
    a = MarkovChain()
    b = a.run(args.filepaths, args.lookback, args.size)
    print ''.join(b)
