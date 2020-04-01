import os
import collections
import glob
from multiprocessing import Pool
import functools
import string
import uuid
import itertools

from resnikmeasure.utils import data_utils as dutils
from resnikmeasure.utils import os_utils as outils


def extract(output_path, verbs_filepath, corpus_dirpaths, relations, num_workers):

    iterator = dutils.grouper(outils.get_filepaths(corpus_dirpaths), 5000)
    partial = functools.partial(extractLists, output_path, verbs_filepath, relations)

    with Pool(num_workers) as p:
        p.map(partial, iterator)


def extractLists(output_path, verbs_filepath, relations_list, corpus_dirpath):

    verbs = dutils.load_verbs_set(verbs_filepath)
    nouns = set()
    noun_freqs = collections.defaultdict(int)
    verb_freqs = {v: 0 for v in verbs}
    freqdict = {v: collections.defaultdict(int) for v in verbs}

    # look for verb-noun pairs and their frequencies
    filenames = os.listdir(corpus_dirpath)
    l_filenames = len(filenames)
    for file_number, filename in enumerate(filenames):
        if not file_number % 3000:
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
                            if pos[0] == "V" and lemma in verbs:
                                verb_freqs[lemma] += 1
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
        if not file_number % 3000:
            print("PID: {} processing file n: {} out of {}".format(os.getpid(), file_number, l_filenames))
        with open(corpus_dirpath+filename) as fin:
            for line in fin:
                line = line.split()
                if len(line) == 6:
                    position, form, lemma, pos, _, rel = line
                    if pos[0] == "N" and lemma in nouns:
                        noun_freqs[lemma] += 1

    random_id = uuid.uuid4()
    # print verb freqs
    with open(output_path+"verbs.freq.{}".format(random_id), "w") as fout:
        for verb in verb_freqs:
            print(verb, verb_freqs[verb], file=fout)

    # print noun freqs
    with open(output_path+"nouns.freq.{}".format(random_id), "w") as fout:
        for noun in noun_freqs:
            print(noun, noun_freqs[noun], file=fout)

    # print verb-noun freqs
    for verb in freqdict:
        with open(output_path+"output_nouns.{}.{}".format(verb, random_id), "w") as fout:
            sorted_nouns = sorted(freqdict[verb].items(), key=lambda x: -x[1])
            for noun, f_vn in sorted_nouns:
                print(noun, f_vn, noun_freqs[noun], file=fout)


def mergeLists(dir_path):

    # nouns and verbs tot count
    counts = {"nouns": collections.defaultdict(int), "verbs": collections.defaultdict(int)}
    for el_type in counts:
        for filename in glob.glob(dir_path+"{}.freq.*".format(el_type)):
            with open(filename) as fin:
                for line in fin:
                    line = line.strip().split()
                    f = int(line[1])
                    counts[el_type][line[0]] += f
            os.remove(filename)

        with open(dir_path+"{}.freq".format(el_type), "w") as fout:
            for el in counts[el_type]:
                print(el, counts[el_type][el], file=fout)

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
    admitted_chars = string.ascii_letters + " .-"

    with open(input_path+"/nouns.freq") as fin, open(output_path+"/nouns.freq", "w") as fout:
        for line in fin:
            line = line.strip()
            f = int(line.split()[1])
            if f > threshold and all(c in admitted_chars for c in line[0]):
                print(line, file=fout)

    for filename in glob.glob(input_path+"/output_nouns.*"):
        verb = filename.split(".")[-1]
        with open(filename) as fin, open(output_path+"/output_nouns.{}".format(verb), "w") as fout:
            for line in fin:
                line = line.strip()
                f = int(line.split()[2])
                if f > threshold and all(c in admitted_chars for c in line[0]):
                    print(line, file=fout)


def filterCoverage(output_path, input_paths, models_fpath, nouns_fpath):

    models = dutils.load_models_dict(models_fpath)
    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)
    nouns_per_verb_freqs = dutils.load_nouns_per_verb_freqs(input_paths)
    nouns = dutils.load_nouns_set(nouns_fpath)

    found_nouns_per_verb = {v: {} for v in nouns_per_verb}
    for v in found_nouns_per_verb:
        found_nouns_per_verb[v] = {n: False for n in nouns_per_verb[v]}

    for model_name, model_path in models.items():
        noun_vectors = dutils.load_vectors(model_path, nouns)

        for verb in found_nouns_per_verb:
            for noun in found_nouns_per_verb[verb]:
                if noun in noun_vectors:
                    found_nouns_per_verb[verb][noun] = True

    for verb in found_nouns_per_verb:
        with open(output_path+"output_nouns.{}".format(verb), "w") as fout:
            for noun in found_nouns_per_verb[verb]:
                if found_nouns_per_verb[verb][noun]:
                    print(noun, nouns_per_verb_freqs[verb][noun], file=fout)
