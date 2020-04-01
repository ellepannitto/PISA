# New measure based on Resnik

## Install

Under the main directory:
```shell script
python3 setup.py [install|develop]
```

## Run

### Extract list of items
The first thing you want to do is to extract from a corpus the list of target nouns associated with each verb.
In order to do so, launch the command:

```shell script
resnikmeasure extract-dobjects \
    --verbs-input abs_path_to_verb_list \
    --corpus abs_path_to_corpus_files \
    --rels list_of_relations \
    --workers number_of_worker_for_multiprocessing \ 
    --output-dir abs_path_to_output_directory
```

The verb list for Resnik original measure is in `data/verb_list_resnik.txt`

The script will create, in the output directory:
* a file `nouns.freq` containing the absolute frequencies of the selected verbs
* a file `verbs.freq` containing the absolute frequencies of the found nouns
* a set of files `output_nouns.[verb]`, one for each verb, containing the list of nouns for the specific verbs 
with its relative frequency

### Filtering

After having extracted the complete list of co-occurrences, the next thing to do would be to filter the lists of nouns 
based on their absolute frequency (to reduce noise) and their presence in the distributional models we plan to use.

To do so, run the following commands:

```shell script
resnikmeasure filter-threshold \
    --input-dir abs_path_to_directory_containing_input_files \
    --threshold minimum_admitted_frequency \
    --output-dir abs_path_to_output_directory
```

```shell script
resnikmeasure filter-coverage \
    --input-filepaths abs_paths_to_files_with_lists \
    --models-fpath abs_path_to_file_containing_models_list \
    --nouns-fpath abs_path_to_noun_frequency_file \
    --output-dir abs_path_to_output_directory
```

The file containing the list of models should be formatted as follows:
```text
model.one.id	/abs/path/to/file/containing/one/vector/per/line
model.two.id	/abs/path/to/file/containing/one/vector/per/line
```

### Resnik measure

Next, you can compute the standard measure proposed by Resnik, using the following command:
```shell script
resnikmeasure resnik
    --input-filepaths abs_paths_to_files_with_lists \
    --wordnet true_if_specified \
    --language-code wordnet_language_code \
    --output-dir abs_path_to_output_directory
```

The `--language-code` parameter is required only if the `--wordnet` flag is used.

### The distributional measures

