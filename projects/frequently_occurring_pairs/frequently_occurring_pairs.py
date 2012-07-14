#!/usr/bin/env python
"""
I'm given a spreadsheet containing several rows of artist names and asked to find the artist pairs that occur 50 or more times.

Q: what are the most frequently occurring artist pairs in given data set?

Reading the description, I realized this is a frequency analysis problem,
and then realized it would be the birthday problem if we were to consider
combinations larger than just pairs...

...

So first, who are the most frequently occuring artists?

then, given a frequency distribution of artists occuring at least 50 times,
define the probability that a given artist will appear on any given line

    p(artist1) = f1/n

    where f1 = num lines that artist1 appeared on
          n = total num lines of input

what's the likelihood that any 2 of them appear together at least 50 times?

    p(pair appears once) = p(artist1) * p(artist2) = f1/n * f2/n
    p(pair appears twice) = f1*f2/n**2 * (f1-1)*(f2-1)/(n-1)**2
    ...
    p(pair appears x times) <= ( (f1!/(f1-x)!) * (f2!/(f2-x)!) ) / (n**2 * (n-1)**2 * ... (n-x)**2)

    where n = total number of lines
          x = min number times something occurs
          f1 and f2 = number of lines each artist appeared on, respectively

what artist pairs have 90% or higher probability that
it'll appear at least 50 times?

    .90 <= ( (f1!/(f1-x)!) * (f2!/(f2-x)!) ) / lambda

    f2! / (f2-x)! >= .90 * lambda / (f1!/(f1-x)!)

    where lambda = (n**2 * (n-1)**2 * ... * (n-x)**2)
    and f1 represents a given artist 
    and f2 is any other artist

Computing factorials can be memory intensive and this is scary looking.
We should simplify by taking the log and applying log rules.

... simplify lambda term

    log(lambda) = log(n**2 * (n-1)**2 * ... * (n-x)**2)
                = log(n**2) + log((n-1)**2) + ... + log((n-x)**2)
                = 2*(log(n) + log(n-1) + ... + log(n-x))
                = 2*sum(log(i) where n-x<i<=n)

...simplify factorials:

    let function g(X;y) = log(X!/(X-y)!)
                        = sum(log(x_i) where y < x_i <= X)

    such that:

    g(f2;x) = log(f2!/(f2-x)!)
            = log(f2!) - log((f2-x)!)
            = sum(log(i) where f2-x <= i <= f2)

...therefore:

    log( f2! / (f2-x)! ) >= log( .90 * lambda / (f1!/(f1-x)!) )
    g(f2;x) >= log(.90) - g(f1;x) + log(lambda)

    threshold = log(.90) - g(f1; x) + log(lambda)
             <= g(f2; x)

so, given artist1, find all other artists whose g(frequency;50) is >= the
threshold defined.  Then, produce combinations of (artist1, artistX)

**
Runtime analysis

    The left side of the equation:
    O(g(f2;x)) = O(f2-x)

    The right side of the equation:
    O(log(.90) + g(n;x) + g(f1;x)) = 1 + O(n-x) + O(f1-x)

**
assumptions:
  each row in data set is unique (actually, there is a duplicate artist on line 922)
  there are 973 rows (not 1000!)
  python is going to have string encoding issues
  artists are indepedent variables
"""
import csv
import nltk
import numpy
import pandas

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
    if len(dists) != 1000: print "The total number of lines considered is: ", len(dists)

###
# Scoring
###
def find_pairs(frequencies,
               certainty=.853**1000, min_occurrences=50., max_occurrences=973.):
    """
    Given an indexed pandas.Series obj whose data represents the number of
    times each element (identified by index) appeared, identify
    pairs of objects which occured together at least min_occurrences times
    in a given sample size of max_occurrences with given certainty (b/t 0 and 1)

    The following equation determines this relationship between a given
    element of the input object, f1, and any other element in that array, f2:

        threshold = log(.90) - g(f1; x) + log(lambda)
                 <= g(f2; x)

            where g(x;y) = log( X!/(X-y)!)

            = sum(log(i) where f2-x < i <= f2)
                  n = max_occurrences
                  x = min_occurrences
                  log(lambda) = 2*sum(log(arange(n-x+1, n+1)))
    """
    log_lambda = 2 * numpy.sum(
                   numpy.log(
                   numpy.arange(max_occurrences-min_occurrences+1,
                                max_occurrences+1)))
    g = lambda num: numpy.log(numpy.arange(num - min_occurrences+1, num+1)).sum()

    frequencies = frequencies[frequencies >= min_occurrences] # optimization

    pairings = {}
    for artist in frequencies.index:
        f1 = frequencies[ artist ]
        threshold = numpy.log(certainty) - g(f1) + log_lambda

        artist_loc = frequencies.index.get_loc(artist)
        considered_freqs = frequencies[artist_loc+1:]
        other_artists = considered_freqs[
                considered_freqs.apply(g) > threshold
                ].index

        pairings[artist] = other_artists
    return pairings

###
# Results
###
def make_pairs(dct):
    for a1,others in dct.items():
        for a2 in others:
            yield (a1,a2)


def main():
    raw_data = open('./Artist_lists_small.txt', 'r').readlines()
    validate(raw_data)
    artists = (word
                    for line in raw_data
                    for word in line.split(','))
    total_dist = nltk.FreqDist(artists)
    frequencies = pandas.Series(total_dist.values(), index=total_dist.samples())
    pairings = find_pairs(frequencies)
    print 'Found %s pairs' % sum(len(x) for x in pairings.values())
    gen = make_pairs(pairings)
    print 'first 10 pairs in no particular order:'
    for x in range(10):
        print next(gen)

if __name__ == '__main__':
    main()
