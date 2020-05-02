import logging
import os
import re

from scipy.stats import spearmanr, mannwhitneyu

from resnikmeasure.utils import data_utils as dutils

logger = logging.getLogger(__name__)


def computeSpearmanr(output_path, input_filepaths, resnik_model, label):

	fname_stats = output_path+"{}.spearman_stat.csv".format(label)
	fname_pvalues = output_path+"{}.spearman_pvalues.csv".format(label)

	stats = {}
	weights = set()

	resnik_values = {}
	with open(resnik_model) as fin:
		for line in fin:
			linesplit = line.strip().split()
			if len(line):
				verb, value = linesplit
				value = float(value)
				resnik_values[verb] = value

	for filename in input_filepaths:
		print(filename)
		basename = os.path.basename(filename)

		model_values = {}
		with open(filename) as fin:
			for line in fin:
				linesplit = line.strip().split()
				if len(line):
					verb, value = linesplit
					value = float(value)
					model_values[verb] = value

		stat, pvalue = spearmanr([resnik_values[x] for x in resnik_values], [model_values[x] for x in resnik_values])

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
						sign = ''
						if pvalue <= 0.001:
							sign = "***"
						elif pvalue <= 0.01:
							sign = "**"
						elif pvalue <= 0.05:
							sign = "*"
						s_stat += "\t{:.3f}{}".format(stat,sign)
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

	alternating_map = dutils.load_alternating_verbs(alternating_filepath)

	stats = {}
	weights = set()
	
	for filename in input_paths:
		basename = os.path.basename(filename)

		alternating_values = []
		non_alternating_values = []

		with open(filename) as fin:
			for line in fin:
				linesplit = line.strip().split()

				if len(linesplit):
					verb, value = linesplit
					value = float(value)

					if verb in alternating_map["yes"]:
						alternating_values.append(value)
					elif verb in alternating_map["no"]:
						alternating_values.append(value)
					else:
						print("WARNING: verb not in list", verb)

		stat, pvalue = -1, -1
		# per mann-whitney serve che i valori di ciascuna colonna non siano tutti uguali
		# if df_together['sps'].nunique() != 1:
		# try:
		if not all(el == alternating_values[0] for el in alternating_values):
			stat, pvalue = mannwhitneyu(alternating_values, non_alternating_values, alternative='two-sided')
		# except:
		# 	pass

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
						sign = ''
						if pvalue <= 0.001:
							sign = "***"
						elif pvalue <= 0.01:
							sign = "**"
						elif pvalue <= 0.05:
							sign = "*"

						s_stat += "\t{:.3f}{}".format(stat,sign)
						s_pvalue += "\t{:.3f}".format(pvalue)
					else:
						s_stat += "\t-".format(stat)
						s_pvalue += "\t-".format(pvalue)

				print(s_stat, file=fout_stats)
				print(s_pvalue, file=fout_pvalues)
