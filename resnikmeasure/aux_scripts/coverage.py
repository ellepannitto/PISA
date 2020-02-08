import os
import sys

# nouns = set()
#
# for filename in os.listdir(sys.argv[1]):
#     if filename.startswith("output_nouns"):
#         with open(sys.argv[1]+"/"+filename) as fin:
#             for line in fin:
#                 line = line.strip().split()
#                 nouns.add(line[0])

# for algo in ["word2vec", "word2vecf"]:
#     models_dir = "/extra/DSM/07_models/{}".format(algo)
#     for folder in os.listdir(models_dir):
#         print(models_dir+"/"+folder)
#         with open("found_nouns_{}_{}".format(algo, folder), "w") as fout:
#             with open(models_dir+"/"+folder+"/targets_vectors.decoded") as fin:
#                 fin.readline()
#                 for line in fin:
#                     word = line.strip().split()[0]
#                     if word in nouns:
#                         print(word, file=fout)


# algo = "SVD"
# models_dir = "/extra/DSM/07_models/SVD"
# for folder in os.listdir(models_dir):
#     print(models_dir + "/" + folder)
#     with open("found_nouns_{}_{}".format(algo, folder), "w") as fout:
#         with open(models_dir + "/" + folder + "/counts-ppmi-svd.decoded") as fin:
#             fin.readline()
#             for line in fin:
#                 word = line.strip().split()[0]
#                 if word in nouns:
#                     print(word, file=fout)

nouns = set()
with open("DSM_vocab.txt") as fin:
    for line in fin:
        nouns.add(line.strip())


for filename in os.listdir(sys.argv[1]):
    if filename.startswith("output_nouns"):
        verb = filename.split(".")[1]
#        print("processing", filename)
        found = 0
        tot = 0
        found_f = 0
        tot_f = 0
        with open(sys.argv[1]+"/"+filename) as fin, open(sys.argv[1]+"/"+"filtered.{}".format(filename), "w") as fout:
            for line in fin:
                noun, freq = line.strip().split()
                freq = int(freq)
                if noun in nouns:
                    print(line.strip(), file=fout)
                    found+=1
                    found_f += freq
                tot+=1
                tot_f +=freq
        print("{} {} {} {:.2f} {} {} {:.2f}".format(verb, found, tot, found*100/tot, found_f, tot_f, found_f*100/tot_f))