@echo off
REM 启动 ZPL 标签设计器，支持 JSON 文件参数
cd /d "D:\AiKlientBank\1C_Zebra"

REM 如果有参数（JSON文件路径）- 传递给程序
if "%~1"=="" (
    start "" ".venv\Scripts\pythonw.exe" "main.py"
) else (
    start "" ".venv\Scripts\pythonw.exe" "main.py" "%~1"
)

exit