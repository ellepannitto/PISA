def load_verbs_set(filepath):
    verbs = set()
    with open(filepath) as fin:
        for line in fin:
            verbs.add(line.strip())

    return verb