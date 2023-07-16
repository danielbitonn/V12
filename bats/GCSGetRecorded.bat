@echo off
if %1.==. (set from=00:01) else (set from=%1)
set from=%from%:00

set mydate=%date:~10,4%-%date:~4,2%-%date:~7,2%
set mytime=%time:~0,5%
set mytime=%mytime: =0%:00
set nameableTime=%mytime:~0,2%-%mytime:~3,2%
set nameableTime2=%mytime:~0,2%.%mytime:~3,2%
set nameableFrom=%from:~0,2%.%from:~3,2%

set pressSN=b70001003

echo on


if not exist data\push_exported_data\%pressSN%\%mydate%\ mkdir data\push_exported_data\%pressSN%\%mydate%\

echo ### Extract...
@REM Analog data:
S:\Press\PressTools.EsExporter.exe -i press-state-history* 	-f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\%pressSN%\%mydate%\

echo ### Extract...
S:\Press\PressTools.EsExporter.exe -i event-history* 		-f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\%pressSN%\%mydate%\

echo ### Extract...
S:\Press\PressTools.EsExporter.exe -i restart-history* 		-f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\%pressSN%\%mydate%\

echo ### Extracting Completed!