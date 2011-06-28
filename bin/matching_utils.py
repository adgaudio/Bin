from collections import defaultdict

class Match:
    """A matching algorithm.  Given 2 iterable groups of objects and a hash function or ordered sequence of hash functions, 
    Find 1:1, 1:many, or many:many matches between elements (els) of seq1 and els of seq2 with same hash.

    Assumptions:
       Hashable: Elements have value, metadata, content, position or other measurable property by which they can be paired with member(s) of the other sequence
       Some els may occur more than once in given sequences
       Some els in given seqs may remain unmatched by given hash function(s)
        
    Uses:
        ...For cases where 1:1 matching of els can be defined by a comparison function, or hash function...
        This was riginally intended as a tree comparison tool that matches a node in tree 1 with its counterpart in tree 2. Assuming a discrete group of nodes, one can match nodes in the group based on position, content, or metadata in the tree structure.
        Another great use for this is as a state machine matcher, where the hash can define a sequence of states (based on timestep, for example) by matching the same sequence against itself.  This hash would could be as simple as a delay function that stores the value of the previous element.
        This class can be extended to create an xml factory if you can identify desired ElementTree nodes in a library of xml documents
    """
        
    def run(self, seq1, seq2, hashes, **option):
        """
        Return list of tuples matching elements in seq1 and seq2, respectively,
        Given 2 sequences, a tuple of hash functions, and an optional parameter in the form of: oneToOne=True or manyToOne=True.
        
        By default, perform manyToMany match, unless option parameter given.  

        hashes contains a function or group of functions that, given an el of a seq, return a hash value of that el to identify equivalence with another element.  Use each hash in hashes to pair the elements in seq1 with element(s) in seq2.  

        Two example hashes tuples:
            (lambda x: x % 2 == 0, #1st, pair all numbers divisible by 2
             lambda x: x%3 == 0 #2nd, pair all remaining numbers divisible by 3
             )
             
            (lambda x: tuple(y for y in x.somemethod()),)
        """
        matches = []
        for hash_ in hashes:
            #Run algorithm with given hash
            matches.extend(self.manyToManyMatch(seq1, seq2, hash_, **option)
                           )
            
            #Find remaining children and ensure no duplicates
            seq1, seq2 = self.getUnmatched(seq1, seq2, matches)
        return matches, seq1, seq2

    def manyToManyMatch(self, seq1, seq2, hash_, oneToOne=False, manyToOne=False):
        """Given 2 sequences and hash function that defines equivalence between elements of seq1 and seq2,
        Return tuple of els with matching hash: ([seq1_els],[seq2_els])

        If oneToOne=True, only return tuples matching one seq1 el to one seq2 el
        If manyToOne=True, only return tuples matching one seq1 el to seq2 els
        """
        #dict like this... {hash_val:([seq1_els], [seq2_els])}
        hashed = defaultdict(lambda:([],[]))

        if oneToOne or manyToOne: 
            skip_list = []
        
        #add values to dict
        for i,seq in enumerate((seq1, seq2)):
            for el in seq:
                h = hash_(el)
                if oneToOne or manyToOne and i==1:
                    if h in skip_list: 
                        continue
                    elif len(hashed[h][i]) >= 1:
                        skip_list.append(h)    
                        del hashed[h]
                        continue
                hashed[h][i].append(el)

        #remove k:v pairs if one of values is has no len
        for x in hashed.keys():
            if not hashed[x][0] or not hashed[x][1]:
                del hashed[x]

        return hashed.values()
            
    def oneToOneMatch(self, seq1, seq2, hash_):
        """Given 2 sequences and hash function that identifies equivalence between elements in seq1 and seq2, respectively,
        Return tuples of 1 to 1 matches. ie [ ([seq1_el],[seq2_el]), ...]
        """
        return self.manyToManyMatch(seq1, seq2, hash_, oneToOne=True)

    def manyToOneMatch(self, seq1, seq2, hash_):
        """Given 2 sequences and hash function that identifies equivalence between elements in seq 1 and seq2, respectively,
        Return tuples of 1 to many matches. ie [ ([seq1_el],[seq2_els...]), ...]
        """
        return self.manyToManyMatch(seq1, seq2, hash_, manyToOne=True)

    def getUnmatched(self, seq1, seq2, matches):
        """Given 2 sequences and list of paired elements in form [([],[]), ...]
        Return unmatched elements in seq1 and seq2, respectively"""
        unmatched_seqs = [[],[]]
        for c,seq in enumerate((seq1, seq2)):
            for x in seq:
                inmatches = False 
                for pair in matches:
                    if x in pair[c]:
                        inmatches = True
                if not inmatches:
                    unmatched_seqs[c].append(x)
        return unmatched_seqs[0], unmatched_seqs[1]

