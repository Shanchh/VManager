@echo off
:: 確保以管理員身份運行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Administrator privileges are required to run this script!
    pause
    exit
)

:: 切換到腳本所在目錄
cd /d "%~dp0"

:: 安裝服務
python test.py install

:: 提示完成
echo Service installed and started successfully!
pause