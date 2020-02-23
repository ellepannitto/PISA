import os
import collections
import gzip
import heapq
import contextlib
from multiprocessing import Pool

d = collections.defaultdict(list)
for filename in os.listdir("."):
    filename = filename.split(".")
    d[".".join(filename[:-2])].append(".".join(filename))


def merge(tup):
    model, files = tup
    print(os.getpid(), " - PROCESSING MODEL ", model)
    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(gzip.open(fn, "rt")) for fn in files]
        with gzip.open('{}.merged.gzip'.format(model), 'wt') as f:
            f.writelines(heapq.merge(*files))

with Pool(12) as p:
    p.map(merge, d.items())