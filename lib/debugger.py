class Debugger:
	def __init__(self, status=True):
		self.status = status
	
	def __call__(self, *args, pause=False, **kwargs):
		if self.status:
			if pause:
				kwargs.pop('end', None)
				print('[DEBUG]', *args, '(Press enter to continue...)', **kwargs, end='')
				input()
			else:
				print('[DEBUG]', *args, **kwargs)