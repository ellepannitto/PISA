import os
from nltk.corpus import wordnet
import collections
import math

def compute_measure(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    nouns_to_wordnet = {}
    category_frequencies = collections.defaultdict(float)

    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]

        with open(input_path+filename) as fin:
            items = collections.defaultdict(float)
            tot = 0
            for line in fin:
                line = line.strip().split()
                noun, freq = line
                freq = int(freq)
                if not noun in nouns_to_wordnet:
                    nouns_to_wordnet[noun] = set()
                    for synset in wordnet.synsets(noun, pos='n', lang="eng"):
                        for el in synset.hypernym_paths():
                            for ul in el:
                                nouns_to_wordnet[noun].add(ul)

                for ul in nouns_to_wordnet[noun]:
                    weighted_freq = freq / len(nouns_to_wordnet[noun])
                    category_frequencies[ul]+=weighted_freq

    tot_categories = sum(category_frequencies.values())
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        with open(input_path + filename) as fin:
            items = collections.defaultdict(float)
            tot = 0
            for line in fin:
                line = line.strip().split()
                noun, freq = line
                freq = int(freq)

                for ul in nouns_to_wordnet[noun]:
                    weighted_freq = freq / len(nouns_to_wordnet[noun])
                    items[ul] += weighted_freq
                    tot += weighted_freq
            s = 0
            for ul in items:
                p_c_v = items[ul] / tot
                p_c = category_frequencies[ul] / tot_categories
                s += p_c_v * math.log(p_c_v / p_c, 2)
            print("{} {}".format(verb, s))
            input()