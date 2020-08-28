@echo off
title Unit test for NOMAD

"%NOMAD_HOME%\bin\nomad.exe" "NOMAD\params.txt" > NUL 2>&1

IF %ERRORLEVEL%==0 (
	echo NOMAD was detected succesfully.
) ELSE IF %ERRORLEVEL%==9009 (
	echo NOMAD was not detected ^(%ERRORLEVEL%^).
) ELSE (
	echo NOMAD was detected but an unexpected error occured ^(%ERRORLEVEL%^).
)

echo.
pause