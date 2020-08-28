__author__ = 'Amine Kchouk'
__credits__ = ['John Kidikian']
__version__ = "0.3"
__email__ = "amine.kchouk@polymtl.ca"
__status__ = "Development"


# Built-in libraries
from argparse import ArgumentParser
from lib.configfile import ConfigFile
import os, csv, re

# Pipy libraries
import numpy as np


# Parse the input file path
parser = ArgumentParser()
parser.add_argument('INPUT_FILE')
parser.add_argument('-ns', '--no-save', help='don\'t save the results in log file', dest='save', action='store_false')
parser.add_argument('-log', help='path of the log file where to append results', dest='LOG', default='Logs/MDIDS-NOMAD_results.log')
args = parser.parse_args()

# Read the config file and check for common errors
config = ConfigFile(filename='config.ini', warn=False)
config.has_section('main', error_ok=False)
config.has_param('main', 'master_file', error_ok=False)
config.has_param('output', 'target', error_ok=False)
assert os.path.isfile(config.main()['master_file']), f'MDIDS master file `{config.main()["master_file"]}` file doesn\'t exist'

# Gather the data from the config file
target = np.array([])
for var in config.params('output'):
	target = np.append(target, var['target'])

# Execute MDIDS
os.makedirs(os.path.split(args.LOG)[0], exist_ok=True)
os.system(f'MDIDSGTconsole {config.main()["master_file"]} Logs/MDIDS_output.txt -OPT {args.INPUT_FILE} Logs/MDIDS_opt-output.txt > Logs/MDIDS_display.log')

# Reading the MDIDS output values of SFC, OPR, Thrust
with open('Logs/MDIDS_opt-output.txt', 'r') as f:
	result = f.read().upper().replace(',', '.')
	if args.save:
		# os.makedirs('Logs', exist_ok=True)
		with open(args.LOG, 'a') as f:
			f.write(result)
	if 'NAN' in result:
		exit(code=1)
	else:
		result = np.array(list(map(float, result.split())))

# Calculating the error and displaying the norm to NOMAD
error = abs((result-target)/target)

print(np.linalg.norm(error, ord=float('2')))