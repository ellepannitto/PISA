import os
import numpy as np
from scipy.spatial.distance import cosine
import itertools
import tqdm
from multiprocessing import Pool
import functools
import heapq
import gzip
import collections
import math


def tuples_generator(nouns_per_verb):
    files = [itertools.combinations(nouns_per_verb[verb], 2) for verb in nouns_per_verb]
    last_tuple = None
    for tuple in heapq.merge(*files):
        if not tuple == last_tuple:
            yield tuple
            last_tuple = tuple

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

files_dict = {}
def parallel_f(noun_vectors, file_prefix, tup):

    global files_dict

    pid = os.getpid()
    if not pid in files_dict:
        files_dict[pid] = gzip.open(file_prefix+".{}.gzip".format(pid), "wt")
        print(pid, "OPENING FILE", file_prefix+".{}.gzip".format(pid))

    tup_list = filter(lambda x: x is not None, tup)
    for n1, n2 in tup_list:
        print(n1, n2, "{:.4f}".format(1-cosine(noun_vectors[n1], noun_vectors[n2])), file=files_dict[pid])

def temp_topk_distributional_measure(weight_fpath, models_path, output_path, k):
    os.makedirs(output_path, exist_ok=True)

    weights = {}
    with open(weight_fpath) as fin:
        for line in fin:
            verb, noun, w, _ = line.strip().split()
            w = float(w)
            if not verb in weights:
                weights[verb] = {}
            weights[verb][noun] = w

    nouns_per_verb = {}
    for verb in weights:
        nouns_per_verb[verb] = list(sorted(weights[verb].items(), key= lambda x: -x[1]))

        if k>0: nouns_per_verb[verb] = [x[0] for x in nouns_per_verb[verb][:k]]
        else: nouns_per_verb[verb] = [x[0] for x in nouns_per_verb[verb][k:]]

    if k==300 or k==-300:
        w = weight_fpath.split("/")[-1].split(".")[0]
        s = "300" if k>0 else "_300"
        os.makedirs("data/sortednouns/{}/{}".format(w,s), exist_ok=True)

        for verb in nouns_per_verb:
            print("printing verb", verb)
            with open("data/sortednouns/{}/{}/{}.txt".format(w,s,verb), "w") as fout:
                for noun in nouns_per_verb[verb]:
                    print(noun, weights[verb][noun], file=fout)

def topk_distributional_measure(weight_fpath, models_path, output_path, k):
    os.makedirs(output_path, exist_ok=True)

    weights = {}
    with open(weight_fpath) as fin:
        for line in fin:
            verb, noun, _, w = line.strip().split()
            w = float(w)
            if not verb in weights:
                weights[verb] = {}
            weights[verb][noun] = w

    # print(len(weights))
    # input()
    # for verb in weights:
    #     print(verb, len(weights[verb]))
    # input()

    nouns_per_verb = {}
    for verb in weights:
        nouns_per_verb[verb] = list(sorted(weights[verb].items(), key= lambda x: -x[1]))

        if k>0: nouns_per_verb[verb] = [x[0] for x in nouns_per_verb[verb][:k]]
        else: nouns_per_verb[verb] = [x[0] for x in nouns_per_verb[verb][k:]]

    if k == 300 or k == -300:
        w = weight_fpath.split("/")[-1].split(".")[0]
        s = "300" if k > 0 else "_300"
        os.makedirs("data/sortednouns/{}/{}".format(w, s), exist_ok=True)

        for verb in nouns_per_verb:
            print("printing verb", verb)
            with open("data/sortednouns/{}/{}/{}.txt".format(w, s, verb), "w") as fout:
                for noun in nouns_per_verb[verb]:
                    print(noun, weights[verb][noun], file=fout)

    for verb in nouns_per_verb:
        nouns_per_verb[verb] = list(sorted(nouns_per_verb[verb]))
    print("nouns loaded")

    with open(output_path+"LOG", "w") as fout:
        for model_filename in os.listdir(models_path):

            print("working on ", model_filename)
            sp = collections.defaultdict(float)
            n_summed = collections.defaultdict(int)
            nouns_per_verb_gen = {verb: itertools.combinations(nouns_per_verb[verb], 2) for verb in nouns_per_verb}
            first_elements = {verb: next(x) for verb, x in nouns_per_verb_gen.items()}

        #    print(first_elements)
        #    input()
            with gzip.open(models_path+model_filename, "rt") as fin:
                for line_no, line in enumerate(tqdm.tqdm(fin)):
                    update = []
                    w1, w2, cos = line.strip().split()
                    cos = float(cos)
                    tup = (w1, w2)
                    # print("looking for", tup)

                    for verb in first_elements:
                        el = first_elements[verb]
                        if el < tup:
                            # print(tup, "not found", file=fout)
                            update.append(verb)
                        elif el == tup:
                            sp[verb]+=cos
                            n_summed[verb]+=1
                            update.append(verb)

                    for v in update:
                        try:
                            first_elements[v] = next(nouns_per_verb_gen[v])
                        except StopIteration:
                            del first_elements[v]
                        # print(first_elements)
                        # input()

            bare_model_filename = ".".join(model_filename.split(".")[:-2])
            with open(output_path+bare_model_filename, "w") as fout_model:
                print(model_filename, file=fout)
                for verb in sp:
                    print(verb, sp[verb]/n_summed[verb], file=fout_model)

