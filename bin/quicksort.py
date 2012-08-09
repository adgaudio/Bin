"""Perform in place quicksort on input array with different partition options

O(nlogn) on avg
O(n**2) in worst case, ie recursively left partition a reverse sorted array
"""

import random

def swap(i,j,A):
    tmp = A[i]
    A[i] = A[j]
    A[j] = tmp

def partitionLeft(l, r, A):
    """Partition array A[l:r] such that everything left of the returned
    partition/pivot index, i, is less than the pivot value, and everything
    right of the returned partition index is greater than the pivot value

    fyi: chooses pivot value of left-most element, A[l]
    """
    p = A[l] # pivot value
    i = l+1 # partition index
    j = l+1 # index over l..r
    while j <= r:
        if A[j] < p:
            swap(i,j,A)
            i += 1
        j += 1
    swap(l, i-1, A)
    print A
    return i

def partitionRight(l, r, A):
    """Partition Array A[l:r] using A[r] as pivot"""
    swap(l,r, A)
    return partitionLeft(l,r,A)

def partitionRandom(l, r, A):
    """Partition array A[l:r] using random pivot"""
    pivot_index = random.randint(l,r)
    swap(l,pivot_index, A)
    return partitionLeft(l,r,A)

def quicksort(A, l=None, r=None, partition=partitionRandom):
    if not l:
        l = 0
    if not r:
        r = len(A) - 1

    if r <= l+1:
        return
    next_pivot_i = partition(l,r, A)
    quicksort(A, l, next_pivot_i-1, partition)
    quicksort(A, next_pivot_i, r, partition)
    return A


if __name__ == '__main__':
    import sys
    arr = [int(i) for i in sys.argv[1:]]
    if not arr:
        arr = [random.randint(0,100) for x in range(10)]

    print quicksort(arr, partition=partitionRandom)
