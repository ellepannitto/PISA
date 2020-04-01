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
    --num-workers number_of_worker_for_multiprocessing \ 
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

Next, you want to compute the set of measures based on distributional information. In order to do so, a preliminary
step has to be done for efficiency reasons.

Before getting to the actual computation, we need to store the pairwise cosine similarities between the nouns that we
have extracted during the previous steps. This is a costly operation in terms of both space and time, so be prepared to 
see this computation last for a while.

```shell script
resnikmeasure cosines
    --input-filepaths abs_paths_to_files_with_lists \
    --nouns-fpath abs_path_to_file_with_noun_frequencies \
    --num-workers  number_of_worker_for_multiprocessing \
    --models-fpath abs_path_to_file_containing_models_list \
    --output-dir abs_path_to_output_directory
```

Another thing that we might want to pre-compute are the weights that will be used during the computation of the
distributional measures. This will make it easier to have a qualitative understanding of what the measures do.

```shell script
resnikmeasure weights
    --input-filepaths abs_paths_to_files_with_lists \
    --weight-name [id|frequency|idf|entropy|in_entropy|lmi] \
    --noun-freqs abs_path_to_file_with_noun_frequencies \
    --verb-freqs abs_path_to_file_with_verb_frequencies \
    --output-dir abs_path_to_output_directory
```

The `--noun-freqs` parameter is only needed for `entropy` and `lmi` computation.

The `--verb-freqs` parameter is only needed for `lmi` computation.

[TODO: add a description of weights]

We can now turn to the computation for the actual measures. Note that they are quite time-consuming.

#### Full weighted

[TODO: add description]

```shell script
resnikmeasure weighted-dist-measure
    --input-filepaths abs_paths_to_files_with_lists \
    --models-filepaths abs_paths_to_files_containing_pairwise_cosines \
    --weight-filepaths abs_paths_to_files_containing_weights
    --output-dir abs_path_to_output_directory
```

#### Top/Bottom K ranked
[TODO: add description]

```shell script
resnikmeasure topk-dist-measure
    --input-filepaths abs_paths_to_files_with_lists \
    --weight-filepaths abs_paths_to_files_containing_weights \
    --models-filepaths abs_paths_to_files_containing_pairwise_cosines \
    --top-k number_of_items_to_consider \
    --output-dir abs_path_to_output_directory
```

If `--top-k` is given a negative value, the least significant `k` values will be considered.

### Statistics