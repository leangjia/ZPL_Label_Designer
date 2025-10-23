@echo off
REM 用于GUI测试Line Snap的快速启动器

echo ================================================
echo   1C_ZEBRA - GUI测试: Line Snap Both Ends
echo ================================================
echo.

cd /d D:\AiKlientBank\1C_Zebra

echo [1] 正在激活虚拟环境...
call .venv\Scripts\activate.bat

echo [2] 正在启动GUI...
echo.
echo 测试用例: Line Snap to Grid - Both Ends
echo -----------------------------------------
echo 1. 添加Line元素（通过侧边栏或菜单）
echo 2. 将Line拖拽到画布上
echo 3. 检查属性面板：
echo    - 起始位置X、Y坐标应为1mm的倍数
echo    - 结束位置X、Y坐标应为1mm的倍数
echo 4. 切换吸附功能（Ctrl+G）以测试开启/关闭状态
echo.
echo 测试完成后请关闭窗口。
echo.

python main.py

echo.
echo ================================================
echo   GUI已关闭
echo ================================================
pause