#!/usr/bin/env python
"""Get word count and sentence index for every word in a string"""
from collections import defaultdict
import operator

def makedict(string):
    """Given string, return dict of words: (word_count, set(sentence_indexes))"""

    # initialize dictionary where
    # values automatically have form: [num_occurrences, (sentence_index1, ...)]
    d = defaultdict(lambda: [0, set()])

    for c,s in enumerate(string.split('.')):
        for w in s.split():
            d[w][1].add(c+1)
            d[w][0] += 1
    return d

def report(d):
    """Given dict, display it sorted by value"""
    a = sorted(d.iteritems(), key=operator.itemgetter(1), reverse=1)
    for x in a:
        print "%s, %s, %s" % (x[0], x[1][0], list(x[1][1]))

def run(string):
    report(makedict(string))


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        run(open(sys.argv[1]).read())
    else:
        string = "Meet Jon. Jon is a computer programmer and " +\
                 "lives in Connecticut. Jon is tall."
        print "Since you didn't provide a filepath, I'm analyzing this string:"
        print string
        print
        run(string)

