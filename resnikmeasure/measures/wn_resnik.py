import os
from nltk.corpus import wordnet
import collections
import math

def new_compute_measure(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    nouns_per_verb = {}
    tot_verbs = {}
    tot_nouns = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        nouns_per_verb[verb] = {}
        tot_verbs[verb] = 0

        with open(input_path+filename) as fin:
            for line in fin:
                line = line.strip().split()
                noun, freq = line
                freq = int(freq)
                nouns_per_verb[verb][noun] = freq
                tot_verbs[verb]+=freq
                if not noun in tot_nouns:
                    tot_nouns[noun] = 0
                tot_nouns[noun]+=freq

    TOT = sum(tot_nouns.values())
    with open(output_path+"RESNIK_NEW.txt", "w") as fout:
        for verb in nouns_per_verb:
            print(verb, len(nouns_per_verb[verb]), tot_verbs[verb])
            # input()
            s = 0
            for noun in nouns_per_verb[verb]:
                p_n_v  = nouns_per_verb[verb][noun]/tot_verbs[verb]
                p_n = tot_nouns[noun]/TOT

                s+= p_n_v*math.log(p_n_v/p_n , 2)

                # print(noun, p_n_v, p_n)
                # input()
            print("{} {}".format(verb, s), file=fout)




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
    with open(output_path+"RESNIK.txt", "w") as fout:
        for filename in os.listdir(input_path):
            verb = filename.split(".")[-1]
            with open(input_path + filename) as fin:
                items = collections.defaultdict(float)
                tot = 0
                for line in fin:
                    line = line.strip().split()
                    noun, freq = line
                    freq = int(freq)

                    if noun in nouns_to_wordnet:
                        for ul in nouns_to_wordnet[noun]:
                            weighted_freq = freq / len(nouns_to_wordnet[noun])
                            items[ul] += weighted_freq
                            tot += weighted_freq

                s = 0
                for ul in items:
                    p_c_v = items[ul] / tot
                    p_c = category_frequencies[ul] / tot_categories
                    # print(ul)
                    # print(p_c_v, p_c)
                    # input()
                    s += p_c_v * math.log(p_c_v / p_c, 2)
                print("{} {}".format(verb, s), file=fout)