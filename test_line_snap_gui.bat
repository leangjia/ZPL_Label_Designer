@echo off
REM Quick launcher для GUI тестирования Line Snap

echo ================================================
echo   1C_ZEBRA - GUI TEST: Line Snap Both Ends
echo ================================================
echo.

cd /d D:\AiKlientBank\1C_Zebra

echo [1] Activating venv...
call .venv\Scripts\activate.bat

echo [2] Launching GUI...
echo.
echo ТЕСТ-КЕЙС: Line Snap to Grid - Both Ends
echo -----------------------------------------
echo 1. Добавь Line элемент (Sidebar или Menu)
echo 2. Drag Line на canvas
echo 3. Проверь Property Panel:
echo    - Position X, Y (start) должны быть кратны 1mm
echo    - End X, End Y (end) должны быть кратны 1mm
echo 4. Toggle Snap (Ctrl+G) для проверки On/Off
echo.
echo После теста закрой окно.
echo.

python main.py

echo.
echo ================================================
echo   GUI закрыт
echo ================================================
pause
