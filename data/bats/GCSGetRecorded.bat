@echo off
if %1.==. (set from=00:01) else (set from=%1)

set mydate=%date:~10,4%-%date:~4,2%-%date:~7,2%

set mytime=%time:~0,5%
set mytime=%mytime: =0%
set nameableTime=%mytime:~0,2%-%mytime:~3,2%
set nameableTime2=%mytime:~0,2%.%mytime:~3,2%
set nameableFrom=%from:~0,2%.%from:~3,2%
echo on

if not exist C:\ExportedEsData mkdir C:\ExportedEsData


@REM Analog data: 
S:\Press\PressTools.EsExporter.exe -i press-state-history* -f %mydate%T%from% -t %mydate%T%mytime% -o C:\ExportedEsData\

REM node S:\Press\PressTools.EsExporter.exe -i press-state-history* -f %mydate%T%from% -t %mydate%T%mytime% -f C:\ExportedEsData\GCS_Events.csv

REM Copy...
robocopy C:\ExportedEsData "\\iifs3.inr.rd.hpicorp.net\kedemst$\%COMPUTERNAME%\Recorder Data\%mydate%"


