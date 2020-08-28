@echo off
title Unit test for Python 3

python.exe "Python\python_check.py" 2> NUL

IF %ERRORLEVEL%==9009 (
	echo [ERROR] Python was not detected ^(%ERRORLEVEL%^).
) ELSE IF NOT %ERRORLEVEL%==0 (
	echo [WARNING] Python was detected but an unexpected error occured ^(%ERRORLEVEL%^).
)

echo.
pause