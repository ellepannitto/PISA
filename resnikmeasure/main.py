import argparse

from .aux_scripts import _filter_noun_files
from .preprocess import extract
from .measures import resnik, distributional_measures
from .utils import os_utils as outils

def _extract_lists(args):
    output_path = outils.check_dir(args.output_dir)
    verbs_filepath = args.verbs_input
    corpus_dirpaths = args.corpus
    relations = args.rels
    num_workers = args.num_workers

    extract.extract(output_path, verbs_filepath, corpus_dirpaths, relations, num_workers)
    extract.mergeLists(output_path)

def _filter_objectlist(args):
    output_path = outils.check_dir(args.output_dir)
    input_path = args.input_dir
    threshold = args.threshold

    extract.filterLists(output_path, input_path, threshold)


def _resnik(args):
    output_path = outils.check_dir(args.output_dir)
    input_paths = args.input_filepaths
    wn = args.wordnet

    if wn:
        resnik.compute_measure_wordnet(input_paths, output_path)
    else:
        resnik.compute_measure(input_paths, output_path)


def _pairwise_cosines(args):
    output_path = outils.check_dir(args.output_dir)
    input_path = args.input_dir
    nouns_fpath = args.nouns_fpath
    models_fpath = args.models_fpath
    num_workers = args.num_workers

    distributional_measures.compute_cosines(input_path, output_path, nouns_fpath, num_workers, models_fpath)
    distributional_measures.merge_cosines_files(output_path, models_fpath)

def _compute_weights(args):
    name = args.weight_name
    output_path = outils.check_dir(args.output_dir)
    input_path = args.input_dir
    if name == "id":
        distributional_measures.compute_identity_weight(input_path, output_path)
    elif name == "frequency":
        distributional_measures.compute_frequency_weight(input_path, output_path)
    elif name == "idf":
        distributional_measures.compute_idf_weight(input_path, output_path)
    elif name == "entropy":
        distributional_measures.compute_entropy_weight(input_path, output_path)
    elif name == "lmi":
        pass

def _weighted_dist_measure(args):
    output_path = outils.check_dir(args.output_dir)
    input_path = args.input_dir
    models_path = args.models_dir
    weight_fpath = args.weight_fpath

    distributional_measures.weighted_distributional_measure(input_path, models_path, output_path, weight_fpath)

def _topk_dist_measure(args):
    output_path = outils.check_dir(args.output_dir)
    weight_fpath = args.weights_fpath
    models_path = args.models_dir
    top_k = args.top_k

    distributional_measures.topk_distributional_measure(weight_fpath, models_path, output_path, top_k)


def _filter_weight(args):
    input_path = args.input_dir
    output_path = outils.check_dir(args.output_dir)
    weight_fpath = args.weight_fpath
    _K = args.top_k

    _filter_noun_files.filter_on_weight(input_path, output_path, weight_fpath, _K)


