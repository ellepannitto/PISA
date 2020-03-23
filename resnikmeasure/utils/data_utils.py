def load_verbs_set(filepath):
    verbs = set()
    with open(filepath) as fin:
        for line in fin:
            verbs.add(line.strip())

    return verbs

def load_models_dict(filepath):
    ret = {}
    with open(filepath) as fin:
        for line in fin:
            line = line.strip().split()
            if len(line):
                ret[line[0]] = line[1]

    return ret