def weighted_distributional_measure(input_path, models_path, output_path, weight_fpath):
    os.makedirs(output_path, exist_ok=True)


    weights = {}
    with open(weight_fpath) as fin:
        for line in fin:
            verb, noun, _, w = line.strip().split()
            w = float(w)
            if not verb in weights:
                weights[verb] = {}
            weights[verb][noun] = w

    print("weights loaded")


    nouns_per_verb = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        print(verb)
        nouns_per_verb[verb] = []
        with open(input_path+filename) as fin:
            for line in fin:
                word = line.strip().split()[0]
                nouns_per_verb[verb].append(word)

            nouns_per_verb[verb] = list(sorted(nouns_per_verb[verb]))

    print("nouns loaded")

    with open(output_path+"LOG", "w") as fout:
        for model_filename in os.listdir(models_path):
            print("working on ", model_filename)
            sp = collections.defaultdict(float)
            nouns_per_verb_gen = {verb: itertools.combinations(nouns_per_verb[verb], 2) for verb in nouns_per_verb}
            first_elements = {verb: next(x) for verb, x in nouns_per_verb_gen.items()}
            with gzip.open(models_path+model_filename, "rt") as fin:
                for line_no, line in enumerate(tqdm.tqdm(fin)):

                    if not line_no%10000000:
                        print(sp)

                    update = []
                    w1, w2, cos = line.strip().split()
                    cos = float(cos)
                    tup = (w1, w2)

                    for verb in first_elements:
                        el = first_elements[verb]
                        if el < tup:
                            print(tup, "not found", file=fout)
                            update.append(verb)
                        elif el == tup:
                            sp[verb]+=weights[verb][el[0]]*cos
                            sp[verb]+=weights[verb][el[1]]*cos
                            update.append(verb)

                    for v in update:
                        try:
                            first_elements[v] = next(nouns_per_verb_gen[v])
                        except StopIteration:
                            del first_elements[v]

            bare_model_filename = ".".join(model_filename.split(".")[:-2])
            with open(output_path + bare_model_filename, "w") as fout_model:
                print(model_filename, file=fout)
                for verb in sp:
                    print(verb, sp[verb]/len(nouns_per_verb[verb]), file=fout_model)