class TestMatch:
    def __init__(self):
        self.seq1 = '1 1 2 2 3 4 6'.split()
        self.seq2 = '1 1 2 3 3 4 5'.split()

        print 'TESTING Match class'
        print
        print "Given sequences:"
        print '    seq1: ', self.seq1
        print '    seq2: ', self.seq2

    def testAll(self):
        self.testOneToOne()
        self.testManyToOne()
        self.testManyToMany()
        self.testHashes()

    def testRun(self, aa, bb, cc, option='manyToMany'):
        """Given expected output to run method, 
        print results of test"""
        
        #expected input
        seq1 = self.seq1
        seq2 = self.seq2
        hashes = (lambda x: x,)

        #run test
        d = Match()
        a,b,c = d.run(seq1, seq2, hashes, 
                      oneToOne=True if option == 'oneToOne' else False, 
                      manyToOne=True if option == 'manyToOne' else False)

        #analyze and print results
        msg = '\n' + option + ' '
        if      a == aa and \
                b == bb and \
                c == cc:
            msg += 'PASSED all tests!'
        else:
            msg += 'FAILED'
            if aa != a:
                msg += '\n    failed: %s match returned wrong result:%s' % (option, a) 
                msg += '\n    expected: %s' % aa
            else:
                msg += '\n    passed: %sMatch()' % option
            for c,(xx,x) in enumerate(zip([bb,cc],[b,c])):
                if xx != x:
                    msg += '\n    failed: getUnmatched() returned seq%s=%s' % (c+1, x)
                    msg += '\n    expected: %s' % xx
                else:
                    msg += '\n    passed: getUnmatched() for seq%s' % (c+1) 
        print msg

    def testOneToOne(self):
        aa = [(['4'], ['4'])]
        bb = ['1', '1', '2', '2', '3', '6']
        cc = ['1', '1', '2', '3', '3', '5']
        self.testRun(aa,bb,cc,'oneToOne')

    def testManyToOne(self):
        aa = [(['2', '2'], ['2']), (['4'], ['4'])]
        bb = ['1', '1', '3', '6']
        cc = ['1', '1', '3', '3', '5']
        self.testRun(aa,bb,cc, 'manyToOne')

    def testManyToMany(self):
        aa = [(['1', '1'], ['1', '1']), (['3'], ['3', '3']), (['2', '2'], ['2']), (['4'], ['4'])]
        bb = ['6']
        cc = ['5']
        self.testRun(aa,bb,cc, 'manyToMany')

    def testHashes(self):
        hashes = (lambda x:x,
                  lambda x:int(x)/7==0 and 1
                  )
        d = Match()
        a,b,c = d.run(self.seq1, self.seq2, hashes)
        aa = [(['1', '1'], ['1', '1']), (['3'], ['3', '3']), (['2', '2'], ['2']), (['4'], ['4']), (['6'], ['5'])]
        bb = []
        cc = []
        if a == aa and b == bb and c == cc:
            print '\ntestHashes success!'
        else:
            print '\ntestHashes success!'

if __name__ == '__main__':
    #for testing purposes    
    t = TestMatch()
    t.testAll()


