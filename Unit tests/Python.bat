@echo off
title Unit test for Python 3

python.exe "Python\python_check.py" 2> NUL

IF %ERRORLEVEL%==9009 (
	echo Python was not detected ^(%ERRORLEVEL%^).
) ELSE IF NOT %ERRORLEVEL%==0 (
	echo Python was detected but an unexpected error occured ^(%ERRORLEVEL%^).
)

echo.
pause