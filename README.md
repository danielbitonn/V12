# V12
-
pip install -r requirements.txt
click "More info" and then "Run anyway" when they see the Windows SmartScreen warning

Exececute compile desktop app into .exe file using cmd In your terminal or command prompt, navigate to the directory containing your Python script (main.py in your case). Then run the following command to create an executable

"pyinstaller --onefile --name="my_executable" --icon=path_to_your_icon.ico main.py"
"pyinstaller --onefile --name="V12Daily" --icon=src/ref/media/v12.ico --add-data "config.json;." main.py"