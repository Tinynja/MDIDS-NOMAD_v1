import sys

if sys.version_info.major >= 3:
	print('Python was detected succesfully.')
else:
	print('Python was detected but the wrong version is installed (%s)' % '.'.join(map(str,sys.version_info[0:3])))