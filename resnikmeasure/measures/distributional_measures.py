import os
import numpy as np
from scipy.spatial.distance import cosine
import collections
import tqdm

def compute_measure(input_path, output_path, nouns_file, algo):
    os.makedirs(output_path, exist_ok=True)

    nouns = set()
    with open(nouns_file) as fin:
        for line in fin:
            line = line.strip().split()
            nouns.add(line[0])

    nouns_per_verb = {}
    pairs = collections.defaultdict(int)
    for filename in os.listdir(input_path):
        verb = filename.split(".")[-1]
        print(verb)
        nouns_per_verb[verb] = []
        with open(input_path+filename) as fin:
            for line in fin:
                nouns_per_verb[verb].append(line.strip().split()[0])
            # for noun1 in nouns_per_verb[verb]:
            #     for noun2 in nouns_per_verb[verb]:
            #         if noun1 > noun2:
            #             pairs[(noun1, noun2)]+=1


    if algo in ["word2vec", "word2vecf"]:
        models_dir = "/extra/DSM/07_models/{}".format(algo)
        for folder in tqdm.tqdm(os.listdir(models_dir)):
            print(folder)
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
            print(min_len)
            for n in noun_vectors:
                v = noun_vectors[n][-min_len:]
                noun_vectors[n] = np.array(v)

            for verb in tqdm.tqdm(nouns_per_verb):
                with open(output_path + algo + "." + folder + "." + verb, "w") as fout:
                    for noun1 in tqdm.tqdm(nouns_per_verb[verb]):
                        for noun2 in nouns_per_verb[verb]:
                            if noun1 > noun2:
                                cos = 1 - cosine(noun_vectors[noun1], noun_vectors[noun2])
                                print(noun1, noun2, cos, file=fout)

    elif algo in ["SVD"]:
        models_dir = "/extra/DSM/07_models/{}".format(algo)
        for folder in tqdm.tqdm(os.listdir(models_dir)):
            print(folder)
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
            print(min_len)
            for n in noun_vectors:
                v = noun_vectors[n][-min_len:]
                noun_vectors[n] = np.array(v)

            for verb in tqdm.tqdm(nouns_per_verb):
                with open(output_path + algo + "." + folder + "." + verb, "w") as fout:
                    for noun1 in tqdm.tqdm(nouns_per_verb[verb]):
                        for noun2 in nouns_per_verb[verb]:
                            if noun1 > noun2:
                                cos = 1 - cosine(noun_vectors[noun1], noun_vectors[noun2])
                                print(noun1, noun2, cos, file=fout)
