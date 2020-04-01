import itertools
import gzip
import collections

from resnikmeasure.utils import data_utils as dutils


def weighted_distributional_measure(input_paths, models_paths, output_path, weight_fpaths):

    weight_names = [fpath.split("/")[-1].split(".")[0] for fpath in weight_fpaths]
    weights = [dutils.load_weights(fpath) for fpath in weight_fpaths]
    weights = dict(zip(weight_names, weights))
    print("weights loaded", weights.keys())
    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)
    print("nouns loaded")

    for model_filename in models_paths:
        print("working on ", model_filename)
        sp = {w: collections.defaultdict(float) for w in weights}

        print("SPDICT:", sp)

        nouns_per_verb_gen = {verb: itertools.combinations(nouns_per_verb[verb], 2) for verb in nouns_per_verb}
        first_elements = {verb: next(x) for verb, x in nouns_per_verb_gen.items()}

        with gzip.open(model_filename, "rt") as fin:

            for line_no, line in enumerate(fin):

                if not line_no % 100000:
                    print(line_no)

                w1, w2, cos = line.strip().split()
                cos = float(cos)
                tup = (w1, w2)

                update_again = True
                while update_again:
                    update = []
                    update_again = False
                    for verb in first_elements:
                        el = first_elements[verb]
                        # print("(", verb, ")", el)
                        if el < tup:
                            # print(verb, el, "not found")
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
                print("printing on", output_path + bare_model_filename + "." + w_name)
                for verb in sp[w_name]:
                    print(verb, sp[w_name][verb]/len(nouns_per_verb[verb]), file=fout_model)


def topk_distributional_measure(weight_paths, models_paths, input_paths, output_path, k):

    weight_names = [fpath.split("/")[-1].split(".")[0] for fpath in weight_paths]
    weights = [dutils.load_weights(fpath) for fpath in weight_paths]
    weights = dict(zip(weight_names, weights))
    print("weights loaded", weights.keys())
    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)
    print("nouns loaded")

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
                print(", ".join(sorted_nouns) + "\n", file=fout)
                sorted_nouns_per_verb[w][verb] = list(sorted(sorted_nouns))  # sort again in alphabetical order

    for model_filename in models_paths:
        print("working on ", model_filename)
        sp = {w: collections.defaultdict(float) for w in weights}
        n_summed = {w: collections.defaultdict(int) for w in weights}

        print("SPDICT:", sp)

        nouns_per_verb_gen = {w: {} for w in weights}
        first_elements = {w: {} for w in weights}
        for w in nouns_per_verb_gen:
            nouns_per_verb_gen[w] = {verb: itertools.combinations(sorted_nouns_per_verb[w][verb], 2)
                                     for verb in sorted_nouns_per_verb[w]}
            first_elements[w] = {verb: next(x) for verb, x in nouns_per_verb_gen[w].items()}

        with gzip.open(model_filename, "rt") as fin:
            for line_no, line in enumerate(fin):

                if not line_no % 100000:
                    print(line_no)

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
                            # print("(", verb, ")", el)
                            if el < tup:
                                # print(verb, el, "not found")
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
                print("printing on", output_path + bare_model_filename + "." + w_name)
                for verb in sp[w_name]:
                    print(verb, sp[w_name][verb]/n_summed[w_name][verb], file=fout_model)


# def temp_topk_distributional_measure(weight_fpath, models_path, output_path, k):
#     os.makedirs(output_path, exist_ok=True)
#
#     weights = {}
#     with open(weight_fpath) as fin:
#         for line in fin:
#             verb, noun, w, _ = line.strip().split()
#             w = float(w)
#             if not verb in weights:
#                 weights[verb] = {}
#             weights[verb][noun] = w
#
#     nouns_per_verb = {}
#     for verb in weights:
#         nouns_per_verb[verb] = list(sorted(weights[verb].items(), key= lambda x: -x[1]))
#
#         if k>0: nouns_per_verb[verb] = [x[0] for x in nouns_per_verb[verb][:k]]
#         else: nouns_per_verb[verb] = [x[0] for x in nouns_per_verb[verb][k:]]
#
#     if k==300 or k==-300:
#         w = weight_fpath.split("/")[-1].split(".")[0]
#         s = "300" if k>0 else "_300"
#         os.makedirs("data/sortednouns/{}/{}".format(w,s), exist_ok=True)
#
#         for verb in nouns_per_verb:
#             print("printing verb", verb)
#             with open("data/sortednouns/{}/{}/{}.txt".format(w,s,verb), "w") as fout:
#                 for noun in nouns_per_verb[verb]:
#                     print(noun, weights[verb][noun], file=fout)
