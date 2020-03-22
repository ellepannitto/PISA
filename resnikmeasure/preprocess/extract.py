import os
import collections
import glob

from resnikmeasure.utils import data_utils as dutils

def extractLists(output_path, verbs_filepath, corpus_dirpath, relations_list):

    verbs = dutils.load_verbs_set(verbs_filepath)
    nouns = set()
    noun_freqs = collections.defaultdict(int)
    verb_freqs = {v:0 for v in verbs}
    freqdict = {v: collections.defaultdict(int) for v in verbs}

    # look for verb-noun pairs and their frequencies
    for filename in os.listdir(corpus_dirpath):
        print("processing file: ", filename)
        with open(corpus_dirpath+filename) as fin:
            sentence = {}
            lookfor = []
            for line in fin:
                line = line.strip()

                if not len(line) or line.startswith("#"):
                    if len(lookfor) > 0:
                        for head, lemma in lookfor:
                            if head in sentence:
                                if sentence[head] in verbs:
                                    freqdict[sentence[head]][lemma] += 1
                    sentence = {}
                    lookfor = []

                else:
                    line = line.split()
                    if len(line) == 6:
                        position, form, lemma, pos, _, rel = line
                        position = int(position)
                        rel = rel.split(",")[0].split("=")
                        if len(rel) == 2:
                            rel, head = rel
                            head = int(head)
                            if rel in relations_list and pos[0] == "N":
                                lookfor.append((head, lemma))
                                nouns.add(lemma)
                            if pos[0]=="V" and lemma in verbs:
                                verb_freqs[lemma]+=1
                            sentence[position] = lemma

            if len(lookfor) > 0:
                for head, lemma in lookfor:
                    if head in sentence:
                        if sentence[head] in verbs:
                            freqdict[sentence[head]][lemma] += 1

    # look for noun frequencies
    for filename in os.listdir(corpus_dirpath):
        print("processing file: ", filename)
        with open(corpus_dirpath+filename) as fin:
            for line in fin:
                line = line.split()
                if len(line) == 6:
                    position, form, lemma, pos, _, rel = line
                    if pos=="N" and lemma in nouns:
                        noun_freqs[lemma]+=1


    # print verb freqs
    with open(output_path+"verbs.freq", "w") as fout:
        for verb in verb_freqs:
            print(verb, verb_freqs[verb], file=fout)

    # print noun freqs
    with open(output_path+"nouns.freq", "w") as fout:
        for noun in noun_freqs:
            print(noun, noun_freqs[noun], file=fout)

    # print verb-noun freqs
    for verb in freqdict:
        with open(output_path+"output_nouns.{}".format(verb), "w") as fout:
            sorted_nouns = sorted(freqdict[verb].items(), key = lambda x: -x[1])
            for noun, f_vn in sorted_nouns:
                print(noun, f_vn, noun_freqs[noun], file=fout)


def filterLists(output_path, input_path, threshold):

    with open(input_path+"/nouns.freq") as fin, open(output_path+"/nouns.freq", "w") as fout:
        for line in fin:
            line = line.strip()
            f = int(line.split()[1])
            if f > threshold:
                print(line, file=fout)

    for filename in glob.glob(input_path+"/output_nouns.*"):
        verb = filename.split(".")[-1]
        with open(filename) as fin, open(output_path+"/output_nouns.{}"+verb, "w") as fout:
            for line in fin:
                line = line.strip()
                f = int(line.split()[2])
                if f > threshold:
                    print(line, file=fout)

