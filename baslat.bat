@echo off
title PhishAware - Otonom Oltalama Simulasyonu & Guvenlik Platformu
cd /d "%~dp0"
chcp 65001 >nul
echo =================================================================
echo   [+] PHISHAWARE - Otonom Oltalama Simulasyonu Baslatiliyor...
echo =================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYCMD=python
) else (
    set PYCMD="C:\Users\pc\AppData\Local\Programs\Python\Python311\python.exe"
)

%PYCMD% -c "import fastapi, uvicorn, sqlalchemy" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] Gerekli kutuphaneler eksik, requirements.txt yukleniyor...
    %PYCMD% -m pip install -r requirements.txt
)

echo Tarayiciniz otomatik olarak acilacaktir: http://127.0.0.1:8000/dashboard
echo Sunucuyu durdurmak icin bu pencereyi kapatabilir veya Ctrl+C yapabilirsiniz.
echo.

start http://127.0.0.1:8000/dashboard

%PYCMD% -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

echo.
echo Sunucu kapandi.
pause
