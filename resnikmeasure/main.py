import argparse
from .preprocess import extract
from .measures import wn_resnik, distributional_measures

def _extract_dobjects(args):
    output_path = args.output_dir
    verbs_filepath = args.verbs_input
    corpus_filepath = args.corpus

    extract.extractDobj(output_path, verbs_filepath, corpus_dirpath)

def _wn_resnik(args):
    output_path = args.output_dir
    input_path = args.input_dir

    wn_resnik.compute_measure(input_path, output_path)


def _pairwise_cosines(args):
    output_path = args.output_dir
    input_path = args.input_dir
    nouns_fpath = args.nouns_fpath

    distributional_measures.compute_cosines(input_path, output_path, nouns_fpath, args.num_workers)

def _dist_measure(args):
    output_path = args.output_dir
    input_path = args.input_dir
    models_path = args.models_dir
    weight_fpath = args.weight_fpath

    distributional_measures.distributional_measure(input_path, models_path, output_path, weight_fpath)


def _compute_weights(args):
    name = args.weight_name
    output_path = args.output_dir
    input_path = args.input_dir
    if name == "id":
        distributional_measures.compute_identity_weight(input_path, output_path)
    elif name == "frequency":
        distributional_measures.compute_frequency_weight(input_path, output_path)
    elif name == "idf":
        distributional_measures.compute_idf_weight(input_path, output_path)
    elif name == "entropy":
        distributional_measures.compute_entropy_weight(input_path, output_path)

def main():

    parent_parser = argparse.ArgumentParser(add_help=False)

    root_parser = argparse.ArgumentParser(prog='resnikmeasure')
    subparsers = root_parser.add_subparsers(title="actions", dest="actions")

    # VERB LIST
    parser_objectlist = subparsers.add_parser('extract-dobjects', parents=[parent_parser],
                                               description='set of utilities to extract the list of direct objects from'
                                                           'required corpora',
                                               help='set of utilities to extract the list of direct objects from'
                                                           'required corpora')

    parser_objectlist.add_argument("-o", "--output-dir", default="data/results/",
                                   help="path to output dir, default is data/results/")

    parser_objectlist.add_argument("-v", "--verbs-input", help="path to file containing verbs")

    parser_objectlist.add_argument("-c", "--corpus", help="path to dir containing corpus")

    parser_objectlist.set_defaults(func=_extract_dobjects)

    # MEASURES

    parser_wnresnik = subparsers.add_parser("wn-resnik", parents=[parent_parser],
                                            description='computes standard Resnik measure',
                                            help='computes standard Resnik measure')
    parser_wnresnik.add_argument("-i", "--input-dir", required=True,
                                 help="path to input directory containing one file per verb")
    parser_wnresnik.add_argument("-o", "--output-dir", default="data/wn_resnik/",
                                 help="path to output directory, default is `data/wn_resnik/`")
    parser_wnresnik.set_defaults(func=_wn_resnik)

    parser_cosines = subparsers.add_parser("cosines", parents=[parent_parser],
                                                  description='computes pairwise cosines',
                                                  help='computes pairwise cosines')
    parser_cosines.add_argument("-i", "--input-dir", required=True,
                                 help="path to input directory containing one file per verb")
    parser_cosines.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                 help="path to output directory, default is `data/dist_measures/`")
    parser_cosines.add_argument("-n", "--nouns-fpath", required=True,
                                       help="path to file containing required nouns")
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

    parser_distmeasure = subparsers.add_parser("dist-measure", parents=[parent_parser],
                                               description='computes distributional measure',
                                               help='computes distributional measure')
    parser_distmeasure.add_argument("-i", "--input-dir", required=True,
                                    help="path to input directory containing one file per verb")
    parser_distmeasure.add_argument("-m", "--models-dir", required=True,
                                    help="path to input directory containing one file per model")
    parser_distmeasure.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                    help="path to output directory, default is `data/dist_measures/`")
    parser_distmeasure.add_argument("-w", "--weight-fpath", required=True,
                                    help="path to file with weights on fourth column")
    parser_distmeasure.set_defaults(func=_dist_measure)


    args = root_parser.parse_args()
    args.func(args)