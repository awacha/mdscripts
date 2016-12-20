set MENU_DIR="%PREFIX%"\Menu
mkdir "%MENU_DIR%"
"%PYTHON%" setup.py install
if errorlevel 1 exit 1
