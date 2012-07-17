#!/usr/bin/env python
"""
I'm given a spreadsheet containing several rows of artist names and 
asked to find the artist pairs that occur 50 or more times.

Q: what are the most frequently occurring artist pairs in given data set?

Reading the description, I realized this is a frequency analysis problem,
and then realized it would be the birthday problem if we were to consider
combinations larger than just pairs...

...

first, who are the most frequently occuring artists?

then, given a frequency distribution of artists occuring at least 50 times,
define the probability that a given artist will appear on any given line

    p(artist1) = f1/n

    where f1 = num lines that artist1 appeared on
          n = total num lines of input

what's the likelihood that any 2 of them appear together at least 50 times?

    p  = p(pair appears on given line) = p(artist1) * p(artist2) = (f1/n * f2/n)
    p' = p(pair doesnt appear on a line) = 1-p

    p(pair;1) = p(pair appears on exactly 1 line) = \
            (n choose 1)
            * p(pair appears on given line)
            * p(pair doesn't appear on remaining lines)**(n-1)

    p(pair;k) = p(pair appears on exactly k lines)
              = (n choose k) * p**k * (1-p)**(n-k)

    where n = total number of lines
          k = min number occurrences
          f1 and f2 = number of lines each artist appeared on, respectively

find and return the artist pairs whose max(p(pair;k) for 0 < k < n)
is greater than 50
  - this is optimized by checking if the gradient at k=50 and k=51 is increasing
  - Also, introduce the idea of certainty in the p(pair;k) function:

      n = certainty * n.

    Changing the size of n (the size of the feature space), we change where the
    peak of this distribution falls, thereby returning more (certainty -> 0) or
    less (certainty -> 1) pairs

**
Runtime analysis

Assuming p(pair;k, k+1) is a constant value, c, the algorithm is bounded by:

    O(c + sum(i for i in  1..n))
        where n is number of artists who appear at least 50 times

**
assumptions:
  each row in data set is unique
      (actually, there is a duplicate artist on line 922)
  there are 973 rows (not 1000!)
  python is going to have string encoding issues
  artists are indepedent variables
"""
import csv
from functools import partial
import nltk
import pandas
import scipy

###
# Data Validation
###
def check_row_uniqueness(dists):
    for n,dist in enumerate(dists):
        if dist.itervalues().next() > 1:
            print 'line %s has dup artists: %s' % \
                    (n, [k for k,v in dist.items() if v>1])

def validate(raw_data):
    dists = [nltk.FreqDist(line)
            for line in csv.reader(raw_data) if len(line)]
    check_row_uniqueness(dists)
    if len(dists) != 1000: 
        print "The total number of lines considered is: ", len(dists)

###
# Scoring
###
def is_pair(p_pair, min_occurrences, max_occurrences, certainty):
    """
    Determine whether a pair occurrs min_occurrences or more times
    given probability of occurring, p_pair, and the max_occurrences possible.

    The binomial probability mass function defines the relationship between
    any 2 elements of the frequencies array according to the following:

    p(pair on exactly k lines) = choose(n,k) * p(pair)**k * (1-p(pair))**(n-k)

      where p(pair) =  p(artist1) * p(artist2)
      and p(artist) = (num artist occurrences) / max_occurrences

    If we know the probability of a pair on the kth and kth+1 lines, and if 
    p(k+1) > p(k), we know that the most likely number of pairs is some
    number > k

    Note, the certainty is a number between 0 and 1. It changes the size of
    the feature space, n, which means it reduces the distribution's mean, and
    therefore makes it more likely that a pair will occur.
    """
    likelihoods = scipy.stats.binom.pmf(
            [min_occurrences-1, min_occurrences],
            1./certainty*max_occurrences,
            p_pair)
    return likelihoods.argmax() == 1

def find_pairs(frequencies,
               certainty=.5,
               min_occurrences=50.,
               max_occurrences=973.):
    """
    Given frequencies, an indexed pandas.Series obj whose data represents
    the number of times each element appeared, identify pairs of objects
    which occured together at least min_occurrences times
    in a given sample size of max_occurrences
    with a level of certainty b/t 0 and 1
    """
    pairings = {}

    is_pair_partial = partial(is_pair,
            min_occurrences=min_occurrences,
            max_occurrences=max_occurrences,
            certainty=certainty)

    frequencies = frequencies[frequencies >= min_occurrences] # optimization
    probs = frequencies / max_occurrences
    for artist in probs.index:
        artist_loc = frequencies.index.get_loc(artist)
        p1 = probs[artist]
        joint_probs = probs[artist_loc+1:].apply(lambda p2: p1 * p2)
        pairs = joint_probs.apply(is_pair_partial)
        pairings[artist] = pairs[pairs == True].index
    return pairings

###
# Results
###
def make_pairs(dct):
    for a1,others in dct.items():
        for a2 in others:
            yield (a1,a2)


def main(certainty=.9):
    raw_data = open('./Artist_lists_small.txt', 'r').readlines()
    validate(raw_data)
    artists = (word
                    for line in raw_data
                    for word in line.split(','))
    total_dist = nltk.FreqDist(artists)
    frequencies = pandas.Series(total_dist.values(), index=total_dist.samples())
    pairings = find_pairs(frequencies, certainty=certainty)
    print 'Found %s pairs' % sum(len(x) for x in pairings.values())
    gen = make_pairs(pairings)
    print 'first 10 pairs in no particular order:'
    for x in range(10):
        print next(gen)
    return total_dist, frequencies, pairings

if __name__ == '__main__':
    total_dist, frequencies, pairings = main()
