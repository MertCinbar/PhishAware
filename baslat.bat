@echo off
title PhishAware Sunucusu
cd /d "%~dp0"
echo ===================================================
echo   PhishAware Oltalama Simulasyon Sunucusu Baslatiliyor...
echo ===================================================
echo.
echo Tarayicinizda su adres acilacak: http://127.0.0.1:8000/dashboard
echo Sunucuyu durdurmak icin bu pencereyi kapatabilir veya Ctrl+C yapabilirsiniz.
echo.

start http://127.0.0.1:8000/dashboard

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) else (
    "C:\Users\pc\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
)
pause
