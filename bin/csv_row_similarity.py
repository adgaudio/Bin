"""Analyze a csv and generate similarity metric between all pairs of rows in the csv
"""

from pandas import read_csv
from itertools import combinations
from operator import itemgetter
from collections import defaultdict

from settings import filepath


def preprocess(data, also_remove=[]):
    """Given input structure with rows and cols (ie pandas DataFrame)
    remove columns that are entirely unique
    remove columns in also_remove list
    Return DataFrame"""

    for col in data.columns:
        if len(set(data[col])) != len(data[col]):
            data.pop(col)

    for col in also_remove:
        data.pop(col)
    return data


def scorePairRelationships(data):
    """Given input structure (ie pandas DataFrame)
    with columns and groupby, and indexed by some unique ID
    Return dictionary of that identifies number of connections
    between all 2 element pairs of IDs in the input data.

    dict in form:  { (ID1, ID2):count, ... }"""

    columns = {} # { col:{group1:IDs, group2:IDs, ...}, ... }
    relationships = defaultdict(int)

    tmp = []
    for col in data.columns:
        groups = data.groupby(col).groups
        for grp in groups:
            print 'grp', grp, 'size', len(groups[grp])
            #for pair in combinations(groups[grp], 2):
                #relationships[pair] += 1
            tmp.append(groups)
    return tmp
    #result = sorted(relationships.iteritems(), key=itemgetter(1), reverse=1)
    #return result

#print score(data)[:int(len(result) * .10)]
def go():
    data = read_csv(filepath)
    data = preprocess(data)
    relationships = scorePairRelationships(data)

go()
