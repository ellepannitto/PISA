import os
import itertools
import heapq
import contextlib

nouns_per_verb = {}
input_path = "data/ukwac_nouns_filtered_th300/"
for filename in os.listdir(input_path):
    verb = filename.split(".")[-1]
    print(verb)
    nouns_per_verb[verb] = []
    with open(input_path + filename) as fin:
        for line in fin:
            word = line.strip().split()[0]
            if all(x.isalpha() or x in ["-", "'"] for x in word):
                nouns_per_verb[verb].append(word)

    for verb in nouns_per_verb:
        nouns_per_verb[verb] = list(sorted(nouns_per_verb[verb]))

generators = {}
for verb in nouns_per_verb:
    generators[verb] = itertools.combinations(nouns_per_verb[verb], 2)

next_items = {verb: generators[verb].__next__() for verb in generators}
#next_item = min(next_items.values())
#print(next_items)
#print(next_item)
#print([x for x in next_items.values() if x == next_item])

#with contextlib.ExitStack() as stack:

def tuples_generator(nouns_per_verb):
    files = [itertools.combinations(nouns_per_verb[verb], 2) for verb in nouns_per_verb]
    last_tuple = None
    for tuple in heapq.merge(*files):
        if not tuple == last_tuple:
            yield tuple
            last_tuple = tuple


print(tuples_generator(nouns_per_verb))

for tuple in tuples_generator(nouns_per_verb):
    print(tuple)
    input()