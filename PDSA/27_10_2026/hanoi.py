def hanoi(n, source='A', target='B', auxiliary='C'):
    """Generuje tahy (zdroj, cíl); n musí být nezáporné celé číslo."""
    if not isinstance(n, int) or n < 0:
        raise ValueError('n musí být nezáporné celé číslo')
    if n:
        yield from hanoi(n-1, source, auxiliary, target)
        yield source, target
        yield from hanoi(n-1, auxiliary, target, source)

def verify_hanoi(n):
    rods = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
    moves = list(hanoi(n))
    for source, target in moves:
        assert rods[source], 'Prázdná zdrojová tyč'
        disk = rods[source].pop()
        assert not rods[target] or rods[target][-1] > disk, 'Větší disk na menším'
        rods[target].append(disk)
    assert rods == {'A': [], 'B': list(range(n, 0, -1)), 'C': []}
    assert len(moves) == 2**n-1
    return len(moves)
