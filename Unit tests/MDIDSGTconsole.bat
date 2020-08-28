@echo off
title Unit test for MDIDS-GT console

"..\MDIDSGTconsole.exe" "MDIDSGTconsole\EngineV2500-Master" temp.txt > NUL 2>&1

IF %ERRORLEVEL%==0 (
	echo MDIDS-GT console was detected succesfully.
	del temp.txt
) ELSE IF %ERRORLEVEL%==9009 (
	echo MDIDS-GT console was not detected ^(%ERRORLEVEL%^).
) ELSE (
	echo MDIDS-GT console was detected but an unexpected error occured ^(%ERRORLEVEL%^).
)

echo.
pause