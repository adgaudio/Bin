import appcontext
import os
from utils import rev_copy
from copy import deepcopy
from lxml import etree
import re

class MatchError(Exception): pass
class ElemLengthError(MatchError): pass
class UnexpectedElementIDError(MatchError): pass

class Match:
    """A matching algorithm.  Given 2 iterable groups of objects and a hash function or ordered sequence of hash functions, 
    Get 1:1 (or 1:many???) matches between elements (els) of seq1 and els of seq2 that share the same hash.

    Assumptions:
       Hashable: Elements have metadata, content or calculable position by which they can be paired with a member(s) of other sequence
       Some els may not be matchable with given function
        
    Uses:
        This class can be used when 1:1 matching of els can be defined by a comparison function, or hash function.  It is probably a good base-class.
        This class was originally intended as a tree comparison tool that matches a node in tree 1 with its counterpart in tree 2. Assuming a discrete group of nodes in each tree can be parameterized as a list, one can match els in list based on its position, content, or metadata in the tree.
        This class can be extended to create an xml factory if you can identify desired ElementTree nodes.
    """

    def getHashes(self):
        """Return tuple of hash functions that create hash of an element.
        Assuming we are comparing 2 sequences, this is meant to match
        an element in seq1 with an element in seq2."""
        return (
            #lambda y:\
            #    str(sum(1 + len(x.attrib) for x in y.iter()) * \
            #            sum(1 for x in y.iter())) + \
            #    ''.join(self.extractID(x).split('-')[-1] for x in y),
            
            #lambda x: [str(x)+str(x.attrib) for x in x.iterancestors()],
            
            #lambda seq: [(x.tag,self.extractID(x).split('-')[-1]) for x in seq],
            
            lambda seq: re.sub('(siegel)|(fwk)|(134226)|[-_]', '', self.extractID(seq))
            # +  ''.join(re.sub('(siegel)|(fwk)|(134226)|[-_]', '', self.extractID(seq.getparent())) for seq in [seq] if  seq.getparent() != None),
            )
            
    def __init__(self, *hashes=None):
        """setup class vars and run"""
        self.unmatched_seq1_els = [] 
        self.unmatched_seq2_els = []
        
        if hashes == None:
            hashes = self.getHashes()
            
        seq1 = 
        seq2 = 
        self.run(hashes)

    def run(self):
        """merge docbook_p back into docbook
        1. Parse docbook xml
        2. Match each el in each docbook with a el in the other docbook
        3. Test Results
        """
        #convert tree into linear list of els
        seq1 = [x for x in el1.iter()]
        seq2 = [x for x in el2.iter()]
        
        #match, replace ids, save docbook, test resulting xml
        matches = self.matchEls(seq1, seq2, hashes)

        #debug - test hash
        #print
        #print [(hash_4(x),self.extractID(x)) for x in self.unmatched_seq1_els]
        #print
        #print [(hash_4(x),self.extractID(x)) for x in self.unmatched_seq2_els]
        
        el2 = self.replaceIDs(el2, matches)
        if len(self.unmatched_seq2_els) == 0:
            self.saveDocbookAndTest(el2)
        else:
            print "You need to fix the following els in book %s manually:" %\
                self.book_name
            print
        return

    def parseDocbooks(self):
        """parse xml docbooks given by filenames in 
           self.docbook_orig and self.docbook_merged.
           Return 2 etrees"""
        parser = etree.XMLParser(remove_comments=True)
        orig = etree.parse(self.docbook_orig, parser)
        merged = etree.parse(self.docbook_merged, parser)

        el1 = orig.getroot()
        el2 = merged.getroot()

        # post-parsing:
        # remove els where both el and all descendants have no xml:id
        for x in [el1, el2]:
            x = self.purgeNoIDEls(x)
        #debug_print('post-parse results:", \
        #    [self.extractID(x) for x in orig.iter()])
        return el1, el2

    def matchEls(self, seq1, seq2, *hashes):
        """Given 2 els, 
        1:1 match each el2 descendant with one el1 descendant
        and append the non-matched els to self.unmatched_els
        Return ([matched els],[unmatched els])
        
        How:
        Define hashes that define every descendant of given parents, and
        find the descendants in mirror el with equivalent hashes.
        """
        good_children = dict()

        for hash_ in hashes:
            #Run algorithm with given hash
            good_children.update(
                self.algorithm1(seq1, seq2, hash_))
        
            #Find remaining children
            seq1, seq2 = \
                self.getUnmatched(seq1, seq2, good_children)

            #print '---\nUnmatched els:'
            #print 'el1:', seq1
            #print
            #print 'el2:', seq2
        self.unmatched_seq1_els += seq1
        self.unmatched_seq2_els += seq2
        return good_children

    def setupFiles(self):
        """setup working dir/files"""
        if not os.path.exists(self.tmpdir):
            os.mkdir(self.tmpdir)
        rev_copy(self.docbook_p, self.docbook_merged, max_revs=5)

    def algorithm1(self, seq1, seq2, hash_, check_=None):
        """Given 2 sequences and hash function that uniquely pairs
        two elements (each in different seq),
        Return dict of seq1_el:seq2_el matches"""
      
        # get (hash,child) for all root el descendants
        seq1 = [(hash_(y), y) for y in seq1] 
        seq2 = [(hash_(y), y) for y in seq2] 
        good_children = dict() #{el1 descendant: el2 descendant}
        
        for x in seq1: #x is tuple, (hash, ith_child)
            ymatches = ()
            for y in seq2: #y is (hash, ith_child)
                if x[0] == y[0]:
                    ymatches += y
                elif len(ymatches) >= 4:
                    break
            if len(ymatches) == 2: #algorithm safe from hash collisions
                good_children.__setitem__(
                    x[1], #el1 child el
                    ymatches[1]) #el2 child

        #Check that there is 1:1 relationship between all keys and values
        checkseq = self.swapKeyValue(good_children)
        if len(checkseq) != len(good_children):
            raise Exception("seq2 elements matched multiple seq1 elements"
                            "but there is only supposed to be a "
                            "1:1 relationship")     
        
        if check_ != None:
            check(good_children)
        '''
        #Check that items are properly paired
        for x,y in good_children.items():
            bad = False
            a = x
            b = y
            #for a,b in [(x,y)]+ zip(x.iterancestors(), y.iterancestors()):
            while a.getparent() != None and b.getparent() != None:
                if a.getparent() == b.getparent() == None:
                    continue
                if not a.tag.split('}')[-1] == b.tag.split('}')[-1]:
                    bad = True
                    print a.tag, b.tag
                #elif not self.extractID(a).split('-')[-1] == \
                #        self.extractID(b).split('-')[-1]:
                #    bad = True
                #    print self.extractID(a), self.extractID(b)
                if bad == True:
                    print ('Algorithm incorrectly matched a ' 
                           'el pair, %s %s' % (x,y) )
                    del good_children[x]
                    break
                a = a.getparent()
                b = b.getparent()
        '''
        print('\n---\nAlgorithm matched %s %% of descendant els\n---\n' % (
            (100. * 2 * len(good_children)) / (len(seq1) + len(seq2) or True)))
        return good_children

    def replaceIDs(self, el2, matches):
        """#todo: iterate through these vars and swap element ids
        #assume this: at this point, children of every connected el in 
        #    orig and merged have a 1:1 relationship of ids
        """
        matches2 = self.swapKeyValue(matches) # {el2_el:el1_el}
        for n in el2.iter():            
            if n not in self.unmatched_seq2_els:
                id_ = self.extractID(matches2[n][0])
                n = self.setID(n, id_)
        return el2
    #TODO
    def saveDocbookAndTest(self, el):
        """
        #todo: make new docbook xml, test, etc
        """
        el.getroottree().write(self.docbook_merged, pretty_print=True)
        #1. genpdf of docbook_p
        #2. test_genpdf of docbook_merged with given fixture
        #3. backup docbook_orig and then replace




        self.el = el
        pass

    def getUnmatched(self, seq1, seq2, matchesdict):
        """Given 2 sequences and dict matching an element in seq1
        with one in seq2,
        Check that there is 1:1 matching between elements in seq1 and seq2
        Return unmatched elements in seq1 and seq2, respectively"""
        unmatched_seq1 = [x for x in seq1 
                          if x not in matchesdict.keys()]
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
    
    def extractID(self, el):
        """Given el, 
        Return the 'id' attribute if exists, else return empty string.  
        Check that every el only has one attribute name ending in 'id'"""
        ax = [el.attrib[x] for x in el.attrib if 'id' in x[-2:]]
        if len(ax) > 1:
            raise UnexpectedElementIdError(
                "There should only be 1 id attribute for every tag, "
                "but I found these ids: %s" % ', '.join(ax))
        return ''.join(ax)

    def setID(self, el, value):
        """Given el,
        Set the 'id' attribute and return el"""
        id_ = self.extractID(el)
        if id_ == '':
            raise UnexpectedElementIDError(
                "No id attribute tag found for given el, "
                "but here is list of el attributes: %s" % str(el.attrib))
        return el.set(id_, value)

    def purgeNoIDEls(self, parent):
        """Return modified parent el where
        all descendants that don't have xml:id are removed"""
        for child in parent:
            if all(self.extractID(z) == '' for z in child.iter()):
                #debug_print 'removing child', child
                parent.remove(child)
            else:
                child = self.purgeNoIDEls(child)
        return parent

    #TODO
    def evalIfAffectsOverlays(self, el1, el2):
        """Given els in docbook element tree, 
        evaluate if missing els that exist in 
        el1 but not in el2 will 
        break overlays when we start using the merged docbook."""
            #todo: eval if this effects overlays
            #    discussion: when does a missing el affect overlays?  if the overlays are calling its xml:id or any of its children't xml:ids, then we will break overlays.  What should I do? Modify overlays or not?
            #
            #also, I can't just continue because the algorithm assumes that nels_orig is only <= nels_merged, so fixing needs to happen
            
            #print warning and return (don't recurse through el's children)
        print (#raise ElemLengthError(
            "%s els were removed in proofread book.  Continuing will "
            "break overlays that rely on these changes" 
            % (len(el1) - len(el2)))

DEBUG=0
def debug_print(*msg):
    if DEBUG:
        print(''.join(msg))
if __name__ == '__main__':
    a = Match('siegel', 'siegel_p')
