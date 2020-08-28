# Built-in libraries
from configparser import ConfigParser
import re
import os

# User libraries
from lib.useful_functions import safe_float, autosplit

class ConfigFile:
	def __init__(self, filename='config.ini', warn=True):
		assert os.path.isfile(filename), f'Config file \'{filename}\' doesn\'t exist'
		self.filename = filename
		self.config = ConfigParser()
		self.config.read(filename)

		self.warn = warn

		self._retrieve_params()
		self._convert_data()
	
	def main(self):
		self.has_section('main', error_ok=False)
		return self.sections['main']

	def params(self, section, dict_format=False):
		assert section != 'main', 'Use \'main\' method to access the main section\'s data'
		self.has_section(section, error_ok=False)
		if dict_format:
			return self.sections[section]
		else:
			return list(self.sections[section].values())
	
	def names(self, section):
		assert section != 'main', 'Use \'main\' method to access the main section\'s data'
		self.has_section(section, error_ok=False)
		return list(self.sections[section])

	def _set_default(self, section, param, value, dtype_check=(lambda d: isinstance(d, float)), convert=None):
		self.has_section(section, error_ok=False)
		for sub_s in self.sections[section]:
			if param not in self.sections[section][sub_s] or not dtype_check(self.sections[section][sub_s][param]):
				try:
					self.sections[section][sub_s][param] = convert(self.sections[section][sub_s][param])
				except (TypeError, ValueError):
					if self.warn: print(f'[WARN] Using default value ({value}) for parameter \'{param}\' of {section} variable \'{sub_s}\'')
					self.sections[section][sub_s][param] = value
	
	def _convert_data(self):
		if self.has_param('input', 'sensitivity_range'):
			for sub_s in self.sections['input']:
				self.sections['input'][sub_s]['sensitivity_range'] = autosplit(self.sections['input'][sub_s]['sensitivity_range'], pp=float)
				assert len(self.sections['input'][sub_s]['sensitivity_range']) == 2, f'Incorrect \'sensitivity\' parameter format for the input variable \'{sub_s}\''
		if self.has_param('input', 'sensitivity_npoints'):
			self._set_default('input', 'sensitivity_npoints', 10, dtype_check=(lambda d: isinstance(d, int)), convert=int)

	def has_param(self, section, param, error_ok=True):
		assert self.has_section(section), f'\'{section}\' section not present in {self.filename}'
		if section == 'main':
			check = param in self.sections[section]
		else:
			check = all([param in v for k,v in self.sections[section].items()])
		if not error_ok:
			assert check, f'\'{param}\' parameter not found in {self.filename}/{section}'
		return check

	def has_section(self, section, error_ok=True):
		check = section in self.sections and bool(self.sections[section])
		if not error_ok:
			assert check, f'\'{section}\' section not found in {self.filename}'
		return check
	
	def _retrieve_params(self):
		self._find_section_idx()
		# self.sections: {'main': {'master_file':'V2500'}, 'input':{'Work_Fan': {'sensibility':'23,30', 'weight':1, ...}}, ...}
		self.sections = {}
		for i,v in enumerate(self._section_idx[:-1]):
			if v[0] == 'main':
				self.sections[v[0]] = dict(self.config[v[2]])
			else:
				self.sections[v[0]] = {}
				for sub_s in self.config.sections()[ v[1]+1 : self._section_idx[i+1][1] ]:
					self.sections[v[0]][sub_s] = {k:safe_float(v) for k,v in self.config[sub_s].items()}
	
	def _find_section_idx(self):
		r = re.compile('(?i)main|input|output|constraint')
		# section_idx: [['main', 0, 'Main'], ['input', 5, 'INPUTS'], ...]
		self._section_idx = []
		for i,s in enumerate(self.config.sections()):
			parsed = r.search(s)
			if parsed:
				self._section_idx.append([parsed[0].lower(), i, s])
		self._section_idx.append(['eof', len(self.config.sections())+1])