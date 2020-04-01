import itertools
import numpy as np

def load_verbs_set(filepath):
    verbs = set()
    with open(filepath) as fin:
        for line in fin:
            verbs.add(line.strip())

    return verbs


def load_models_dict(filepath):
    ret = {}
    with open(filepath) as fin:
        for line in fin:
            line = line.strip().split()
            if len(line):
                ret[line[0]] = line[1]

    return ret


def load_nouns_set(filepath):

    nouns = set()
    with open(filepath) as fin:
        for line in fin:
            line = line.strip().split()
            nouns.add(line[0])

    return nouns


def load_nouns_per_verb(input_paths):

    nouns_per_verb = {}
    tot_pairs = {}
    for filename in input_paths:
        verb = filename.split(".")[-1]
        # print(verb)
        nouns_per_verb[verb] = []
        with open(filename) as fin:
            for line in fin:
                word = line.strip().split()[0]
                nouns_per_verb[verb].append(word)

            nouns_per_verb[verb] = list(sorted(nouns_per_verb[verb]))
            tot_pairs[verb] = (len(nouns_per_verb[verb]) * (len(nouns_per_verb[verb]) - 1)) // 2

    return nouns_per_verb, tot_pairs


def load_nouns_per_verb_freqs(input_paths):

    nouns_per_verb = {}
    for filename in input_paths:
        verb = filename.split(".")[-1]
        nouns_per_verb[verb] = {}
        # print(verb)
        with open(filename) as fin:
            for line in fin:
                line = line.strip().split()
                word = line[0]
                f = line[1]
                f = int(f)
                # tot_f = int(tot_f)
                nouns_per_verb[verb][word] = f

    return nouns_per_verb


def load_vectors(model_fpath, noun_set):
    noun_vectors = {}

    with open(model_fpath) as fin_model:
        fin_model.readline()
        for line in fin_model:
            line = line.strip().split()
            word = line[0]
            if word in noun_set:
                try:
                    vector = [float(x) for x in line[1:]]
                    noun_vectors[word] = vector
                except:
                    print("problem with vector for word", word)

    min_len = min([len(vector) for vector in noun_vectors.values()])
    print("LEN VECTORS: ", min_len)
    for n in noun_vectors:
        v = noun_vectors[n][-min_len:]
        noun_vectors[n] = np.array(v)

    return noun_vectors


def load_freq_dict(filepath):
    ret = {}
    with open(filepath) as fin:
        for line in fin:
            line = line.strip().split()
            w = line[0]
            f = int(line[1])
            if w not in ret:
                ret[w] = 0
            ret[w] += f

    return ret


def load_weights(filepath):
    ret = {}
    with open(filepath) as fin:
        for line in fin:
            verb, noun, _, w = line.strip().split()
            w = float(w)
            if verb not in ret:
                ret[verb] = {}
            ret[verb][noun] = w
    return ret


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"""
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)
