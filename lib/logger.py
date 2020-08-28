# Built-in libraries
import sys
import os

# Logger makes it so that all printed values will also be written to a log file. Prevents duplicate code.
class Logger:
	def __init__(self, log_file, erase=True, status=False):
		self.status = status
		if status:
			if erase:
				self.log_file = open(log_file, 'w')
			else:
				self.log_file = open(log_file, 'a')

	def __call__(self, *args, **kwargs):
		print(*args, file=kwargs.pop('file', None), **kwargs)
		if self.status: print(*args, file=self.log_file, **kwargs)