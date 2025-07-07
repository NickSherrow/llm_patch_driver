from timeit import timeit
from glom import glom, Iter

data = [{'x': i, 'y': i * 2} for i in range(1000)]

# 1) list-comprehension
def comp():
    return [d['y'] for d in data if d['x'] % 2 == 0]

# 2) glom spec
spec = ([{'y': 'y'}], Iter().filter(lambda d: d['x'] % 2 == 0))
def g():
    return glom(data, spec)

def a():
    return "kek"

print("comp:", timeit(comp, number=10000))
print("glom:", timeit(a, number=10000))
