def take_each_n(iter, n):
    c = 0
    for i in iter:
        if c % n == 0:
            yield i
        c = c + 1