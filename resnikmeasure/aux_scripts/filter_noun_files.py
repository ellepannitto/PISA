import os

def filter_on_weight(input_path, output_path, weight_fpath, k):
    os.makedirs(output_path, exist_ok=True)

    weights = {}
    with open(weight_fpath) as fin:
        for line in fin:
            verb, noun, w, _ = line.strip().split()
            w = float(w)
            if not verb in weights:
                weights[verb] = {}
            weights[verb][noun] = w

    for verb in weights:
        weights[verb] = list(sorted(weights[verb].items(), key= lambda x: -x[1]))[:k]
        with open(output_path+"filtered.output_nouns.{}".format(verb), "w") as fout:
            for noun, w in weights[verb]:
                print(noun, w, file=fout)