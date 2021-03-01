from nltk.corpus import wordnet as wn


def basic_function(lemma, rel):
    return True, []


def subject_is_not_artifact(lemma, rel):
    if rel.startswith("nsubjpass"):
        return True, []
    else:
        bool_value, list = word_is_artifact(lemma)
        return not bool_value, list


def word_is_artifact(lemma, category='artifact', top_k=1, lang='eng'):
    # print(lemma)
    hyper = lambda s: s.hypernyms()
    synsets = wn.synsets(lemma, lang=lang, pos='n')[:top_k]

    chain = [lemma]

    for s in synsets:
        # print("SYNSET: ", s)
        for hyper_synset in list(s.closure(hyper)):
            # print("hyper", hyper_synset)
            name = hyper_synset.lemmas()[0].name()
            chain.append(name)
            # print(name)
            if category == name:
                return True, chain

    return False, chain


if __name__ == "__main__":
    import sys
    word = sys.argv[1]
    print(word_is_artifact(word))
