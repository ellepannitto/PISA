import os
import numpy as np
from scipy.spatial.distance import cosine

def compute_measure(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    for filename in os.listdir(input_path):
        nouns = set()
        with open(input_path+filename) as fin:
            for line in fin:
                nouns.add(line.strip().split()[0])

        for algo in ["word2vec", "word2vecf"]:
            models_dir = "/extra/DSM/07_models/{}".format(algo)
            for folder in os.listdir(models_dir):
                print(folder)
                with open(models_dir + "/" + folder + "/targets_vectors.decoded") as fin_model:
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
                with open(output_path+"{}.{}.{}".format(algo, folder, filename), "w") as fout:
                    for noun1 in noun_vectors:
                        for noun2 in noun_vectors:
                            if noun1 < noun2:
                                cos = 1 - cosine(noun_vectors[noun1], noun_vectors[noun2])
                                print(noun1, noun2, cos, file=fout)

        algo = "SVD"
        models_dir = "/extra/DSM/07_models/SVD"
        for folder in os.listdir(models_dir):
            print(models_dir + "/" + folder)
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
                with open(output_path + "{}.{}.{}".format(algo, folder, filename), "w") as fout:
                    for noun1 in noun_vectors:
                        for noun2 in noun_vectors:
                            if noun1 < noun2:
                                cos = 1 - cosine(noun_vectors[noun1], noun_vectors[noun2])
                                print(noun1, noun2, cos, file=fout)
