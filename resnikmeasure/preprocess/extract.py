import logging
import os
import collections
import glob
from multiprocessing import Pool
import functools
import string
import uuid
import zipfile

from resnikmeasure.preprocess import wordnet_preprocess as wn_preprocess
from resnikmeasure.utils import data_utils as dutils
from resnikmeasure.utils import os_utils as outils

logger = logging.getLogger(__name__)


# TODO: add reader for corpus
def parse_ukwac(filenames, verbs, test_subject, freqdict, relations_list, nouns, verb_freqs, noun_freqs):

    l_filenames = len(filenames)
    for file_number, filename in enumerate(filenames):
        if not file_number % 3000:
            logger.info("PID: {} processing file n: {} out of {}".format(os.getpid(), file_number, l_filenames))
        if filename is not None:
            with open(filename) as fin:
                sentence = {}
                lookfor = []
                subjects = {}
                for line in fin:
                    line = line.strip()

                    if not len(line) or line.startswith("#"):
                        if len(lookfor) > 0:
                            for head, lemma in lookfor:
                                subj_passed_test, wn_chain = True, []

                                if head in sentence:
                                    lemma_head, pos_head = sentence[head]
                                    if lemma_head in verbs and pos_head == "V":

                                        if head in subjects:
                                            sbj, sbj_rel = subjects[head][0]
                                            subj_passed_test, wn_chain = test_subject(sentence[sbj][0], sbj_rel)
                                        # else:
                                        #     print("HEAD NOT IN SUBJECTS {} with {} - {}".format(sentence[head],
                                        #                                                    lemma,
                                        #                                                     subj_passed_test))
                                        #     input()

                                        if subj_passed_test:
                                            # logger.info("subject {} passed the test".format(sentence[sbj]))
                                            freqdict[sentence[head][0]][lemma] += 1
                                        else:
                                            logger.info("DISCARDING: {} {} with  {}".format(sentence[sbj][0],
                                                                                            sentence[head][0],
                                                                                            lemma))
                                            # input()
                                            logger.info("subject {} did NOT pass the test, {}".format(sentence[sbj][0],
                                                                                                        " -> ".join(
                                                                                                            wn_chain)))
                        sentence = {}
                        lookfor = []
                        subjects = {}

                    else:
                        line = line.split()
                        # print(line)
                        if len(line) == 6:
                            position, form, lemma, pos, _, rel = line
                            position = int(position)
                            rels_list = rel.split(",")
                            for el in rels_list:
                                rel = el.split("=")
                                if len(rel) == 2:
                                    rel, head = rel
                                    head = int(head)
                                    if rel in relations_list and pos[0] == "N":
                                        # print("adding object")
                                        # input()
                                        lookfor.append((head, lemma))
                                        nouns.add(lemma)
                                    if pos[0] == "V" and lemma in verbs:
                                        verb_freqs[lemma] += 1
                                    if rel.startswith("nsubj") and pos[0] == "N" and not pos in ["NNP", "NNPS"]:
                                        # print("adding subject")
                                        # input()
                                        if not head in subjects:
                                            subjects[head] = []
                                        subjects[head].append((position, rel))
                                        # print(subjects)
                                        # input()
                                    sentence[position] = (lemma, pos[0])

                if len(lookfor) > 0:
                    for head, lemma in lookfor:
                        if head in sentence:
                            lemma_head, pos_head = sentence[head]
                            if lemma_head in verbs and pos_head == "V":
                            # if lemma_head in verbs:
                                freqdict[sentence[head][0]][lemma] += 1

    # look for noun frequencies
    l_filenames = len(filenames)
    for file_number, filename in enumerate(filenames):
        if not file_number % 3000:
            logger.info("PID: {} processing file n: {} out of {}".format(os.getpid(), file_number, l_filenames))
        if filename is not None:
            with open(filename) as fin:
                for line in fin:
                    line = line.split()
                    if len(line) == 6:
                        position, form, lemma, pos, _, rel = line
                        if pos[0] == "N" and lemma in nouns:
                            noun_freqs[lemma] += 1