def main():

    parent_parser = argparse.ArgumentParser(add_help=False)

    root_parser = argparse.ArgumentParser(prog='resnikmeasure')
    # root_parser.set_defaults(func=)
    subparsers = root_parser.add_subparsers(title="actions", dest="actions")

    # VERB LIST
    parser_objectlist = subparsers.add_parser('extract-dobjects', parents=[parent_parser],
                                               description='set of utilities to extract the list of direct objects from'
                                                           ' required corpora',
                                               help='set of utilities to extract the list of direct objects from'
                                                    ' required corpora')
    parser_objectlist.add_argument("-o", "--output-dir", default="data/results/",
                                   help="path to output dir, default is data/results/")
    parser_objectlist.add_argument("-v", "--verbs-input", help="path to file containing verbs")
    parser_objectlist.add_argument("-c", "--corpus", nargs="+",
                                   help="path to dir containing corpus")
    parser_objectlist.add_argument("-r", "--rels", nargs="+", required=True, help="target relations")
    parser_objectlist.add_argument("-w", "--num-workers", default=1, type=int,
                                    help="number of workers for multiprocessing")
    parser_objectlist.set_defaults(func=_extract_lists)

    # FILTER
    parser_filterlist = subparsers.add_parser('filter-objects', parents=[parent_parser],
                                              description="filters list of objects based on threshold",
                                              help="filters list of objects based on threshold")
    parser_filterlist.add_argument("-o", "--output-dir", default="data/results/filtered/",
                                   help="path to output dir, default is data/results/filtered/")
    parser_filterlist.add_argument("-i", "--input-dir", default="data/results/",
                                   help="path to input dir, default is data/results/")
    parser_filterlist.add_argument("-t", "--threshold", required=True, type=int,
                                   help="minimum frequency for nouns")
    parser_filterlist.set_defaults(func=_filter_objectlist)

    # RESNIK MEASURE
    parser_resnik = subparsers.add_parser("resnik", parents=[parent_parser],
                                          description='computes standard Resnik measure',
                                          help='computes standard Resnik measure')
    parser_resnik.add_argument("-i", "--input-filepaths", nargs="+", required=True,
                                 help="path to input directory containing one file per verb")
    parser_resnik.add_argument("-o", "--output-dir", default="data/wn_resnik/",
                                 help="path to output directory, default is `data/wn_resnik/`")
    parser_resnik.add_argument("-w", "--wordnet", action="store_true",
                               help="compute using wordnet classes")
    parser_resnik.set_defaults(func=_resnik)


    # PAIRWISE COSINES
    parser_cosines = subparsers.add_parser("cosines", parents=[parent_parser],
                                                  description='computes pairwise cosines',
                                                  help='computes pairwise cosines')
    parser_cosines.add_argument("-i", "--input-dir", required=True,
                                 help="path to input directory containing one file per verb")
    parser_cosines.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                 help="path to output directory, default is `data/dist_measures/`")
    parser_cosines.add_argument("-n", "--nouns-fpath", required=True,
                                       help="path to file containing required nouns")
    parser_cosines.add_argument("-m", "--models-fpath", required=True,
                                help="path to file containing list of models")
    parser_cosines.add_argument("-w", "--num-workers", default=1, type=int,
                                       help="number of workers for multiprocessing")
    parser_cosines.set_defaults(func=_pairwise_cosines)

    parser_weights = subparsers.add_parser("weights", parents=[parent_parser],
                                            description='computes weights measures',
                                            help='computes weights measures')
    parser_weights.add_argument("-i", "--input-dir", required=True,
                                 help="path to input directory containing one file per verb")
    parser_weights.add_argument("-o", "--output-dir", default="data/dist_measures/weights/",
                                 help="path to output directory, default is `data/dist_measures/weights/`")
    parser_weights.add_argument("-n", "--weight-name", required=True,
                                       help="name of chosen weight - id, frequency, idf, entropy")
    parser_weights.set_defaults(func=_compute_weights)

    parser_weighteddistmeasure = subparsers.add_parser("weighted-dist-measure", parents=[parent_parser],
                                               description='computes distributional measure',
                                               help='computes distributional measure')
    parser_weighteddistmeasure.add_argument("-i", "--input-dir", required=True,
                                    help="path to input directory containing one file per verb")
    parser_weighteddistmeasure.add_argument("-m", "--models-dir", required=True,
                                    help="path to input directory containing one file per model")
    parser_weighteddistmeasure.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                    help="path to output directory, default is `data/dist_measures/`")
    parser_weighteddistmeasure.add_argument("-w", "--weight-fpath", required=True,
                                    help="path to file with weights on fourth column")
    parser_weighteddistmeasure.set_defaults(func=_weighted_dist_measure)

    parser_topkdistmeasure = subparsers.add_parser("topk-dist-measure", parents=[parent_parser],
                                                description='computes average of pairwise cosines',
                                                help='computes average of pairwise cosines')
    parser_topkdistmeasure.add_argument("-w", "--weights-fpath", required=True,
                                    help="path to file with weights per verb")
    parser_topkdistmeasure.add_argument("-m", "--models-dir", required=True,
                                    help="path to input directory containing one file per model")
    parser_topkdistmeasure.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                    help="path to output directory, default is `data/dist_measures/pairwise_cosines/`")
    parser_topkdistmeasure.add_argument("-k", "--top-k", default=0, type=int,
                                      help="number of nouns to consider. Default is 0 meaning all will be considered."
                                           "If a negative number is given, the last k nouns will be considered")
    parser_topkdistmeasure.set_defaults(func=_topk_dist_measure)

    parser_filterweights = subparsers.add_parser("filter-weight", parents=[parent_parser],
                                                 description="filter noun list based on weight and threshold",
                                                 help="filter noun list based on weight and threshold")
    parser_filterweights.add_argument("-i", "--input-dir", required=True,
                                    help="path to input directory containing one file per verb")
    parser_filterweights.add_argument("-o", "--output-dir", default="data/nouns_list/",
                                    help="path to output directory, default is `data/nouns_list/`")
    parser_filterweights.add_argument("-w", "--weight-fpath", required=True,
                                      help="path to file with weights on fourth column")
    parser_filterweights.add_argument("-k", "--top-k", default=0, type=int,
                                      help="number of nouns to consider. Default is 0 meaning all will be considered."
                                           "If a negative number is given, the last k nouns will be considered")
    parser_filterweights.set_defaults(func=_filter_weight)


    args = root_parser.parse_args()
    if not "func" in args:
        root_parser.print_usage()
        exit()
    args.func(args)