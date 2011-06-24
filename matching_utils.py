from collections import defaultdict
import os

HASHES = (
    lambda x:x,
    #lambda x:x.next()
    #lambda y:\
    #    str(sum(1 + len(x.attrib) for x in y.iter()) * \
    #            sum(1 for x in y.iter())) + \
    #    ''.join(self.extractID(x).split('-')[-1] for x in y),
    
    #lambda x: [str(x)+str(x.attrib) for x in x.iterancestors()],
    
    #lambda seq: [(x.tag,self.extractID(x).split('-')[-1]) for x in seq],
    
    #lambda seq: re.sub('(siegel)|(fwk)|(134226)|[-_]', '', self.extractID(seq))
    # +  ''.join(re.sub('(siegel)|(fwk)|(134226)|[-_]', '', self.extractID(seq.getparent())) for seq in [seq] if  seq.getparent() != None),
    )


class MatchError(Exception): pass

class Match:
    """A matching algorithm.  Given 2 iterable groups of objects and a hash function or ordered sequence of hash functions, 
    Find 1:1, 1:many, or many:many matches between elements (els) of seq1 and els of seq2 with same hash.

    Assumptions:
       Hashable: Elements have metadata, content, position or other measurable property by which they can be paired with member(s) of the other sequence
       Some els may not be matched with given hash function
        
    Uses:
        This class can be used when 1:1 matching of els can be defined by a comparison function, or hash function.  
        This was riginally intended as a tree comparison tool that matches a node in tree 1 with its counterpart in tree 2. Assuming a discrete group of nodes in each tree can be parameterized as a list, one can match els in list based on its position, content, or metadata in the tree.
        Another great use for this is as a state machine matcher, where the hash can define a sequence of states (based on timestep, for example) by matching the same sequence against itself.  This hash would could be as simple as a delay function that stores the value of the previous element
        This class can be extended to create an xml factory if you can identify desired ElementTree nodes.
    """
            
    def __init__(self, seq1, seq2, hashes=HASHES):
        """setup class vars and run"""
        #self.run(seq1, seq2, hashes)

    def run(self, seq1, seq2, hashes):
        """Given 2 sequences and tuple of hash functions,
        Use each hash in tuple to try to pair the elements in seq1 with element(s) in seq2.  After trying all given hashes, 
        Return dict of matches and remaining unmatched elements in seq1 and seq2, respectively.
        """
        matches = dict()
        for hash_ in hashes:
            print hash_
            #Run algorithm with given hash
            matches.update(
                self.oneToOneMatch(seq1, seq2, hash_)
                #self.oneToManyMatch(seq1, seq2, hash_)
                #self.manyToManyMatch(seq1, seq2, hash_)
                )
        
            #Find remaining children
            seq1, seq2 = \
                self.getUnmatched(seq1, seq2, matches)
        return matches, seq1, seq2 #seq1 or seq2 may be empty

    def manyToManyMatch(self, seq1, seq2, hash_):
        """yield element of seq1 if equivalent to el in seq2
        as determined by given hash"""

        class NestedList(list):
            def __init__(self):
                self.append([])
                self.append([])
        
        hashed = defaultdict(NestedList) #{hash_val:[[seq1_els], [seq2_els]]}
        for i,seq in enumerate((seq1, seq2)):
            for el in seq:
                hashed[hash_(el)][i].append(el)
        return hashed, hashed.values()
            
    def oneToOneMatch(self, seq1, seq2, hash_):
        """Given 2 sequences and hash function that identifies equivalence between elements in seq1 and seq2, respectively,
        Return dict of 1 to 1 matches. ie {seq1_el:seq2_el}
        """

        els = []
        hashed = []
        dup_indices = []
        
        for el1, el2, h in self.yieldEquivalents(seq1, seq2, hash_):
            els.append((el1, el2))
            hashed.append(h)
        for h in hashed:
            if hashed.count(h) > 1: #then find all equal hashes
                for i in range(len(hashed)): 
                    if hashed[i] == h:
                        dup_indices.append(h)
        for x in sorted(dup_indicies, reverse=True):
            els.pop(x)
        return dict(els)

    def oneToManyMatch(self, seq1, seq2, hash_):
        """Given 2 sequences and hash function that identifies equivalence between elements in seq 1 and seq2, respectively,
        Return dict of 1 to many matches. ie {seq1_el:[seq2_els...]}
        """
        matches = defaultdict(list) #{el1_seq1:[elx_seq2, ...]}
        for el1, el2, h in self.yieldEquivalents(seq1, seq2, hash_):
            matches[el1].append(el2)
        return matches
    
    def manyToManyMatch(self, seq1, seq2, hash_):
        """Given 2 sequences and hash function that defines equivalence between elements in seq1 and seq2,
        Return two groups of els with matching hash: {[seq1_els]:[seq2_els]}
        Will not match one to one, one to many, or many to one"""
        
        hashed = defaultdict(NestedList)

        #find elements of seq1 that share same hash
        for cx,x in enumerate(seq1):
            hx = hash_(x)
            i = len(seq1)
            while i > cx:
                if hx == hash_(seq1[i]):
                    hashed[hx][0].append(seq1[i])                
                i -= 1
        #find elements of seq2 that share same hash
        for x in seq2:
            hx = hash_(x)
            if hash(x) in hashed:
                hashed[hx][1].append(x)
        return dict(a.values)
                
    def getUnmatched(self, seq1, seq2, matchesdict):
        """Given 2 sequences and dict matching an element in seq1
        with one in seq2,
        Check that there is 1:1 matching between elements in seq1 and seq2
        Return unmatched elements in seq1 and seq2, respectively"""
        unmatched_seq1 = [x for x in seq1 
                          if x not in matchesdict]
        unmatched_seq2 = [x for x in seq2
                          if x not in matchesdict.values()]
        #check: algorithm didn't match one to many
        a = abs(len(unmatched_seq2) - len(unmatched_seq1))
        b = abs(len(seq2) - len(seq1))
        if a - b < 0:
            raise MatchError("There are not entirely 1:1 matches"
                                     " between seq1 and seq2")
        return unmatched_seq1, unmatched_seq2

    def swapKeyValue(self, dict1):
        dict2 = {}
        for k,v in dict1.items():
            if v not in dict2:
                dict2[v] = [k]
            else:
                dict2[v].append(k)
        return dict2

    def getHashes(self):
        """Return tuple of hash functions that create hash of an element.
        Assuming we are comparing 2 sequences, each hash function attempts to 
        define equivalence of an element in seq1 with an element in seq2."""
        return HASHES
    

DEBUG=0
def dprint(*msg):
    if DEBUG:
        print(''.join(msg))
if __name__ == '__main__':
    a = Match('I am an animal'.split(), 'I am not a dog'.split())
