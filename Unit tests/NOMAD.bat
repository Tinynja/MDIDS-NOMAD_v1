@echo off
title Unit test for NOMAD

"%NOMAD_HOME%\bin\nomad.exe" "NOMAD\params.txt" > NUL 2>&1

IF %ERRORLEVEL%==0 (
	echo [SUCCESS] NOMAD was detected successfully.
) ELSE IF %ERRORLEVEL%==9009 (
	echo [ERROR] NOMAD was not detected ^(%ERRORLEVEL%^).
) ELSE (
	echo [WARNING] NOMAD was detected but an unexpected error occured ^(%ERRORLEVEL%^).
)

echo.
pause