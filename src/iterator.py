def take_each_n(iter, n):
    c = 0
    for i in iter:
        if c % n == 0:
            yield i
        c = c + 1
from itertools import chain, islice
def batch(iterable, batch_size):
    while batch := list(islice(iterable, batch_size)):
        yield batch

def flatten(iterables):
    return (elem for iterable in iterables for elem in iterable)