@echo off
REM Запуск ZPL Label Designer с параметром JSON файла
cd /d "D:\AiKlientBank\1C_Zebra"

REM Если есть параметр (путь к JSON) - передаем его
if "%~1"=="" (
    start "" ".venv\Scripts\pythonw.exe" "main.py"
) else (
    start "" ".venv\Scripts\pythonw.exe" "main.py" "%~1"
)

exit
