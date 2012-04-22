# Basic utilities for working with a binary heap data structure.
# The heap is stored as an array and objects inside this array must be
# comparable (ie a < b)

def insert(val, heap):
    heap.append(val)
    child_i = len(heap) - 1
    parent_i = parent_of(child_i, heap)
    while heap[child_i] < heap[parent_i]:
        swap(child_i, parent_i, heap)
        child_i = parent_i
        parent_i = parent_of(child_i, heap)
    return heap

def poproot(heap):
    root = heap[0]
    heap[0] = heap.pop()
    heap_size = len(heap)
    parent_i = 0
    child_i = min_child_of(parent_i, heap, heap_size)
    print child_i
    while child_i < heap_size and heap[child_i] < heap[parent_i]:
        swap(child_i, parent_i, heap)
        parent_i = child_i
        child_i = min_child_of(parent_i, heap, heap_size)
    return root

def swap(i, j, heap):
    tmp = heap[i]
    heap[i] = heap[j]
    heap[j] = tmp
    return heap

def parent_of(child_i, heap):
    #return child_i / 2
    return child_i >> 1

def min_child_of(parent_i, heap, heap_size):
    ith_child = parent_i and parent_i << 1 or 1 # base case
    if len(heap) <= ith_child+1:
        return ith_child
    if heap[ith_child] < heap[ith_child+1]:
        return ith_child
    return ith_child + 1

