import sys

if sys.version_info.major >= 3:
	print('[SUCCESS] Python was detected successfully.')
else:
	print('[ERROR] Python was detected but the wrong version is installed (%s)' % '.'.join(map(str,sys.version_info[0:3])))