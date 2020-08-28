__author__ = 'Amine Kchouk'
__credits__ = ['John Kidikian']
__version__ = "1.0"
__email__ = "amine.kchouk@polymtl.ca"
__status__ = "Development"


# Built-in libraries
from argparse import ArgumentParser
from itertools import chain, zip_longest
import os, sys, re

# Pipy libraries
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

# User libraries
from lib.logger import Logger
from lib.debugger import Debugger
from lib.configfile import *
from lib.useful_functions import *
from lib.multiplot import *


# Parse input arguments
parser = ArgumentParser()
options = parser.add_argument_group('Execution options')
options.add_argument('-ns', '--no-save', help='don\'t save the results', dest='save', action='store_false')
options.add_argument('-sg', '--show-graph', help='show the graphs', action='store_true')
options.add_argument('-e', '--read-exported', help='read exported results instead of log results', dest='READ_EXPORT', action='store_true')
options.add_argument('--debug', help='activates debug-mode', dest='DEBUG', action='store_true')
paths = parser.add_argument_group('Paths')
paths.add_argument('--config', help='path of the config file', dest='CONFIG', default='config.ini')
paths.add_argument('--solution', help='path of the NOMAD SOLUTION_FILE', dest='SOLUTION', default='Logs/NOMAD_solution.0.log')
paths.add_argument('--history', help='path of the NOMAD HISTORY_FILE', dest='HISTORY', default='Logs/NOMAD_history.0.log')
paths.add_argument('--mdids-results', help='path of the MDIDS results file', dest='MDIDS', default='Logs/MDIDS-NOMAD_results.log')
paths.add_argument('--export', help='path of the folder where results will be exported', dest='EXPORT', default='Results')
fileformat = parser.add_argument_group('File format')
fileformat.add_argument('-d', '--delimiter', help='delimiter used when generating csv file', dest='DELIMITER', default=';')
fileformat.add_argument('-size', '--figure-size', help='Size of the figures', dest='FIGSIZE', type=float, default=14)
args = parser.parse_args()
# Append a slash to the end of args.EXPORT if not present:
if args.EXPORT[-1] not in ('/', '\\'): args.EXPORT += '/'


# If READ_EXPORT is True, check if the file exists, if not try to use the log files
if args.READ_EXPORT:
	try:
		assert os.path.isdir(args.EXPORT)
		assert os.path.isfile(args.EXPORT + 'history.csv')
		print('[WARNING] Cannot generate sensitivity matrix with the `--read-exported` option.\n')
	except AssertionError:
		print("Exported results not found, trying to use log results instead.")
		args.READ_EXPORT = False

if not args.READ_EXPORT:
	assert os.path.isfile(args.SOLUTION), f'SOLUTION_FILE "{args.SOLUTION}" not found'
	assert os.path.isfile(args.HISTORY), f'HISTORY_FILE "{args.HISTORY}" not found'
	assert os.path.isfile(args.MDIDS), f'MDIDS results file "{args.MDIDS}" not found'

if args.save: os.makedirs(args.EXPORT, exist_ok=True)
# Logger prints to sys.stdout and also logs the print to the log file.  Prevents duplicate code.
printlog = Logger(log_file=args.EXPORT+'solution.txt', status=args.save)
# Debugger helps to debug the code py printing extra information and pausing the code for checks
debug = Debugger(args.DEBUG)


# history: [bbe1, bbe2, bbe3...]
# where bbe1: [#bbe, input1, ..., output1, output1_target, output1_err_abs, output1_err_rel, output1_err_weight, ..., obj, cstr1, cstr2, ...]
history = []
if args.READ_EXPORT:
	# Open the exported results and populate `history` with their data
	history_csv = csv_read(args.EXPORT + 'history.csv', delimiters=args.DELIMITER)
	header = history_csv[0]
	history = [list(map(safe_float, h)) for h in history_csv[1:]]
	# Find the index of the output variables in the header
	output_idx = [idx-2 for idx,s in enumerate(header) if '_err_abs' in s]
	# Save the input and constraints names
	input_names = header[1:output_idx[0]]
	constraint_names = header[output_idx[-1]+6:]
	# Read the output variable names, targets and weights and put them in `outputs`
	outputs, output_names = [], []
	for i in output_idx:
		output_names.append(header[i])
		outputs.append({'target':history[0][i+1]})
	ni, no, nc = len(input_names), len(output_names), len(constraint_names)
