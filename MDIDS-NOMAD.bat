@echo off
setlocal EnableDelayedExpansion
title MDIDS-NOMAD Runner

:: Deleting files and create folder
del Logs\MDIDS-NOMAD_results.log 2> NUL

echo ~~~~ NOMAD Optimization ~~~~
set "startTime=%time: =0%"
"%NOMAD_HOME%\bin\nomad.exe" params.txt
set "endTime=%time: =0%"
:: Get elapsed time:
set "end=!endTime:%time:~8,1%=%%100)*100+1!"  &  set "start=!startTime:%time:~8,1%=%%100)*100+1!"
set /A "elap=((((10!end:%time:~2,1%=%%100)*60+1!%%100)-((((10!start:%time:~2,1%=%%100)*60+1!%%100), elap-=(elap>>31)*24*60*60*100"
:: Convert elapsed time to HH:MM:SS:CC format:
set /A "cc=elap%%100+100,elap/=100,ss=elap%%60+100,elap/=60,mm=elap%%60+100,hh=elap/60+100"
:: Display elapsed time
echo Elapsed time:  %hh:~1%%time:~2,1%%mm:~1%%time:~2,1%%ss:~1%%time:~8,1%%cc:~1%
echo.

:: Post-processing
python.exe postprocess.py
echo.

:: Sensitivity matrix
python.exe sensitivity.py
echo.

pause