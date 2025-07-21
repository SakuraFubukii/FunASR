@echo off
chcp 65001 >nul
title OCR音频识别系统 - Web版本

echo ====================================================
echo OCR音频识别系统 - Web版本启动脚本
echo ====================================================
echo.

echo 正在启动Web版本...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 启动Web应用
python web_launcher.py

echo.
echo 程序已退出
pause
