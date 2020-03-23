import os
import collections

verbs = set()
for filename in os.listdir("ukwac1"):
    v = filename.split(".")[1]
    verbs.add(v)

for verb in verbs:
    files = ["ukwac{}/output_nouns.{}".format(i, verb) for i in range(1, 6)]

    d = collections.defaultdict(int)
    for f in files:
        with open(f) as fin:
            for line in fin:
                line = line.strip().split()
                d[line[0]] += int(line[1])

    with open("output_nouns.{}".format(verb), "w") as fout:
        sorted_d = sorted(d.items(), key=lambda x: -x[1])
        for x, y in sorted_d:
            print(x, y, file=fout)
