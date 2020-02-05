import argparse
from .preprocess import extract

def _extract_dobjects(args):
    output_path = args.output_dir
    verbs_filepath = args.verbs_input
    corpus_filepath = args.corpus

    extract.extractDobj(output_path, verbs_filepath, corpus_dirpath)



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

    args = root_parser.parse_args()
    args.func(args)