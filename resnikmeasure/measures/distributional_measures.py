import os
import numpy as np
from scipy.spatial.distance import cosine
import itertools
import tqdm
from multiprocessing import Pool
import functools

def f(verb, output_path, algo, folder, nouns_per_verb, noun_vectors):
    print("START", verb, output_path, algo, folder)
    with open(output_path + algo + "." + folder + "." + verb, "w") as fout:
        for noun1 in nouns_per_verb[verb]:
            for noun2 in nouns_per_verb[verb]:
                if noun1 > noun2:
                    cos = 1 - cosine(noun_vectors[noun1], noun_vectors[noun2])
                    print(noun1, noun2, cos, file=fout)
    print("END", verb, output_path, algo, folder)

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def parallel_f(noun_vectors, tup):
#    noun_vectors, tup_list = tup
    tup_list = filter(lambda x: x is not None, tup)
    #print(os.getpid(), "START")
    #return [(n1, n2, 10) for n1, n2 in tup_list]
    return [(n1, n2, 1-cosine(noun_vectors[n1], noun_vectors[n2])) for n1, n2 in tup_list]

def compute_measure(input_path, output_path, nouns_file, n_workers):
    os.makedirs(output_path, exist_ok=True)

    nouns = set()
    with open(nouns_file) as fin:
        for line in fin:
            line = line.strip().split()
            nouns.add(line[0])

    nouns_per_verb = {}
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        print(verb)
        nouns_per_verb[verb] = []
        with open(input_path+filename) as fin:
            for line in fin:
                nouns_per_verb[verb].append(line.strip().split()[0])


    for algo in ["word2vec", "word2vecf"]:
        models_dir = "/extra/DSM/07_models/{}".format(algo)
        for folder in tqdm.tqdm(os.listdir(models_dir)):
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

            for verb in nouns_per_verb.keys():
                print("PROCESSING VERB ", verb)
                with Pool(n_workers) as p:
                    with open(output_path + algo + "." + folder + "." + verb, "w") as fout:
                        iterator = grouper(itertools.combinations(nouns_per_verb[verb], 2), 1000000)
                        tot = (len(nouns_per_verb[verb])*(len(nouns_per_verb[verb]) - 1))//(2*1000000)
                        for retlist in tqdm.tqdm(p.imap(functools.partial(parallel_f, noun_vectors), iterator), total=tot+1):
                            for n1, n2, cos in retlist:
                                print(n1, n2, cos, file=fout)
    #                        print("RICEVUTI RISULTATI")
    #                        input()


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

                for verb in nouns_per_verb.keys():
                    print("PROCESSING VERB ", verb)
                    with Pool(n_workers) as p:
                        with open(output_path + algo + "." + folder + "." + verb, "w") as fout:
                            iterator = grouper(itertools.combinations(nouns_per_verb[verb], 2), 1000000)
                            tot = (len(nouns_per_verb[verb]) * (len(nouns_per_verb[verb]) - 1)) // (2 * 1000000)
                            for retlist in tqdm.tqdm(p.imap(functools.partial(parallel_f, noun_vectors), iterator),
                                                     total=tot + 1):
                                for n1, n2, cos in retlist:
                                    print(n1, n2, cos, file=fout)
        #                        print("RICEVUTI RISULTATI")
        #                        input()