def parse_itwac(filenames, verbs, test_subject, freqdict, relations_list, nouns, verb_freqs, noun_freqs):
    l_filenames = len(filenames)
    for file_number, filename in enumerate(filenames):
        if not file_number % 3000:
            logger.info("PID: {} processing file n: {} out of {}".format(os.getpid(), file_number, l_filenames))
        if filename is not None:
            file_zip = zipfile.ZipFile(filename)
            inner_filename = file_zip.namelist()[0]
            logger.info(inner_filename)

            with file_zip.open(inner_filename) as fin:
                sentence = {}
                lookfor = []
                subjects = {}
                for line in fin:
                    line = line.decode().strip()
                    if not len(line) or line.startswith("<"):
                        if len(lookfor) > 0:
                            for head, lemma in lookfor:
                                subj_passed_test, wn_chain = True, []

                                if head in sentence:
                                    lemma_head, pos_head = sentence[head]
                                    if lemma_head in verbs and pos_head == "V":

                                        if head in subjects:
                                            sbj, sbj_rel = subjects[head][0]
                                            subj_passed_test, wn_chain = test_subject(sentence[sbj][0], sbj_rel)
                                        # else:
                                        #     print("HEAD NOT IN SUBJECTS {} with {} - {}".format(sentence[head],
                                        #                                                    lemma,
                                        #                                                     subj_passed_test))
                                        #     input()

                                        if subj_passed_test:
                                            # logger.info("subject {} passed the test".format(sentence[sbj]))
                                            freqdict[sentence[head][0]][lemma] += 1
                                        else:
                                            logger.info("DISCARDING: {} {} with  {}".format(sentence[sbj][0],
                                                                                            sentence[head][0],
                                                                                            lemma))
                                            # input()
                                            logger.info("subject {} did NOT pass the test, {}".format(sentence[sbj][0],
                                                                                                        " -> ".join(
                                                                                                            wn_chain)))
                        sentence = {}
                        lookfor = []
                        subjects = {}

                    else:
                        line = line.split()
                        # print(line)
                        if len(line) == 8:
                            position, form, lemma, coarse_pos, pos, _, head, rel = line
                            position = int(position)

                            head = int(head)
                            if rel in relations_list and pos[0] == "S": # serve un controllo su fine-grained pos?
                                lookfor.append((head, lemma))
                                nouns.add(lemma)

                            if pos[0] == "V" and lemma in verbs:
                                verb_freqs[lemma] += 1

                            if rel.startswith("subj") and pos[0] == "S" and not pos in ["SP"]: # controllare se esistono altri tag per nomi propri
                                if not head in subjects:
                                    subjects[head] = []
                                subjects[head].append((position, rel))
                                sentence[position] = (lemma, pos[0])

                if len(lookfor) > 0:
                    for head, lemma in lookfor:
                        if head in sentence:
                            lemma_head, pos_head = sentence[head]
                            if lemma_head in verbs and pos_head == "V":
                            # if lemma_head in verbs:
                                freqdict[sentence[head][0]][lemma] += 1

    # look for noun frequencies
    l_filenames = len(filenames)
    for file_number, filename in enumerate(filenames):
        if not file_number % 3000:
            logger.info("PID: {} processing file n: {} out of {}".format(os.getpid(), file_number, l_filenames))
        if filename is not None:
            with open(filename) as fin:
                for line in fin:
                    line = line.split()
                    if len(line) == 6:
                        position, form, lemma, pos, _, rel = line
                        if pos[0] == "N" and lemma in nouns:
                            noun_freqs[lemma] += 1


