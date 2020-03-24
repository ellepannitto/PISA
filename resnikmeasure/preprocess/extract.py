import os
import collections
import glob
from multiprocessing import Pool
import functools

from resnikmeasure.utils import data_utils as dutils

def extract(output_path, verbs_filepath, corpus_dirpaths, relations, num_workers):
    partial = functools.partial(extractLists, output_path, verbs_filepath, relations)

    with Pool(num_workers) as p:
        p.map(partial, corpus_dirpaths)


def extractLists(output_path, verbs_filepath, relations_list, corpus_dirpath):

    verbs = dutils.load_verbs_set(verbs_filepath)
    nouns = set()
    noun_freqs = collections.defaultdict(int)
    verb_freqs = {v:0 for v in verbs}
    freqdict = {v: collections.defaultdict(int) for v in verbs}

    # look for verb-noun pairs and their frequencies
    filenames = os.listdir(corpus_dirpath)
    l_filenames = len(filenames)
    for file_number, filename in enumerate(filenames):
        if not file_number%3000:
            print("PID: {} processing file n: {} out of {}".format(os.getpid(), file_number, l_filenames))
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
    filenames = os.listdir(corpus_dirpath)
    l_filenames = len(filenames)
    for file_number, filename in enumerate(filenames):
        if not file_number%3000:
            print("PID: {} processing file n: {} out of {}".format(os.getpid(), file_number, l_filenames))
        with open(corpus_dirpath+filename) as fin:
            for line in fin:
                line = line.split()
                if len(line) == 6:
                    position, form, lemma, pos, _, rel = line
                    if pos[0]=="N" and lemma in nouns:
                        noun_freqs[lemma]+=1


    # print verb freqs
    with open(output_path+"verbs.freq.{}".format(os.getpid()), "w") as fout:
        for verb in verb_freqs:
            print(verb, verb_freqs[verb], file=fout)

    # print noun freqs
    with open(output_path+"nouns.freq.{}".format(os.getpid()), "w") as fout:
        for noun in noun_freqs:
            print(noun, noun_freqs[noun], file=fout)

    # print verb-noun freqs
    for verb in freqdict:
        with open(output_path+"output_nouns.{}.{}".format(verb, os.getpid()), "w") as fout:
            sorted_nouns = sorted(freqdict[verb].items(), key = lambda x: -x[1])
            for noun, f_vn in sorted_nouns:
                print(noun, f_vn, noun_freqs[noun], file=fout)


def mergeLists(dir_path):

    # nouns and verbs tot count
    counts = {"nouns": collections.defaultdict(int), "verbs":collections.defaultdict(int)}
    for type in counts:
        for filename in glob.glob(dir_path+"{}.freq.*".format(type)):
            with open(filename) as fin:
                for line in fin:
                    line = line.strip().split()
                    f = int(line[1])
                    counts[type][line[0]] += f
            os.remove(filename)

        with open(dir_path+"{}.freq".format(type), "w") as fout:
            for el in counts[type]:
                print(el, counts[type][el], file=fout)

    # nouns per verb
    verbs = counts["verbs"].keys()
    for verb in verbs:
        counts_for_verb = collections.defaultdict(int)
        for filename in glob.glob(dir_path + "output_nouns.{}.*".format(verb)):
            with open(filename) as fin:
                for line in fin:
                    line = line.strip().split()
                    f = int(line[1])
                    counts_for_verb[line[0]] += f
            os.remove(filename)

        with open(dir_path + "output_nouns.{}".format(verb), "w") as fout:
            for el in counts_for_verb:
                print(el, counts_for_verb[el], counts["nouns"][el], file=fout)

def filterLists(output_path, input_path, threshold):

    with open(input_path+"/nouns.freq") as fin, open(output_path+"/nouns.freq", "w") as fout:
        for line in fin:
            line = line.strip()
            f = int(line.split()[1])
            if f > threshold:
                print(line, file=fout)

    for filename in glob.glob(input_path+"/output_nouns.*"):
        verb = filename.split(".")[-1]
        with open(filename) as fin, open(output_path+"/output_nouns.{}".format(verb), "w") as fout:
            for line in fin:
                line = line.strip()
                f = int(line.split()[2])
                if f > threshold:
                    print(line, file=fout)