def compute_cosines(input_path, output_path, nouns_file, n_workers):
    global files_dict

    os.makedirs(output_path, exist_ok=True)

    nouns = set()
    with open(nouns_file) as fin:
        for line in fin:
            line = line.strip().split()
            nouns.add(line[0])

    nouns_per_verb = {}
    tot_pairs = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        print(verb)
        nouns_per_verb[verb] = []
        with open(input_path+filename) as fin:
            for line in fin:
                word = line.strip().split()[0]
                nouns_per_verb[verb].append(word)

            nouns_per_verb[verb] = list(sorted(nouns_per_verb[verb]))
            tot_pairs[verb] = (len(nouns_per_verb[verb]) * (len(nouns_per_verb[verb]) - 1)) // 2


    for algo in ["word2vec", "word2vecf"]:
        models_dir = "/extra/DSM/07_models/{}".format(algo)
        for folder in os.listdir(models_dir):
            print("WORKING ON FOLDER: ", folder)
            with open(models_dir + "/" + folder + "/targets_vectors.decoded") as fin_model:
                noun_vectors = {}
                fin_model.readline()
                for line in fin_model:
                    line = line.strip().split()
                    word = line[0]
                    if word in nouns:
                        try:
                            vector = [float(x) for x in line[1:]]
                            noun_vectors[word] = vector
                        except:
                            pass

            min_len = min([len(vector) for vector in noun_vectors.values()])
            print("LEN VECTORS: ", min_len)
            for n in noun_vectors:
                v = noun_vectors[n][-min_len:]
                noun_vectors[n] = np.array(v)

            file_prefix = output_path + algo + "." + folder
            with Pool(n_workers) as p:
                iterator = grouper(tuples_generator(nouns_per_verb), 500000)
                imap_obj = p.imap(functools.partial(parallel_f, noun_vectors, file_prefix), iterator)

                for x in tqdm.tqdm (imap_obj, total=sum(tot_pairs.values()) // 500000) :
                    pass

            for pid in files_dict:
                files_dict[pid].close()
                print(pid, "CLOSING FILE")
                del files_dict[pid]


    for algo in ["SVD"]:
        models_dir = "/extra/DSM/07_models/{}".format(algo)
        for folder in tqdm.tqdm(os.listdir(models_dir)):
            print("WORKING ON FOLDER: ", folder)
            with open(models_dir + "/" + folder + "/counts-ppmi-svd.decoded") as fin_model:
                noun_vectors = {}
                fin_model.readline()
                for line in fin_model:
                    line = line.strip().split()
                    word = line[0]
                    if word in nouns:
                        try:
                            vector = np.array([float(x) for x in line[1:]])
                            noun_vectors[word] = vector
                        except:
                            pass

            min_len = min([len(vector) for vector in noun_vectors.values()])
            print("LEN VECTORS: ", min_len)
            for n in noun_vectors:
                v = noun_vectors[n][-min_len:]
                noun_vectors[n] = np.array(v)

            file_prefix = output_path + algo + "." + folder
            with Pool(n_workers) as p:
                iterator = grouper(tuples_generator(nouns_per_verb), 500000)
                imap_obj = p.imap(functools.partial(parallel_f, noun_vectors, file_prefix), iterator)

                for x in tqdm.tqdm(imap_obj, total=sum(tot_pairs.values()) // 500000):
                    pass

            for pid in files_dict:
                files_dict[pid].close()
                print(pid, "CLOSING FILE")
                del files_dict[pid]


def compute_identity_weight(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    nouns_per_verb = {}
    tot_verb = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        nouns_per_verb[verb] = {}
        with open(input_path+filename) as fin:
            for line in fin:
                word = line.strip().split()[0]
                nouns_per_verb[verb][word] = 1
        tot_verb[verb] = sum(nouns_per_verb[verb].values())

    with open(output_path+"ID.txt", "w") as fout:
        for verb in nouns_per_verb:
            print(verb)
            for noun in nouns_per_verb[verb]:
                print(verb, noun, nouns_per_verb[verb][noun], nouns_per_verb[verb][noun]/tot_verb[verb], file=fout)

def compute_frequency_weight(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    nouns_per_verb = {}
    tot_verb = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        nouns_per_verb[verb] = {}
        with open(input_path+filename) as fin:
            for line in fin:
                word, freq = line.strip().split()
                freq = int(freq)
                nouns_per_verb[verb][word] = freq
        tot_verb[verb] = sum(nouns_per_verb[verb].values())

    with open(output_path+"FREQ.txt", "w") as fout:
        for verb in nouns_per_verb:
            print(verb)
            for noun in nouns_per_verb[verb]:
                print(verb, noun, nouns_per_verb[verb][noun], nouns_per_verb[verb][noun]/tot_verb[verb], file=fout)

def compute_idf_weight(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    verbs_per_noun = collections.defaultdict(list)
    nouns_per_verb = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        nouns_per_verb[verb] = {}
        with open(input_path+filename) as fin:
            for line in fin:
                word, freq = line.strip().split()
                nouns_per_verb[verb][word] = 1
                verbs_per_noun[word].append(verb)

    # C = sum(len(nouns_verb_pairs[word]) for word in nouns_verb_pairs)
    C = len(nouns_per_verb)

    tot_verb = {}
    for verb in nouns_per_verb:
        for noun in nouns_per_verb[verb]:
            nouns_per_verb[verb][noun] = math.log(C/len(verbs_per_noun[noun]), 2)
        tot_verb[verb] = sum(nouns_per_verb[verb].values())

    with open(output_path+"IDF.txt", "w") as fout:
        for verb in nouns_per_verb:
            print(verb)
            for noun in nouns_per_verb[verb]:
                print(verb, noun,
                      nouns_per_verb[verb][noun],
                      nouns_per_verb[verb][noun]/tot_verb[verb],
                      file=fout)

def compute_entropy_weight(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    nouns = collections.defaultdict(int)
    nouns_per_verb = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        nouns_per_verb[verb] = collections.defaultdict(int)
        with open(input_path+filename) as fin:
            for line in fin:
                word, freq = line.strip().split()
                freq = int(freq)
                nouns_per_verb[verb][word] = freq
                nouns[word]+=freq

    entropies = {}
    max = 0
    for noun in nouns:
        e = 0
        for verb in nouns_per_verb:
            p = nouns_per_verb[verb][noun]/nouns[noun]
            if p > 0:
                e -= p*math.log(p, 2)
        if e>max:
            max = e
        entropies[noun] = e
    for noun in entropies:
        entropies[noun] = -entropies[noun] + max

    tot_verb = {}
    for verb in nouns_per_verb:
        tot_verb[verb] = 0
        for noun in nouns_per_verb[verb]:
            tot_verb[verb] += entropies[noun]



    with open(output_path+"ENTROPY.txt", "w") as fout:
        for verb in nouns_per_verb:
            print(verb)
            for noun in nouns_per_verb[verb]:
                print(verb, noun, entropies[noun], entropies[noun]/tot_verb[verb], file=fout)