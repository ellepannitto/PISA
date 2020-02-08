import os
import tqdm
import sys

nouns = {}
with open("DSM_vocab.txt") as fin:
    for line in fin:
        nouns[line.strip()] = 0

ukwac_folders = ["ukwac{}/".format(i) for i in range(1, 6)]

path = "/extra/corpora/corpora-en/ukWaC/3_UD/"

for folder in tqdm.tqdm(ukwac_folders):
    for filename in tqdm.tqdm(os.listdir(path+folder)):
        with open(path+folder+filename) as fin:
            for line in fin:
                line = line.strip().split()
                if len(line) == 6:
                    position, form, lemma, pos, _, rel = line
                    if pos[0] == "N" and lemma in nouns:
                        nouns[lemma]+=1

sorted_nouns = sorted(nouns.items(), key = lambda x: -x[1])
with open("DSM_vocab_freqs.txt", "w") as fout:
    for x, y in sorted_nouns:
        print(x, y, file=fout)