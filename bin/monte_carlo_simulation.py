"""
A heuristic for optimizing the value of a bin of items from an input set

where each item has a value and weight, and optionally a type

given the following constraint(s):
    the bin weight (sum of item weights) must be below a given weight limit
    by default, each item may only appear once
    optionally, the bin must have at least `num` elements of each item type

O(num_bins * bin_size)  ---  Assuming the samplers are also bound by that

TODO: one could significantly improve this by swapping indices in bin rather than just randomly selecting a zillion bins
        - there are a lot of better algorithms, like the cross entropy method
        - also, check out scipy.optimize.anneal
      Also, the bin_sampler is pretty basic.  A cython version might give a significant speedup for large num_bins

The problem described above is a multiple knapsack problem
with a lower bound on number of items in the input set.
"""
import numpy as np


def bin_sampler(high, num_bins, bin_size, low=0, guarantee_unique=True):
    """Sample indices from the set of items indexed from [low, high)
    uniformly at random and group the indicies into num_bins, each of bin_size
    Guarantee that each bin is a set by default.  If you can disable this,
    the sampler would be much faster..."""
    assert high >= bin_size
    if guarantee_unique:
        choices = np.arange(low, high)
        bins = np.array([np.random.choice(choices, replace=False, size=bin_size)
                         for _ in xrange(num_bins)])
        #for i in range(num_bins):
            #assert len(np.unique(bins[i, :])) == bin_size
    else:
        bins = np.random.random_integers(low, high - 1,
                                         size=(num_bins, bin_size))
    return bins


def grouped_bin_sampler(group_sizes, min_per_group, num_bins, bin_size):
    """Sample at least min_per_group indices from each group, where
    group_sizes defines the last index + 1 of each group in an array.
        ie.
        group_sizes = [10, 15, 35]

        Corresponds to 1st group of 10 elements at array[0:10]
        2nd group of 5 elements at array[10:15],
        and 3rd group of 20 elements at array[15:35]

    TODO: min_per_group can be an int or an array
    NOTE: While the indices are selected randomly each bin is not randomly sorted.
    """
    assert bin_size >= min_per_group * len(group_sizes)
    samples = np.empty((num_bins, 0), dtype='int')
    start = 0
    for end in group_sizes:
        new_samples = bin_sampler(high=end - start,
                                  num_bins=num_bins,
                                  bin_size=min_per_group)
        new_samples = new_samples + start
        samples = np.concatenate((samples, new_samples), axis=1)
        start = end
    ncols_remaining = bin_size - samples.shape[1]
    #print samples
    assert ncols_remaining == abs(ncols_remaining)
    if ncols_remaining > 0:
        new_samples = bin_sampler(high=group_sizes[-1],
                                  num_bins=num_bins,
                                  bin_size=ncols_remaining)
        samples = np.concatenate((samples, new_samples), axis=1)
    for i in range(len(group_sizes)):
        assert (samples[:, :(i + 1) * min_per_group] < group_sizes[i]).all()
    return samples


def find_best_bin(v, w, num_bins, bin_size, max_weight,
                  group_sizes=None, min_per_group=None, num_best_bins=1):
    """Given arrays v (values) and w (weights) where each item shares same index,
    Find the bin containing `bin_size-1` items with maximum possible value
    under a max_weight limit
    """
    num_items = len(v)
    assert len(v) == len(w)
    # Sample indices of items
    if group_sizes is not None:
        bins = grouped_bin_sampler(group_sizes, min_per_group,
                                   num_bins, bin_size)
    else:
        bins = bin_sampler(num_items, num_bins, bin_size)
    # Filter bins that are above the cost limit and find most valuable bin(s)
    value_per_bin = v[bins].sum(axis=1)
    cost_per_bin = w[bins].sum(axis=1)
    relevant_summed_bin_values = value_per_bin * (cost_per_bin <= max_weight)
    assert relevant_summed_bin_values.shape[0]
    if num_best_bins == 1:
        best_bin_index = relevant_summed_bin_values.argmax()
    else:
        best_bin_index = np.argsort(relevant_summed_bin_values)[-1 * num_best_bins:]
    best_value = value_per_bin[best_bin_index]
    best_bin = bins[best_bin_index, :]
    np.testing.assert_array_equal(
        best_value,
        relevant_summed_bin_values[relevant_summed_bin_values.argsort()[-1 * num_best_bins:]])
    np.testing.assert_array_equal(best_value, sorted(best_value))
    #print sorted(relevant_summed_bin_values)[-10:]
    #print sorted(value_per_bin[cost_per_bin <= max_weight])[-10:]
    #print 'argmax', relevant_summed_bin_values[relevant_summed_bin_values.argmax()]
    #print 'bbsum', best_bin.sum(axis=1)
    #print 'bv', best_value
    #print 'bb', best_bin
    return best_value, best_bin


def find_optimal_num_bins(num_bins_range=np.array(range(1, 20)) ** 3, *args, **kwargs):
    grad = np.zeros(num_bins_range.shape[0])
    i = -1
    for x in num_bins_range:
        i += 1
        num_bins = x

        bv, bb = find_best_bin(*args, num_bins=x, **kwargs)

        grad[i] = bv
    import pylab
    pylab.ion()
    pylab.plot(num_bins_range, grad)
    pylab.xlabel('num_bins')
    pylab.ylim(0)
    pylab.show()


if __name__ == '__main__':
    bin_size = 8
    num_items = 250
    num_bins = 100000
    max_weight = num_items * 20

    v = np.arange(num_items)
    np.random.shuffle(v)
    w = np.arange(num_items, num_items * 2)
    np.random.shuffle(w)

    #print '...plot best value for different num_bin values...'
    #find_optimal_num_bins(np.array(range(1, 15)) ** 4,
                          #v=v, w=w, bin_size=bin_size,
                          #max_weight=max_weight)
    print '\n...find best bin using num_bins = %s...' % num_bins
    bv, bb = find_best_bin(v, w, num_bins, bin_size, max_weight,
                           num_best_bins=3)
    print 'best value', bv
    print 'best bins', bb
