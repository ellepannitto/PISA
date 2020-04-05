import logging
import os
import pandas as pd
import re

from scipy.stats import spearmanr, mannwhitneyu

logger = logging.getLogger(__name__)


def computeSpearmanr(output_path, input_filepaths, resnik_model, label):

	fname_stats = output_path+"{}.spearman_stat.csv".format(label)
	fname_pvalues = output_path+"{}.spearman_pvalues.csv".format(label)

	stats = {}
	weights = set()

	df_resnik = pd.read_table(resnik_model, sep=" ", names=["verb", "sps"]).sort_values(by=['verb'])

	for filename in input_filepaths:
		basename = os.path.basename(filename)
		df_model = pd.read_table(filename, sep=" ", names=["verb", "sps"]).sort_values(by=['verb'])
		stat, pvalue = spearmanr(df_resnik['sps'], df_model['sps'])

		# TODO: handle splitting better
		basename_split = re.split("[-.]", basename)
		algo, weight = basename_split[0], basename_split[-1]
		basename_label = ".".join(basename_split[:-1])
		weights.add(weight)

		if algo not in stats:
			stats[algo] = {}
		if basename_label not in stats[algo]:
			stats[algo][basename_label] = {}

		stats[algo][basename_label][weight] = (stat, pvalue)

	weights = list(sorted(weights))

	with open(fname_stats, "w") as fout_stats, open(fname_pvalues, "w") as fout_pvalues:
		print("\t\t"+"\t".join(w for w in weights), file=fout_stats)
		print("\t\t"+"\t".join(w for w in weights), file=fout_pvalues)
		for algo in stats:
			print(algo, file=fout_stats)
			print(algo, file=fout_pvalues)
			for basename_label in stats[algo]:
				s_stat = "\t"+basename_label
				s_pvalue = "\t"+basename_label
				for weight in weights:
					if weight in stats[algo][basename_label]:
						stat, pvalue = stats[algo][basename_label][weight]
						s_stat += "\t{:.3f}".format(stat)
						s_pvalue += "\t{:.3f}".format(pvalue)
					else:
						s_stat += "\t-".format(stat)
						s_pvalue += "\t-".format(pvalue)

				print(s_stat, file=fout_stats)
				print(s_pvalue, file=fout_pvalues)


# TODO: verb_list_resnik and alternating need to go into just one file
def computeMannwhitneyup(output_path, input_paths, alternating_filepath, label):

	fname_stats = output_path+"{}.mannwhitney_stat.csv".format(label)
	fname_pvalues = output_path+"{}.mannwhitney_pvalues.csv".format(label)
	
	df_alternating = pd.read_table(alternating_filepath, sep=" ", names=["verb", "alternating"]).sort_values(by=['verb'])

	stats = {}
	weights = set()
	
	for filename in input_paths:
		basename = os.path.basename(filename)
		df_model = pd.read_table(filename, sep=" ", names=["verb", "sps"]).sort_values(by=['verb'])
		df_together = pd.concat([df_model.reset_index(drop=True),
								df_alternating['alternating'].reset_index(drop=True)], axis=1)

		yes_alt = df_together['alternating'] == "yes"
		no_alt = df_together['alternating'] == "no"
		stat, pvalue = -1, -1
		# per mann-whitney serve che i valori di ciascuna colonna non siano tutti uguali
		if df_together['sps'].nunique() != 1:
			stat, pvalue = mannwhitneyu(df_together['sps'][yes_alt], df_together['sps'][no_alt])

		# TODO: handle splitting better
		basename_split = re.split("[-.]", basename)
		algo, weight = basename_split[0], basename_split[-1]
		basename_label = ".".join(basename_split[:-1])
		weights.add(weight)

		if algo not in stats:
			stats[algo] = {}
		if basename_label not in stats[algo]:
			stats[algo][basename_label] = {}

		stats[algo][basename_label][weight] = (stat, pvalue)

	weights = list(sorted(weights))

	with open(fname_stats, "w") as fout_stats, open(fname_pvalues, "w") as fout_pvalues:
		print("\t\t"+"\t".join(w for w in weights), file=fout_stats)
		print("\t\t"+"\t".join(w for w in weights), file=fout_pvalues)
		for algo in stats:
			print(algo, file=fout_stats)
			print(algo, file=fout_pvalues)
			for basename_label in stats[algo]:
				s_stat = "\t"+basename_label
				s_pvalue = "\t"+basename_label
				for weight in weights:
					if weight in stats[algo][basename_label]:
						stat, pvalue = stats[algo][basename_label][weight]
						s_stat += "\t{:.3f}".format(stat)
						s_pvalue += "\t{:.3f}".format(pvalue)
					else:
						s_stat += "\t-".format(stat)
						s_pvalue += "\t-".format(pvalue)

				print(s_stat, file=fout_stats)
				print(s_pvalue, file=fout_pvalues)
