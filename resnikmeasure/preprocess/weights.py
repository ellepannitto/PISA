import math

from resnikmeasure.utils import data_utils as dutils

def compute_identity_weight(input_paths, output_path):

    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)

    id_w_nouns_per_verb = {}
    tot_w_per_verb = {}
    for verb in nouns_per_verb:
        id_w_nouns_per_verb[verb] = {noun: 1 for noun in nouns_per_verb[verb]}
        tot_w_per_verb[verb] = sum(id_w_nouns_per_verb[verb].values())

    with open(output_path+"ID.txt", "w") as fout:
        for verb in id_w_nouns_per_verb:
            for noun in id_w_nouns_per_verb[verb]:
                abs_w = id_w_nouns_per_verb[verb][noun]
                rel_w = id_w_nouns_per_verb[verb][noun]/tot_w_per_verb[verb]
                print(verb, noun, abs_w, rel_w, file=fout)


def compute_frequency_weight(input_paths, output_path):

    freq_w_nouns_per_verb = dutils.load_nouns_per_verb_freqs(input_paths)
    tot_w_per_verb = {verb: sum(freq_w_nouns_per_verb[verb].values()) for verb in freq_w_nouns_per_verb}

    with open(output_path+"FREQ.txt", "w") as fout:
        for verb in freq_w_nouns_per_verb:
            print(verb)
            for noun in freq_w_nouns_per_verb[verb]:
                abs_w = freq_w_nouns_per_verb[verb][noun]
                rel_w = freq_w_nouns_per_verb[verb][noun]/tot_w_per_verb[verb]
                print(verb, noun, abs_w, rel_w, file=fout)

def compute_lmi_weight(input_paths, output_path, noun_freq_path, verb_freq_path):

    verb_freqs = dutils.load_freq_dict(verb_freq_path)
    noun_freqs = dutils.load_freq_dict(noun_freq_path)
    ukwac_size = 1900000000

    freq_w_nouns_per_verb = dutils.load_nouns_per_verb_freqs(input_paths)

    lmi_w_nouns_per_verb = {}
    for verb in freq_w_nouns_per_verb:
        lmi_w_nouns_per_verb[verb] = {}
        for noun in freq_w_nouns_per_verb[verb]:
            f_nv = freq_w_nouns_per_verb[verb][noun]
            p_nv = f_nv/ukwac_size
            f_v = verb_freqs[verb]
            p_v = f_v/ukwac_size
            f_n = noun_freqs[noun]
            p_n = f_n/ukwac_size

            lmi = f_nv * math.log(p_nv/(p_n*p_v), 2)

            lmi_w_nouns_per_verb[verb][noun] = lmi

    tot_w_per_verb = {verb: sum(lmi_w_nouns_per_verb[verb].values()) for verb in lmi_w_nouns_per_verb}

    with open(output_path+"LMI.txt", "w") as fout:
        for verb in lmi_w_nouns_per_verb:
            for noun in lmi_w_nouns_per_verb[verb]:
                abs_w = lmi_w_nouns_per_verb[verb][noun]
                rel_w = lmi_w_nouns_per_verb[verb][noun]/tot_w_per_verb[verb]
                print(verb, noun, abs_w, rel_w, file=fout)


def compute_idf_weight(input_paths, output_path):

    nouns_per_verb, _ = dutils.load_nouns_per_verb(input_paths)
    verbs_per_noun = {}
    for verb in nouns_per_verb:
        for noun in nouns_per_verb[verb]:
            if not noun in verbs_per_noun:
                verbs_per_noun[noun] = []
            verbs_per_noun[noun].append(verb)

    C = len(nouns_per_verb)

    w_nouns_per_verb = {}
    for verb in nouns_per_verb:
        w_nouns_per_verb[verb] = {}
        for noun in nouns_per_verb[verb]:
            w_nouns_per_verb[verb][noun] = math.log(C/len(verbs_per_noun[noun]), 2)

    tot_w_per_verb = {verb: sum(w_nouns_per_verb[verb].values()) for verb in w_nouns_per_verb}

    with open(output_path+"IDF.txt", "w") as fout:
        for verb in w_nouns_per_verb:
            for noun in w_nouns_per_verb[verb]:
                abs_w = w_nouns_per_verb[verb][noun]
                rel_w = w_nouns_per_verb[verb][noun]/tot_w_per_verb[verb]
                print(verb, noun, abs_w, rel_w, file=fout)

def compute_entropy_weight(input_paths, output_path, noun_freq_path):

    noun_freqs = dutils.load_freq_dict(noun_freq_path)

    freq_w_nouns_per_verb = dutils.load_nouns_per_verb_freqs(input_paths)

    ent_w_nouns_per_verb = {verb: {} for verb in freq_w_nouns_per_verb}
    for noun in noun_freqs:
        e = 0
        for verb in freq_w_nouns_per_verb:
            if noun in freq_w_nouns_per_verb[verb]:
                p = freq_w_nouns_per_verb[verb][noun]/noun_freqs[noun]
                if p > 0:
                    e-= p * math.log(p, 2)
        for verb in ent_w_nouns_per_verb:
            ent_w_nouns_per_verb[verb][noun] = e

    tot_w_per_verb = {verb: sum(ent_w_nouns_per_verb[verb].values()) for verb in ent_w_nouns_per_verb}
            # entropies[noun] = -entropies[noun] + max


    with open(output_path + "ENTROPY.txt", "w") as fout:
        for verb in ent_w_nouns_per_verb:
            for noun in ent_w_nouns_per_verb[verb]:
                abs_w = ent_w_nouns_per_verb[verb][noun]
                rel_w = ent_w_nouns_per_verb[verb][noun] / tot_w_per_verb[verb]
                print(verb, noun, abs_w, rel_w, file=fout)

def compute_inner_entropy_weight(input_paths, output_path):

    noun_freqs = {}

    freq_w_nouns_per_verb = dutils.load_nouns_per_verb_freqs(input_paths)

    for verb in freq_w_nouns_per_verb:
        for noun in freq_w_nouns_per_verb[verb]:
            if not noun in noun_freqs:
                noun_freqs[noun] = 0
            noun_freqs[noun]+=freq_w_nouns_per_verb[verb][noun]

    ent_w_nouns_per_verb = {verb: {} for verb in freq_w_nouns_per_verb}
    for noun in noun_freqs:
        e = 0
        for verb in freq_w_nouns_per_verb:
            if noun in freq_w_nouns_per_verb[verb]:
                p = freq_w_nouns_per_verb[verb][noun]/noun_freqs[noun]
                if p > 0:
                    e-= p * math.log(p, 2)
        for verb in ent_w_nouns_per_verb:
            ent_w_nouns_per_verb[verb][noun] = e

    tot_w_per_verb = {verb: sum(ent_w_nouns_per_verb[verb].values()) for verb in ent_w_nouns_per_verb}
            # entropies[noun] = -entropies[noun] + max


    with open(output_path + "INNER_ENTROPY.txt", "w") as fout:
        for verb in ent_w_nouns_per_verb:
            for noun in ent_w_nouns_per_verb[verb]:
                abs_w = ent_w_nouns_per_verb[verb][noun]
                rel_w = ent_w_nouns_per_verb[verb][noun] / tot_w_per_verb[verb]
                print(verb, noun, abs_w, rel_w, file=fout)