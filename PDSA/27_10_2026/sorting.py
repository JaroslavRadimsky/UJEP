"""Řazení; statistiky se sbírají pouze při předání slovníku stats."""
import random

def comparison(stats, count=1):
    if stats is not None:
        stats['operations'] = stats.get('operations', 0) + count

def depth(stats, level):
    if stats is not None:
        stats['depth'] = max(stats.get('depth', 0), level)

def merge_sort(data, stats=None, key=lambda x: x, level=1):
    depth(stats, level)
    if len(data) <= 1:
        return list(data)
    mid = len(data) // 2
    left = merge_sort(data[:mid], stats, key, level+1)
    right = merge_sort(data[mid:], stats, key, level+1)
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        comparison(stats)
        if key(left[i]) <= key(right[j]):  # Shoda: přednost má levá část.
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

def quick_sort(data, stats=None, pivot='random', rng=None, level=1):
    if pivot not in ('first', 'random'):
        raise ValueError('Pivot musí být first nebo random.')
    if rng is None:
        rng = random.Random(42)
    depth(stats, level)
    if len(data) <= 1:
        return list(data)
    p = data[0] if pivot == 'first' else rng.choice(data)
    left, equal, right = [], [], []
    for x in data:
        comparison(stats)
        if x < p:
            left.append(x)
        else:
            comparison(stats)  # Počítáme i druhé skutečně provedené porovnání.
            if x == p:
                equal.append(x)
            else:
                right.append(x)
    return (quick_sort(left, stats, pivot, rng, level+1) + equal
            + quick_sort(right, stats, pivot, rng, level+1))

def bubble_sort(data, stats=None):
    a = list(data)
    for end in range(len(a)-1, 0, -1):
        changed = False
        for i in range(end):
            comparison(stats)
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                changed = True
        if not changed:  # Používáme předčasné ukončení.
            break
    return a

def shaker_sort(data, stats=None):
    a = list(data)
    lo, hi = 0, len(a)-1
    while lo < hi:
        changed = False
        for i in range(lo, hi):
            comparison(stats)
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]; changed = True
        hi -= 1
        if not changed:
            break
        changed = False
        for i in range(hi, lo, -1):
            comparison(stats)
            if a[i-1] > a[i]:
                a[i-1], a[i] = a[i], a[i-1]; changed = True
        lo += 1
        if not changed:
            break
    return a