else:
	# Open HISTORY_FILE and MDIDS Results file to gather data and put it in `history`
	history_csv = csv_read(args.HISTORY, pp=safe_float)
	mdids_csv = csv_read(args.MDIDS, pp=safe_float)
	# Check if data is present in the HISTORY_FILE and MDIDS-NOMAD results file
	assert len(history_csv) > 0, 'No data found in NOMAD\'s HISTORY_FILE'
	assert len(mdids_csv) > 0, 'No data found in MDIDS-NOMAD\'s results file'
	# Check if the history file and the mdids results file have the same number of lines
	assert len(history_csv) == len(mdids_csv), f'Mismatch between the number of lines in NOMAD\'s HISTORY_FILE ({len(history_csv)}) and MDIDS-NOMAD\'s results file ({len(mdids_csv)})'
	# Load the config file and check for the required data
	config = ConfigFile(filename=args.CONFIG)
	input_names, inputs = config.names('input'), config.params('input')
	output_names, outputs = config.names('output'), config.params('output')
	if config.has_section('constraint'):
		constraints, constraint_names = config.names('constraint'), config.params('constraint')
	else:
		constraints, constraint_names = [], []
	config.has_param('output', 'target', error_ok=False)
	ni, no, nc = len(inputs), len(outputs), len(constraints)
	# Check if number of inputs, ouputs and constraints in the log files match with config file
	assert len(history_csv[0])-1 == (ni+nc), f'Mismatch in the number of inputs/constraints: Found {len(history_csv[0])-1} in NOMAD\'s HISTORY_FILE and {ni}+{nc} in {args.CONFIG}'
	assert len(mdids_csv[0]) == no, f'Mismatch in the number of outputs: Found {len(mdids_csv[0])} in MDIDS-NOMAD\'s results and {no} in {args.CONFIG}'
	# Merge the data from history_csv and mdids_csv into a single `history` list
	for i in range(len(history_csv)):
		# Create a list from the raw data
		# Construct a list according to the format of `history` described above, and append it to `history`
		line = [i,] + history_csv[i][:ni]
		for j,o in enumerate(outputs):
			line += [mdids_csv[i][j], o['target'], mdids_csv[i][j]-o['target'], (mdids_csv[i][j]-o['target'])/o['target']]
		line += history_csv[i][ni:]
		history.append(line)
	# Save all the history results in a single CSV file if desired
	if args.save:
		# Construct the csv header
		header = ['bbe',] + input_names
		for name in output_names:
			header += [name, name+'_target', name+'_err_abs', name+'_err_rel']
		header += ['err_norm',] + constraint_names
		# Write the header and rows to the csv file
		csv_write(args.EXPORT + 'history.csv', history, header=header, delimiter=args.DELIMITER)
history = np.array(history)

# Print starting point results
printlog('~~~~~~ Starting point ~~~~~~')
printlog('Error norm: %.5g%%\n' % (history[0][-1]*100))
for i,var in enumerate(input_names):
	printlog('%15s: %.16g' % (var, history[0,1+i]))
	# e.g. Work_Boost: 125
printlog('\n' + tabulate(results_table(input_names, output_names, history[0]), headers='keys', tablefmt='presto'))

# Print solution results
solution = history[history[:,-1]==min(history[:,-1]),:][-1]
printlog('\n~~~~~~~~~ Solution ~~~~~~~~~')
printlog('Error norm: %.5g%%\n' % (solution[-1]*100))
for i,var in enumerate(input_names):
	printlog('%15s: %.16g' % (var, solution[1+i]))
	# e.g. Work_Boost: 125
printlog('\n' + tabulate(results_table(input_names, output_names, solution), headers='keys', tablefmt='presto'))


# Plot the inputs and outputs results
multi = MultiPlot(subplots=(2,1), figsize=(args.FIGSIZE,9/16*args.FIGSIZE), margins=(80,60,20,20))
for i in range(ni+no+1):
	if i < ni:
		# Plots of the input graph
		multi.plot(history[:,0], history[:,1+i], label=input_names[i])
	elif i == ni:
		# First plot of the output graph (for writing the main label)
		multi.plot(history[:,0], history[:,1+ni+5*(i-ni)], subplot_id=1, main_label='BBE', label=output_names[i-ni])
		multi.overlay_plot(history[[0,-1],0], 2*[outputs[i-ni]['target'],], linestyle='--', alpha=0.5, subplot_id=1)
	elif i == ni+no:
		# Last plot of the output graph: error norm
		multi.plot(history[:,0], history[:,-1-nc], subplot_id=1, label='Error norm')
	else:
		# Intermediate plots of the output graph
		multi.plot(history[:,0], history[:,1+ni+5*(i-ni)], subplot_id=1, label=output_names[i-ni])
		multi.overlay_plot(history[[0,-1],0], 2*[outputs[i-ni]['target'],], linestyle='--', alpha=0.5, subplot_id=1)

# Save the plot if desired
if args.save:
	multi.figure.savefig(args.EXPORT + 'all_data_history.png')

# Show the plot if desired
if args.show_graph:
	plt.show()