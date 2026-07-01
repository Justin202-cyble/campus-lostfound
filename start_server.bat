@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title 智慧校园失物招领与物品交换平台

echo.
echo ============================================================
echo   智慧校园失物招领与物品交换平台
echo   Smart Campus Lost & Found Exchange Platform
echo ============================================================
echo.

REM 获取本机IPv4地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "IP=%%a"
    set "IP=!IP: =!"
    if not "!IP!"=="127.0.0.1" set "LOCAL_IP=!IP!"
)

if "%LOCAL_IP%"=="" set "LOCAL_IP=未知"

echo   本机局域网IP: %LOCAL_IP%
echo.
echo ============================================================
echo   [访问地址]
echo ============================================================
echo.
echo   本机访问:       http://127.0.0.1:5000
echo   局域网访问:     http://%LOCAL_IP%:5000
echo.
echo   [演示账号]
echo      admin    / admin123  (管理员)
echo      zhangsan / 123456    (学生)
echo.
echo ============================================================
echo   [提示]
echo   - 其他设备请连接同一校园WiFi后访问局域网地址
echo   - 如无法访问，右键 open_firewall.bat -> 以管理员身份运行
echo   - 按 Ctrl+C 停止服务
echo ============================================================
echo.

cd /d %~dp0
python run.py
pause
