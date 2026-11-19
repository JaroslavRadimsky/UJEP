def validate(x, y):
    if not isinstance(x, int) or not isinstance(y, int) or x < 0 or y < 0:
        raise ValueError('Očekávám dvě nezáporná celá čísla.')

def karatsuba(x, y):
    validate(x, y)
    def rec(a, b):
        if a < 10 or b < 10:
            return a*b
        m = max(len(str(a)), len(str(b))) // 2
        base = 10**m
        ah, al = divmod(a, base)
        bh, bl = divmod(b, base)
        z2, z0 = rec(ah, bh), rec(al, bl)
        z1 = rec(ah+al, bh+bl) - z2 - z0
        return z2*base**2 + z1*base + z0
    return rec(x, y)

def school_multiply(x, y):
    validate(x, y)
    a, b = list(map(int, str(x)[::-1])), list(map(int, str(y)[::-1]))
    digits = [0]*(len(a)+len(b))
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            digits[i+j] += u*v
    for i in range(len(digits)-1):
        carry, digits[i] = divmod(digits[i], 10)
        digits[i+1] += carry
    result = 0
    for digit in reversed(digits):
        result = result*10 + digit
    return result
