from random import randrange


def floor_div(a, b):
    return a // b


def ceil_div(a, b):
    return a // b + (a % b > 0)


def _insert(M, a, b):
    for i, (a_, b_) in enumerate(M):
        if a_ <= b and a <= b_:
            a = min(a, a_)
            b = max(b, b_)
            M[i] = (a, b)
            return

    M.append((a, b))
    return


def _step_1(padding_oracle, n, e, c):
    s0 = 1
    c0 = c
    while not padding_oracle(c0):
        s0 = randrange(2, n)
        c0 = (c * pow(s0, e, n)) % n

    return s0, c0


def _step_2a(padding_oracle, n, e, c0, B):
    s = ceil_div(n, 3 * B)
    while not padding_oracle((c0 * pow(s, e, n)) % n):
        s += 1

    return s


def _step_2b(padding_oracle, n, e, c0, s):
    s += 1
    while not padding_oracle((c0 * pow(s, e, n)) % n):
        s += 1

    return s


def _step_2c(padding_oracle, n, e, c0, B, s, a, b):
    r = ceil_div(2 * (b * s - 2 * B), n)
    while True:
        left = ceil_div(2 * B + r * n, b)
        right = floor_div(3 * B + r * n, a)
        for s in range(left, right + 1):
            if padding_oracle((c0 * pow(s, e, n)) % n):
                return s

        r += 1


def _step_3(n, B, s, M):
    M_ = []
    for (a, b) in M:
        left = ceil_div(a * s - 3 * B + 1, n)
        right = floor_div(b * s - 2 * B, n)
        for r in range(left, right + 1):
            a_ = max(a, ceil_div(2 * B + r * n, s))
            b_ = min(b, floor_div(3 * B - 1 + r * n, s))
            _insert(M_, a_, b_)

    return M_


def attack(padding_oracle, n, e, c):
    k = ceil_div(n.bit_length(), 8)
    B = 2 ** (8 * (k - 2))

    s0, c0 = _step_1(padding_oracle, n, e, c)
    M = [(2 * B, 3 * B - 1)]

    s = _step_2a(padding_oracle, n, e, c0, B)
    M = _step_3(n, B, s, M)

    while True:
        if len(M) > 1:
            s = _step_2b(padding_oracle, n, e, c0, s)
        else:
            (a, b) = M[0]
            if a == b:
                m = (a * pow(s0, -1, n)) % n
                return m
            s = _step_2c(padding_oracle, n, e, c0, B, s, a, b)
        M = _step_3(n, B, s, M)
