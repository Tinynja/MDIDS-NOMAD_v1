# Built-in libraries
import threading
from itertools import cycle

class ProgressPrinter():
	def __init__(self):
		self._finished_event = threading.Event()
		self._finished_event.set()
		self._current_output = ''
		self.idot = 1

	def print(self, text):
		self._stop_progress_bar()
		print('\r' + text + ' '*(len(self._current_output)-len(text)), end='', flush=True)
		self._finished_event.clear()
		self._progress_bar_thread = threading.Thread(target=self._run_progress_bar, args=(text,))
		self._progress_bar_thread.start()

	def stop(self, termination_text=''):
		if self._stop_progress_bar():
			print('\r' + self._current_output + ' ' + termination_text)
	
	def _stop_progress_bar(self):
		if not self._finished_event.is_set():
			self._finished_event.set()
			self._progress_bar_thread.join()
			return True

	def _run_progress_bar(self, text):
		n = 4
		while not self._finished_event.is_set():
			self.idot = self.idot%n+1
			self._current_output = text + self.idot*'.'
			print('\r' + self._current_output + (n-self.idot)*' ', end='', flush=True)
			self._finished_event.wait(0.2)

	def __call__(self, text=None):
		if text is not None:
			self.print(text)
		else:
			self.stop()

	def __del__(self):
		self.stop()