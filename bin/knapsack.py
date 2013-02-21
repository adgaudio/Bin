from numpy import array, zeros


# Fundamental realization with knapsack is that the optimal solution is always
# one of these two options: 1) the optimal value of the last element at
# current weight limit, or 2) the value of current element + optimal value of
# the last element at a weight of (current weight limit - weight of last element)
def knapsack(v, w, W):
    """Given a list of items where each item has a value, v[i], and weight, w[i],
    and a maximum weight limit, W, what is the max value I can have?
    Also, what items (defined by indices) make up this max value?
    """
    assert len(v) == len(w)
    Vmap = zeros((len(v), W))  # optimal solution map
    possible_items_in_knapsack = zeros(
        (len(v), W))  # items are identified by index

    for i in range(len(v)):  # for every element
        for W_max in range(W):  # assume knapsack has a maximum possible weight

            previous_optimum = Vmap[i - 1, W_max]
                # optimal value of all previous elements for this knapsack
                                                 # (ie. we've already declared optimal values for i-1, i-2, ..., i-i)

            if (w[i] <= W_max):  # does item fit in this knapsack?
                # it fits!  So is the optimum value one we've seen already?
                # Or does this new item add a new optimum value?

                new_potential_optimum = v[i] + Vmap[i - 1, W_max - w[i]]  # aka the maximum value that can be made if we must include this element in the knapsack

                if previous_optimum > new_potential_optimum:
                    Vmap[i, W_max] = previous_optimum  # previous optimal value doesn't consider this ith element
                else:
                    Vmap[i, W_max] = new_potential_optimum
                    possible_items_in_knapsack[i, W_max] = 1
            else:
                # it doesn't fit, so the optimum value doesn't include this
                # item, and the knapsack's optimum value at this point is the
                # optimum value we determined for the previous element in this
                # knapsack
                Vmap[i, W_max] = previous_optimum
    # figure out which items are actually in the knapsack
    W_tmp = W - 1
    item_indices = []
    for i in reversed(range(len(v))):
        if possible_items_in_knapsack[i, W_tmp]:
            item_indices.append(i)
            W_tmp -= w[i]
    #print possible_items_in_knapsack
    #print Vmap
    return Vmap[len(v) - 1, W - 1], item_indices


if __name__ == '__main__':
    values = array([10, 4, 3, 7])
    weights = array([6, 4, 3, 5])
    max_weight = 10

    max_value, item_indices = knapsack(values, weights, max_weight)
    print 'for items with:'
    print '  values, v = ', values
    print '  weights, v = ', weights
    print 'and max weight = ', max_weight
    print 'max value', max_value
    print 'item indices', item_indices
