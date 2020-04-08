import logging
import itertools
import gzip
import collections
import os
import functools
from multiprocessing import Pool

from resnikmeasure.utils import data_utils as dutils

logger = logging.getLogger(__name__)


def parallel_weighted_distributional_measure(input_paths, output_path, weight_fpaths, model_filename):
    weight_names = [fpath.split("/")[-1].split(".")[0] for fpath in weight_fpaths]
    weights = [dutils.load_weights(fpath) for fpath in weight_fpaths]
    weights = dict(zip(weight_names, weights))
    logger.info("weights loaded {}".format(weights.keys()))
    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)
    logger.info("nouns loaded")

    logger.info("PID: {} - working on {}".format(os.getpid(), model_filename))
    sp = {w: collections.defaultdict(float) for w in weights}

    nouns_per_verb_gen = {verb: itertools.combinations(nouns_per_verb[verb], 2) for verb in nouns_per_verb}
    first_elements = {verb: next(x) for verb, x in nouns_per_verb_gen.items()}

    with gzip.open(model_filename, "rt") as fin:

        for line_no, line in enumerate(fin):

            if not line_no % 100000:
                logger.info("PID: {} - {}".format(os.getpid(), line_no))

            w1, w2, cos = line.strip().split()
            cos = float(cos)
            tup = (w1, w2)

            update_again = True
            while update_again:
                update = []
                update_again = False
                for verb in first_elements:
                    el = first_elements[verb]
                    if el < tup:
                        update.append(verb)
                        update_again = True
                    elif el == tup:
                        for w in sp:
                            sp[w][verb] += weights[w][verb][el[0]]*cos
                            sp[w][verb] += weights[w][verb][el[1]]*cos
                        update.append(verb)

                for v in update:
                    try:
                        first_elements[v] = next(nouns_per_verb_gen[v])
                    except StopIteration:
                        del first_elements[v]

    bare_model_filename = model_filename.split("/")[-1][:-12]  # remove ".merged.gzip"

    for w_name in weights:
        with open(output_path + bare_model_filename + "." + w_name, "w") as fout_model:
            print("PID: {} - printing on {}".format(os.getpid(), output_path + bare_model_filename + "." + w_name))
            for verb in sp[w_name]:
                print(verb, sp[w_name][verb]/len(nouns_per_verb[verb]), file=fout_model)


def weighted_distributional_measure(input_paths, models_paths, output_path, weight_fpaths):

    with Pool(4) as p:
        p.map(functools.partial(parallel_weighted_distributional_measure, input_paths,
                                output_path, weight_fpaths), models_paths)


def parallel_topk_distributional_measure(weights, sorted_nouns_per_verb, output_path, model_filename):

    # TODO: change production of selected_nouns file

    logger.info("working on {}".format(model_filename))
    sp = {w: collections.defaultdict(float) for w in weights}
    n_summed = {w: collections.defaultdict(int) for w in weights}


    nouns_per_verb_gen = {w: {} for w in weights}
    first_elements = {w: {} for w in weights}
    for w in nouns_per_verb_gen:
        nouns_per_verb_gen[w] = {verb: itertools.combinations(sorted_nouns_per_verb[w][verb], 2)
                                 for verb in sorted_nouns_per_verb[w]}
        first_elements[w] = {verb: next(x) for verb, x in nouns_per_verb_gen[w].items()}

    with gzip.open(model_filename, "rt") as fin:
        for line_no, line in enumerate(fin):

            if not line_no % 100000:
                logger.info(line_no)

            w1, w2, cos = line.strip().split()
            cos = float(cos)
            tup = (w1, w2)

            for w_name in weights:
                update_again = True
                while update_again:
                    update = []
                    update_again = False
                    for verb in first_elements[w_name]:
                        el = first_elements[w_name][verb]
                        if el < tup:
                            update.append(verb)
                            update_again = True
                        elif el == tup:
                            sp[w_name][verb] += cos
                            n_summed[w_name][verb] += 1
                            update.append(verb)

                    for v in update:
                        try:
                            first_elements[w_name][v] = next(nouns_per_verb_gen[w_name][v])
                        except StopIteration:
                            del first_elements[w_name][v]

    bare_model_filename = model_filename.split("/")[-1][:-12]  # remove ".merged.gzip"

    for w_name in weights:
        with open(output_path + bare_model_filename + "." + w_name, "w") as fout_model:
            logger.info("PID: {} - printing on {}".format(os.getpid(), output_path + bare_model_filename + "." + w_name))
            for verb in sp[w_name]:
                print(verb, sp[w_name][verb]/n_summed[w_name][verb], file=fout_model)


def topk_distributional_measure(weight_paths, models_paths, input_paths, output_path, k):

    weight_names = [fpath.split("/")[-1].split(".")[0] for fpath in weight_paths]
    weights = [dutils.load_weights(fpath) for fpath in weight_paths]
    weights = dict(zip(weight_names, weights))
    logger.info("weights loaded {}".format(weights.keys()))
    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)
    logger.info("nouns loaded")

    sorted_nouns_per_verb = {}

    with open(output_path+"selected_nouns.txt", "w") as fout:
        for w in weights:
            print("**", w, "**", file=fout)
            sorted_nouns_per_verb[w] = {}
            for verb in nouns_per_verb:
                print("*", verb, "*", file=fout)
                sorted_nouns = sorted(nouns_per_verb[verb], key=lambda x: weights[w][verb][x])
                if k > 0:
                    sorted_nouns = [x for x in sorted_nouns[:k]]
                else:
                    sorted_nouns = [x for x in reversed(sorted_nouns[k:])]

                for selected_noun in sorted_nouns:
                    print(selected_noun, weights[w][verb][selected_noun], file=fout)
                    print("", file=fout)
                print(", ".join(sorted_nouns) + "\n", file=fout)
                sorted_nouns_per_verb[w][verb] = list(sorted(sorted_nouns))  # sort again in alphabetical order

    with Pool(4) as p:
        p.map(functools.partial(parallel_topk_distributional_measure, weights,
                                sorted_nouns_per_verb, output_path), models_paths)