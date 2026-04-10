@echo off
chcp 65001 >nul
echo 正在复制命理模块...

set SOURCE_DIR=G:\07.Project\02.性格测试\01.八字排盘与计算\bazi-master_new\bazi-master
set TARGET_DIR=%~dp0backend\bazi_modules

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

REM 复制所有 Python 文件
xcopy /Y /E "%SOURCE_DIR%\*.py" "%TARGET_DIR%\" >nul 2>&1

REM 复制子目录
xcopy /Y /E "%SOURCE_DIR%\lunar_python" "%TARGET_DIR%\lunar_python\" >nul 2>&1
xcopy /Y /E "%SOURCE_DIR%\bidict" "%TARGET_DIR%\bidict\" >nul 2>&1

echo 复制完成！
echo.
echo 已复制以下模块：
dir /B "%TARGET_DIR%\*.py" 2>nul | findstr /V ".gitkeep"
pause
