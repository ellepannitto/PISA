import argparse

from .preprocess import extract, cosines, weights
from .measures import resnik, distributional_measures
from .utils import os_utils as outils
from .statistics import stats

# TODO: change handling of output folder


def _extract_lists(args):
    output_path = outils.check_dir(args.output_dir)
    verbs_filepath = args.verbs_input
    corpus_dirpaths = args.corpus_dirs
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
    language = args.language_code

    if wn:
        resnik.compute_measure_wordnet(input_paths, output_path, language)
    else:
        resnik.compute_measure(input_paths, output_path)


def _pairwise_cosines(args):
    output_path = outils.check_dir(args.output_dir)
    input_paths = args.input_filepaths
    nouns_fpath = args.nouns_fpath
    models_fpath = args.models_fpath
    num_workers = args.num_workers

    cosines.compute_cosines(input_paths, output_path, nouns_fpath, num_workers, models_fpath)
    cosines.merge_cosines_files(output_path, models_fpath)


def _compute_weights(args):
    name = args.weight_name
    output_path = outils.check_dir(args.output_dir)
    input_paths = args.input_filepaths

    if name == "id":
        weights.compute_identity_weight(input_paths, output_path)
    elif name == "frequency":
        weights.compute_frequency_weight(input_paths, output_path)
    elif name == "idf":
        weights.compute_idf_weight(input_paths, output_path)
    elif name == "entropy":
        weights.compute_entropy_weight(input_paths, output_path, args.noun_freqs)
    elif name == "in_entropy":
        weights.compute_inner_entropy_weight(input_paths, output_path)
    elif name == "lmi":
        weights.compute_lmi_weight(input_paths, output_path, args.noun_freqs, args.verb_freqs)


def _weighted_dist_measure(args):
    output_path = outils.check_dir(args.output_dir)
    input_paths = args.input_filepaths
    models_paths = args.models_filepaths
    weight_fpaths = args.weight_filepaths

    distributional_measures.weighted_distributional_measure(input_paths, models_paths, output_path, weight_fpaths)


def _topk_dist_measure(args):
    output_path = outils.check_dir(args.output_dir)
    input_paths = args.input_filepaths
    weight_paths = args.weight_filepaths
    models_paths = args.models_filepaths
    top_k = args.top_k

    distributional_measures.topk_distributional_measure(weight_paths, models_paths, input_paths, output_path, top_k)


def _filter_coverage(args):
    input_paths = args.input_filepaths
    output_path = outils.check_dir(args.output_dir)
    models_fpath = args.models_fpath
    nouns_fpath = args.nouns_fpath

    extract.filterCoverage(output_path, input_paths, models_fpath, nouns_fpath)


def _spearmanr(args):
    input_paths = args.input_filepaths
    output_path = outils.check_dir(args.output_dir)
    resnik_model = args.resnik_model

    stats.computeSpearmanr(output_path, input_paths, resnik_model)


