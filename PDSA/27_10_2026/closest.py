from math import sqrt
from sorting import comparison, depth

def distance2(a, b, stats):
    comparison(stats)
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

def brute_force(points, stats=None):
    if len(points) < 2:
        raise ValueError('Je nutné zadat alespoň dva body.')
    best, pair = float('inf'), None
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            d = distance2(points[i], points[j], stats)
            if d < best:
                best, pair = d, (points[i], points[j])
    return sqrt(best), pair

def closest_pair(points, stats=None):
    if len(points) < 2:
        raise ValueError('Je nutné zadat alespoň dva body.')
    # ID odliší i různé vstupní body se shodnými souřadnicemi.
    px = sorted((x, y, i) for i, (x, y) in enumerate(points))
    py = sorted(px, key=lambda p: (p[1], p[0], p[2]))
    def solve(xs, ys, level):
        depth(stats, level)
        if len(xs) <= 3:
            best, pair = float('inf'), None
            for i in range(len(xs)):
                for j in range(i+1, len(xs)):
                    d = distance2(xs[i], xs[j], stats)
                    if d < best:
                        best, pair = d, (xs[i], xs[j])
            return best, pair
        mid = len(xs)//2
        left, right = xs[:mid], xs[mid:]
        ids = {p[2] for p in left}
        ly, ry = [], []
        for p in ys:
            (ly if p[2] in ids else ry).append(p)
        dl, pl = solve(left, ly, level+1)
        dr, pr = solve(right, ry, level+1)
        best, pair = (dl, pl) if dl <= dr else (dr, pr)
        if best == 0:
            return best, pair
        border = right[0][0]
        strip = [p for p in ys if (p[0]-border)**2 < best]
        for i in range(len(strip)):
            for j in range(i+1, min(i+8, len(strip))):
                if (strip[j][1]-strip[i][1])**2 >= best:
                    break
                d = distance2(strip[i], strip[j], stats)
                if d < best:
                    best, pair = d, (strip[i], strip[j])
        return best, pair
    best, pair = solve(px, py, 1)
    return sqrt(best), tuple((p[0], p[1]) for p in pair)
