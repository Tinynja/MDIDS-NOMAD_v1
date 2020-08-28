__author__ = 'Amine Kchouk'
__credits__ = ['John Kidikian']
__version__ = "1.0"
__email__ = "amine.kchouk@polymtl.ca"
__status__ = "Development"


# Built-in libraries
from argparse import ArgumentParser
from itertools import chain, zip_longest
import os

# Pipy libraries
import numpy as np
import matplotlib.pyplot as plt

# User libraries
from lib.progressprinter import ProgressPrinter
from lib.configfile import ConfigFile
from lib.multiplot import MultiPlot
from lib.debugger import Debugger
from lib.useful_functions import csv_read, csv_write, safe_float


# Parse input arguments
parser = ArgumentParser()
options = parser.add_argument_group('Execution options')
options.add_argument('-ns', '--no-save', help='don\'t save the results', dest='save', action='store_false')
options.add_argument('-sg', '--show-graph', help='show the graphs', action='store_true')
options.add_argument('--debug', help='activates debug-mode', dest='DEBUG', action='store_true')
paths = parser.add_argument_group('Paths')
paths.add_argument('--config', help='path of the config file', dest='CONFIG', default='config.ini')
paths.add_argument('--export', help='path of the folder where results will be exported', dest='EXPORT', default='Results')
fileformat = parser.add_argument_group('File format')
fileformat.add_argument('-d', '--delimiter', help='delimiter used when generating csv file', dest='DELIMITER', default=';')
fileformat.add_argument('-size', '--figure-size', help='Size of the figures', dest='FIGSIZE', type=float, default=14)
args = parser.parse_args()
# Append a slash to the end of args.EXPORT if not present:
if args.EXPORT[-1] not in ('/', '\\'): args.EXPORT += '/'

# Debugger helps to debug the code py printing extra information and pausing the code for checks
debug = Debugger(args.DEBUG)
# ProgressPrinter makes it easy to have progress bars
progressprint = ProgressPrinter()

# Retrieve the input variables and the sensitivity ranges
config = ConfigFile(filename=args.CONFIG)
input_names, inputs = config.names('input'), config.params('input')
output_names, outputs = config.names('output'), config.params('output')

# Setup some variables used to track the progress of the sensitiviy matrix generation
progress, max_progress = 0, sum([d['sensitivity_npoints'] for d in inputs])
# sens_matrix: [output1, output2, ...] where output1 = [input1_x, input1_y, ...]
sens_matrix = [[] for i in outputs]
for i,d in enumerate(inputs):
	# For every input variable, generate sensitivity results in a log file
	debug('Deleting \'Logs/MDIDS-NOMAD_sensitivity.log\'...')
	try:
		os.remove('Logs/MDIDS-NOMAD_sensitivity.log')
	except FileNotFoundError:
		pass
	debug('Check that \'Logs/MDIDS-NOMAD_sensitivity.log\' has been deleted.', pause=True)
	# Generate the points where the input variable will be evaluated, based on the config file parameters
	input_points = list(np.linspace(d['sensitivity_range'][0], d['sensitivity_range'][1], d['sensitivity_npoints']))
	# Run MDIDS for every evaluation point
	for x in input_points:
		progress += 1
		if not args.DEBUG: progressprint(f'Generating sensitivity matrix ({progress/max_progress*100:.0f}%)')
		debug(f'Creating a \'sensitivity.input\' file ({progress}/{max_progress})...')
		with open('sensitivity.input', 'w') as f:
			f.write(' '.join(map(str, [np.mean(j['sensitivity_range']) for j in inputs[:i]] + [x,] + [np.mean(j['sensitivity_range']) for j in inputs[i+1:]])))
		debug('Check that \'sensitivity.input\' has been created and verify its contents.', pause=True)
		if progress == 1:
			debug('Running \'wrapper.py\'... This should create \'Logs/MDIDS-NOMAD_sensitivity.log\'.')
		else:
			debug('Running \'wrapper.py\'... This should append new results to \'Logs/MDIDS-NOMAD_sensitivity.log\'.')
		os.system('python.exe wrapper.py -log Logs/MDIDS-NOMAD_sensitivity.log sensitivity.input > NUL')
		if progress == 1:
			debug('Check that \'Logs/MDIDS-NOMAD_sensitivity.log\' has been created and verify its contents.', pause=True)
		else:
			debug('Check that \'Logs/MDIDS-NOMAD_sensitivity.log\' has been modified.', pause=True)
	# Read the results from the log file and save them into the sens_matrix list
	sens_results = np.array(csv_read('Logs/MDIDS-NOMAD_sensitivity.log', pp=safe_float))
	for i in range(len(sens_matrix)):
		sens_matrix[i].append(input_points)
		sens_matrix[i].append(sens_results[:,i])
if not args.DEBUG: progressprint.stop('Done!')
os.remove('sensitivity.input')

# The sensitivity matrix has been generated, now save the results in CSV files and plot the results
if args.save:
	for o,matrix in enumerate(sens_matrix):
		# Save each output's sensitivity matrix in a CSV file
		header = list(chain.from_iterable((i, output_names[o]) for i in input_names))
		csv_write(args.EXPORT + 'sensitivity_' + output_names[o] + '.csv', list(zip_longest(*matrix)), header=header, delimiter=args.DELIMITER)
		sens = MultiPlot(margins=(-1,60,20,20), figsize=(args.FIGSIZE,9/16*args.FIGSIZE))
		for i in range(int(len(matrix)/2)):
			if i == 0:
				sens.plot(matrix[2*i], matrix[2*i+1], side='bottom', main_label=output_names[o], label=input_names[i])
			else:
				sens.plot(matrix[2*i], matrix[2*i+1], side='bottom', label=input_names[i])
		sens.figure.savefig(args.EXPORT + 'sensitivity_' + output_names[o] + '.png')

# Show the plot if desired
if args.show_graph:
	plt.show()