import os
import collections

def process(sentence, lookfor, accepted_verbs, freqdict):

    for head, lemma in lookfor:
        if head in sentence:
            if sentence[head] in accepted_verbs:
                freqdict[sentence[head]][lemma]+=1

def extractDobj(output_path, verbs_filepath, corpus_dirpath):
    max = 200
    i = 0
    os.makedirs(output_path, exist_ok=True)
    freqdict = {}
    verbs = set()
    with open(verbs_filepath) as fin:
        for line in fin:
            verbs.add(line.strip())

    for verb in verbs:
        freqdict[verb] = collections.defaultdict(int)

    for filename in os.listdir(corpus_dirpath):
        print("processing file: ", filename)
        with open(corpus_dirpath+filename) as fin:
            sentence = {}
            lookfor = []
            for line in fin:
                line = line.strip()
                if not len(line) or line.startswith("#"):
                    if len(lookfor) > 0:
                        process(sentence, lookfor, verbs, freqdict)
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
                            if rel == "dobj":
                                lookfor.append((head, lemma))
                            sentence[position] = lemma
            if len(lookfor) > 0:
                process(sentence, lookfor, verbs, freqdict)


    for verb in freqdict:
        with open(output_path+"output_nouns.{}".format(verb), "w") as fout:
            sorted_nouns = sorted(freqdict[verb].items(), key = lambda x: -x[1])
            for x, y in sorted_nouns:
                print(x, y, file=fout)