import os
import datetime
import subprocess
import sys
# TODO: Create an exporting functionality form press
# check for command line argument
from_time = sys.argv[1] if len(sys.argv) > 1 else '00:01'

# get current date and time
now = datetime.datetime.now()

# format date as YYYY-MM-DD
mydate = now.strftime('%Y-%m-%d')

# format time as HH:MM
mytime = now.strftime('%H:%M').zfill(5)  # zfill ensures leading zero

# format time as HH.MM
nameable_time2 = mytime.replace(':', '.')

# format from_time as HH.MM
nameable_from = from_time.replace(':', '.')

# create directory if it doesn't exist
if not os.path.exists('C:\\ExportedEsData'):
    os.makedirs('C:\\ExportedEsData')

# execute the external program
cmd = f'S:\\Press\\PressTools.EsExporter.exe -i press-state-history* -f {mydate}T{nameable_from} -t {mydate}T{nameable_time2} -o C:\\ExportedEsData\\'
subprocess.call(cmd, shell=True)