def _mannwhitneyup(args):
    output_path = outils.check_dir(args.output_dir)
    input_paths = args.input_filepaths

    stats.computeMannwhitneyup(output_path, input_paths)


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
    parser_objectlist.add_argument("-c", "--corpus-dirs", nargs="+",
                                   help="path to dirs containing corpus")
    parser_objectlist.add_argument("-r", "--rels", nargs="+", required=True, help="target relations")
    parser_objectlist.add_argument("-w", "--num-workers", default=1, type=int,
                                   help="number of workers for multiprocessing")
    parser_objectlist.set_defaults(func=_extract_lists)

    # TODO: check input folder format

    # FILTER THRESHOLD
    parser_filterlist = subparsers.add_parser('filter-threshold', parents=[parent_parser],
                                              description="filters list of objects based on threshold",
                                              help="filters list of objects based on threshold")
    parser_filterlist.add_argument("-o", "--output-dir", default="data/results/filtered/",
                                   help="path to output dir, default is data/results/filtered/")
    parser_filterlist.add_argument("-i", "--input-dir", default="data/results/",
                                   help="path to input dir, default is data/results/")
    parser_filterlist.add_argument("-t", "--threshold", required=True, type=int,
                                   help="minimum frequency for nouns")
    parser_filterlist.set_defaults(func=_filter_objectlist)

    # COVERAGE FILTER
    parser_filterweights = subparsers.add_parser("filter-coverage", parents=[parent_parser],
                                                 description="filter noun list based on their presence in models",
                                                 help="filter noun list based on their presence in models")
    parser_filterweights.add_argument("-i", "--input-filepaths", nargs='+', required=True,
                                      help="path to input directory containing one file per verb")
    parser_filterweights.add_argument("-o", "--output-dir", default="data/nouns_list/",
                                      help="path to output directory, default is `data/nouns_list/`")
    parser_filterweights.add_argument("-m", "--models-fpath", required=True,
                                      help="path to file containing list of models")
    parser_filterweights.add_argument("-n", "--nouns-fpath", required=True,
                                      help="path to file containing required nouns")
    parser_filterweights.set_defaults(func=_filter_coverage)

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
    parser_resnik.add_argument("-l", "--language-code", default="eng",
                               help="wordnet language code")
    parser_resnik.set_defaults(func=_resnik)

    # PAIRWISE COSINES
    parser_cosines = subparsers.add_parser("cosines", parents=[parent_parser],
                                           description='computes pairwise cosines',
                                           help='computes pairwise cosines')
    parser_cosines.add_argument("-i", "--input-filepaths", nargs="+", required=True,
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

    # COMPUTE WEIGHTS
    parser_weights = subparsers.add_parser("weights", parents=[parent_parser],
                                           description='computes weights measures',
                                           help='computes weights measures')
    parser_weights.add_argument("-i", "--input-filepaths", nargs="+", required=True,
                                help="path to input directory containing one file per verb")
    parser_weights.add_argument("-o", "--output-dir", default="data/dist_measures/weights/",
                                help="path to output directory, default is `data/dist_measures/weights/`")
    parser_weights.add_argument("-w", "--weight-name", required=True,
                                choices=['id', 'frequency', 'idf', 'entropy', 'in_entropy', 'lmi'],
                                help="name of chosen weight - id, frequency, idf, entropy, lmi")
    parser_weights.add_argument("-n", "--noun-freqs",
                                help="path to file with noun frequencies, needed for LMI and ENTROPY")
    parser_weights.add_argument("-v", "--verb-freqs", help="path to file with verb frequencies, needed for LMI")
    parser_weights.set_defaults(func=_compute_weights)

    # WEIGHTED MEASURES
    # TODO: multiprocess
    parser_weighteddistmeasure = subparsers.add_parser("weighted-dist-measure", parents=[parent_parser],
                                                       description='computes distributional measure',
                                                       help='computes distributional measure')
    parser_weighteddistmeasure.add_argument("-i", "--input-filepaths", nargs="+", required=True,
                                            help="path to input directory containing one file per verb")
    parser_weighteddistmeasure.add_argument("-m", "--models-filepaths", nargs='+', required=True,
                                            help="path to input directory containing one file per model")
    parser_weighteddistmeasure.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                            help="path to output directory, default is `data/dist_measures/`")
    parser_weighteddistmeasure.add_argument("-w", "--weight-filepaths", nargs="+", required=True,
                                            help="path to file with weights on fourth column")
    parser_weighteddistmeasure.set_defaults(func=_weighted_dist_measure)

    # TOPK MEASURE
    parser_topkdistmeasure = subparsers.add_parser("topk-dist-measure", parents=[parent_parser],
                                                   description='computes average of pairwise cosines',
                                                   help='computes average of pairwise cosines')
    parser_topkdistmeasure.add_argument("-i", "--input-filepaths", nargs="+", required=True,
                                        help="path to input directory containing one file per verb")
    parser_topkdistmeasure.add_argument("-w", "--weight-filepaths", nargs='+', required=True,
                                        help="path to files with weights per verb")
    parser_topkdistmeasure.add_argument("-m", "--models-filepaths", nargs='+', required=True,
                                        help="path to input directory containing one file per model")
    parser_topkdistmeasure.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                        help="path to output directory, default is "
                                             "`data/dist_measures/pairwise_cosines/`")
    parser_topkdistmeasure.add_argument("-k", "--top-k", default=0, type=int,
                                        help="number of nouns to consider. Default is 0 meaning all will be considered."
                                             "If a negative number is given, the last k nouns will be considered")
    parser_topkdistmeasure.set_defaults(func=_topk_dist_measure)
    
    # STATS: SPEARMAN CORRELATION OF EACH MODEL WITH RESNIK
    parser_spearmanr = subparsers.add_parser("spearmanr", parents=[parent_parser],
                                                   description='computes Spearman r between each model and Resnik model',
                                                   help='computes Spearman r between each model and Resnik model')
    parser_spearmanr.add_argument("-r", "--resnik-model", nargs="+", required=True,
                                        help="path to file containing the standard Resnik measure as computed before")
    parser_spearmanr.add_argument("-i", "--input-filepaths", nargs='+', required=True,
                                        help="path to input directory containing one file per model")
    parser_spearmanr.add_argument("-o", "--output-dir", default="data/stats_final/",
                                        help="path to output directory, default is "
                                             "`data/stats_final/`")
    parser_spearmanr.set_defaults(func=_spearmanr)
    
    # STATS: MANN-WHITNEY U TO SEE DIFFERENCE WITHIN EACH MODEL
    parser_mannwhitneyup = subparsers.add_parser("mannwhitneyup", parents=[parent_parser],
                                                   description='computes p value of Mann-Whitney U within each model',
                                                   help='computes p value of Mann-Whitney U within each model')
    parser_mannwhitneyup.add_argument("-i", "--input-filepaths", nargs='+', required=True,
                                        help="path to input directory containing one file per model")
    parser_mannwhitneyup.add_argument("-o", "--output-dir", default="data/stats_final/",
                                        help="path to output directory, default is "
                                             "`data/stats_final/`")
    parser_mannwhitneyup.set_defaults(func=_mannwhitneyup)

    args = root_parser.parse_args()
    if "func" not in args:
        root_parser.print_usage()
        exit()
    args.func(args)
