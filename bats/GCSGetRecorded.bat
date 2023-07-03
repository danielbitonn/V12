@echo off
if %1.==. (set from=00:01) else (set from=%1)

set mydate=%date:~10,4%-%date:~4,2%-%date:~7,2%

set mytime=%time:~0,5%
set mytime=%mytime: =0%
set nameableTime=%mytime:~0,2%-%mytime:~3,2%
set nameableTime2=%mytime:~0,2%.%mytime:~3,2%
set nameableFrom=%from:~0,2%.%from:~3,2%
echo on
echo %mydate%T%from% -t %mydate%T%mytime%

if not exist data\push_exported_data\ mkdir data\push_exported_data\

echo ###################################################################################################################
@REM Analog data press-state-history*:
S:\Press\PressTools.EsExporter.exe -i press-state-history* -f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\

echo ###################################################################################################################
@REM Analog data restart*:
S:\Press\PressTools.EsExporter.exe -i restart* -f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\

echo ###################################################################################################################
@REM Analog data restart-history*:
S:\Press\PressTools.EsExporter.exe -i restart-history* -f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\

echo ###################################################################################################################
@REM Analog data print-attempt*:
S:\Press\PressTools.EsExporter.exe -i print-attempt* -f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\

echo ###################################################################################################################
@REM Analog data print-session*:
S:\Press\PressTools.EsExporter.exe -i print-session* -f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\

echo ###################################################################################################################
@REM Analog data *event-history*:
S:\Press\PressTools.EsExporter.exe -i *event-history* -f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\

echo ###################################################################################################################
@REM Analog data event-history*:
S:\Press\PressTools.EsExporter.exe -i event-history* -f %mydate%T%from% -t %mydate%T%mytime% -o data\push_exported_data\
