@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo   需要管理员权限来开放防火墙端口
    echo   即将弹出 UAC 提示框，请点击"是"
    echo ============================================
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ============================================
echo   正在开放防火墙端口 5000...
echo ============================================
echo.

:: 删除旧规则（如果存在）
netsh advfirewall firewall delete rule name="CampusLostFound" >nul 2>&1

:: 添加新规则
netsh advfirewall firewall add rule name="CampusLostFound" dir=in action=allow protocol=TCP localport=5000 profile=any

if %errorlevel% equ 0 (
    echo   [成功] 防火墙端口 5000 已开放！
    echo.
    echo   ----------------------------------------
    echo   局域网访问地址：
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
        set "IP=%%a"
        set "IP=!IP: =!"
        if not "!IP!"=="127.0.0.1" (
            echo     http://!IP!:5000
        )
    )
    echo   ----------------------------------------
    echo.
    echo   其他设备连接同一校园WiFi后，浏览器打开上述地址即可
) else (
    echo   [失败] 无法自动添加防火墙规则
    echo.
    echo   请手动操作（只需30秒）：
    echo   1. 按 Win+R，输入 wf.msc，回车
    echo   2. 点击左侧"入站规则"
    echo   3. 点击右侧"新建规则..."
    echo   4. 选择"端口" -> 下一步
    echo   5. 选择"TCP"，输入"5000" -> 下一步
    echo   6. 选择"允许连接" -> 下一步 -> 下一步
    echo   7. 名称输入"CampusLostFound" -> 完成
)

echo.
pause
