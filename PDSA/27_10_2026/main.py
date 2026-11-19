"""Příprava dat a férové experimenty. Spuštění: python main.py."""
import csv
import math
import random
import sys
from pathlib import Path
from statistics import median
from time import perf_counter
from sorting import merge_sort, quick_sort, bubble_sort, shaker_sort
from closest import brute_force, closest_pair
from multiplication import karatsuba, school_multiply

SIZES = (100, 300, 1000, 3000)

def measure(fn, data, check, repeats=7):
    # Kopie, kontrola i generování dat leží mimo měřený úsek.
    fn(list(data))  # Zahřívací běh.
    times = []
    for _ in range(repeats):
        work = list(data)
        start = perf_counter()
        result = fn(work)
        times.append(perf_counter()-start)
        assert check(result)
    return median(times)

def run_experiments():
    rng = random.Random(42)
    rows = []
    algorithms = {
        'Merge Sort': merge_sort,
        'Quick Sort / první': lambda a, stats=None: quick_sort(a, stats, 'first'),
        'Quick Sort / náhodný': lambda a, stats=None: quick_sort(a, stats, 'random', random.Random(42)),
        'Bubble Sort': bubble_sort,
        'Shaker Sort': shaker_sort,
    }
    for n in SIZES:
        data = [rng.randint(0, 10*n) for _ in range(n)]
        datasets = {'náhodná': data, 'vzestupná': sorted(data),
                    'sestupná': sorted(data, reverse=True),
                    'mnoho shod': [rng.randint(0, 9) for _ in range(n)]}
        for kind, values in datasets.items():
            expected = sorted(values)
            for name, fn in algorithms.items():
                stats = {'operations': 0, 'depth': 0}
                row = dict(group='řazení', algorithm=name, input=kind, n=n,
                           seconds=None, operations=None, depth=None, correct=False, status='OK')
                try:
                    row['seconds'] = measure(fn, values, lambda a: a == expected)
                    assert fn(list(values), stats) == expected  # Oddělený běh s počítadly.
                    row.update(operations=stats['operations'], depth=stats['depth'], correct=True)
                except RecursionError:
                    row['status'] = 'RecursionError'
                rows.append(row)
    for n in SIZES:
        points = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(n)]
        expected = brute_force(points)[0]
        for name, fn in [('Úplné prohledávání', brute_force), ('Rozděl a panuj', closest_pair)]:
            stats = {'operations': 0, 'depth': 0}
            check = lambda result: math.isclose(result[0], expected, rel_tol=1e-12, abs_tol=1e-12)
            elapsed = measure(fn, points, check)
            assert check(fn(list(points), stats))
            rows.append(dict(group='body', algorithm=name, input='rovina', n=n,
                             seconds=elapsed, operations=stats['operations'], depth=stats['depth'],
                             correct=True, status='OK'))
    return rows

def multiplication_experiments():
    rng = random.Random(42)
    rows = []
    for digits in (10, 30, 100, 300, 1000):
        x, y = (rng.randrange(10**(digits-1), 10**digits) for _ in range(2))
        expected = x*y
        for name, fn in [('Školní', school_multiply), ('Karatsuba', karatsuba)]:
            fn(x, y)
            times = []
            for _ in range(7):
                start = perf_counter(); result = fn(x, y); times.append(perf_counter()-start)
                assert result == expected
            rows.append(dict(algorithm=name, digits=digits, seconds=median(times), correct=True))
    return rows

def save_csv(rows, path):
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

if __name__ == '__main__':
    destination = Path(__file__).parent
    save_csv(run_experiments(), destination/'mereni.csv')
    save_csv(multiplication_experiments(), destination/'nasobeni.csv')
    print('Výsledky byly uloženy do CSV.')
