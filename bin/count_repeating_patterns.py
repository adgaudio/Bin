#!/usr/bin/env python
"""
Find all 2 element pairs that occur more than 50 times in a csv
"""
from itertools import combinations

def getPairs(filepath):
    """Given csv filepath,
    Yield all 2 element pairs in each row of csv"""
    for line in open(filepath, 'r').read().split('\n'):
        for pair in combinations(line.split(','), 2):
            yield pair

def run(filepath, num=50):
    """Given csv filepath and int,
    Return pairs of elements that exist in more than 'num' rows"""
    data = {} # in form: { (artist1, artist2) : [count, ith_pair] }
    c = 0 # keep track of which pair came first

    for pair in getPairs(filepath):
        c += 1

        # Gen running count of all pairs across whole csv
        if pair not in data:
            data[pair] = [1, c]
        elif data[pair][0] > 50:
            continue
        else:
            data[pair][0] += 1

    # Get only pairs that occurred > num times
    output = [x for x in data.viewitems() if x[1][0] > num]
    # Sort and pairs by order in which they were found
    output = sorted(output, key=lambda x: x[1][1])
    return [x[0] for x in output]

    return [x[0] for x in output if x[1][0] > num]

if __name__ == '__main__':
    import sys
    from pprint import pprint
    if len(sys.argv) > 1:
        pprint( run(sys.argv[1]) )
    else:
        filepath = './Artist_lists_small.csv'
        print "Since you didn't supply a filepath to a csv, I'm using this one:"
        print filepath
        pprint( run(filepath) )
