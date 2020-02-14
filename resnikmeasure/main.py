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


def _dist_measure(args):
    output_path = args.output_dir
    input_path = args.input_dir

    distributional_measures.compute_measure(input_path, output_path)


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

    parser_distributional = subparsers.add_parser("dist-measure", parents=[parent_parser],
                                                  description='computes distributional measure',
                                                  help='computes distributional measure')
    parser_distributional.add_argument("-i", "--input-dir", required=True,
                                 help="path to input directory containing one file per verb")
    parser_distributional.add_argument("-o", "--output-dir", default="data/dist_measures/",
                                 help="path to output directory, default is `data/dist_measures/`")
    parser_distributional.set_defaults(func=_dist_measure)

    args = root_parser.parse_args()
    args.func(args)