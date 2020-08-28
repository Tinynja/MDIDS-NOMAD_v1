@echo off
title Unit test for pip and dependencies

pip.exe -V > NUL 2>&1

IF %ERRORLEVEL%==0 (
	echo [SUCCESS] Pip was detected succesfully.
	echo.
	python.exe -m pip install --upgrade pip
	pip.exe install -r "Pip\requirements.txt"
) ELSE IF %ERRORLEVEL%==9009 (
	echo [ERROR] Pip was not detected ^(%ERRORLEVEL%^).
) ELSE (
	echo [WARNING] Pip was detected but an unexpected error occured ^(%ERRORLEVEL%^).
)

echo.
pause