def extract(output_path, verbs_filepath, corpus_dirpaths, corpus_type, relations, num_workers, test_subject):
    if corpus_type=="ukwac":
        filenames = outils.get_filepaths(corpus_dirpaths)
    else:
        filenames = corpus_dirpaths
    logger.info("Extracting data from {} files".format(len(filenames)))
    chunk_size = len(filenames) // num_workers
    while chunk_size > 30000:
        chunk_size = chunk_size // 2

    iterator = dutils.grouper(filenames, chunk_size)
    partial = functools.partial(extractLists, output_path, verbs_filepath, relations, test_subject, corpus_type)

    with Pool(num_workers) as p:
        p.map(partial, iterator)


def extractLists(output_path, verbs_filepath, relations_list, test_subject, corpus_type, filenames):

    verbs = dutils.load_verbs_set(verbs_filepath)
    nouns = set()
    noun_freqs = collections.defaultdict(int)
    verb_freqs = {v: 0 for v in verbs}
    freqdict = {v: collections.defaultdict(int) for v in verbs}

    # look for verb-noun pairs and their frequencies
    logger.info(corpus_type)


    if corpus_type == "ukwac":
        parse_ukwac(filenames, verbs, test_subject, freqdict, relations_list, nouns, verb_freqs, noun_freqs)
    elif corpus_type == "itwac":
        parse_itwac(filenames, verbs, test_subject, freqdict, relations_list, nouns, verb_freqs, noun_freqs)

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
            if f > threshold and all(c in admitted_chars for c in line.split()[0]):
                print(line, file=fout)

    for filename in glob.glob(input_path+"/output_nouns.*"):
        verb = filename.split(".")[-1]
        with open(filename) as fin, open(output_path+"/output_nouns.{}".format(verb), "w") as fout:
            for line in fin:
                line = line.strip()
                f = int(line.split()[2])
                if f > threshold and all(c in admitted_chars for c in line.split()[0]):
                    print(line, file=fout)


def filterCoverage(output_path, input_paths, models_fpath, nouns_fpath):

    models = dutils.load_models_dict(models_fpath)
    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)
    nouns_per_verb_freqs = dutils.load_nouns_per_verb_freqs(input_paths)
    nouns = dutils.load_freq_dict(nouns_fpath)

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
                    print(noun, nouns_per_verb_freqs[verb][noun], nouns[noun], file=fout)


def filterArtifacts(output_path, input_path):
    admitted_chars = string.ascii_letters + " .-"

    with open(input_path+"/nouns.freq") as fin, open(output_path+"/nouns.freq", "w") as fout:
        for line in fin:
            line = line.strip()
            linesplit = line.split()
            lemma  = linesplit[0]
            if all(c in admitted_chars for c in lemma):
                test_result, chain = wn_preprocess.word_is_artifact(lemma)
                if test_result:
                    # print(lemma, "passed the test", "->".join(chain))
                    print(line, file=fout)
                # else:
                    # print(lemma, "NOT passed the test", "->".join(chain))
                    # input()

    for filename in glob.glob(input_path+"/output_nouns.*"):
        verb = filename.split(".")[-1]
        with open(filename) as fin, open(output_path+"/output_nouns.{}".format(verb), "w") as fout:
            for line in fin:
                line = line.strip()
                linesplit = line.split()
                lemma = linesplit[0]
                if all(c in admitted_chars for c in lemma):
                    test_result, chain = wn_preprocess.word_is_artifact(lemma)
                    if test_result:
                        # print(lemma, "passed the test", "->".join(chain))
                        print(line, file=fout)
                    # else:
                        # print(lemma, "NOT passed the test", "->".join(chain))
                        # input()


if __name__ == "__main__":
    import glob
    import resnikmeasure.preprocess.wordnet_preprocess as wn
    filenames = glob.glob("/home/ludovica/corpus/ukwac*/*")
    print(filenames)
    extractLists("/tmp/prova/", "/home/ludovica/PycharmProjects/ResnikNew/data/verb_list_resnik.txt",
                 ["nmod:with"], wn.subject_is_not_artifact, filenames)