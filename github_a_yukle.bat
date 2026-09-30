@echo off
title GitHub'a Yukle - PhishAware
cd /d "%~dp0"
echo ===================================================
echo   PhishAware - GitHub'a Otomatik Yukleme Araci
echo ===================================================
echo.
echo 1. Asama: Tarayicinizda GitHub yeni depo sayfasi aciliyor...
echo    (Depo adi 'PhishAware' otomatik doldurulacak, sadece 'Create repository' butonuna tiklayin)
echo.

start "" "https://github.com/new?name=PhishAware&description=Otonom+Oltalama+Simulasyonu+ve+Farkindalik+Platformu"

echo 2. Asama: GitHub sayfasinda yesil 'Create repository' butonuna tikladiktan sonra
echo           bu pencereye donup herhangi bir tusa basin...
echo.
pause >nul

echo.
echo [BILGI] Kodlar GitHub'a aktariliyor (git push -u origin main)...
echo.

"C:\Program Files\Git\cmd\git.exe" push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ===================================================
    echo   TEBRIKLER! Projeniz basariyla GitHub'a yuklendi!
    echo   Depo Adresi: https://github.com/MertCinbar/PhishAware
    echo ===================================================
    start "" "https://github.com/MertCinbar/PhishAware"
) else (
    echo.
    echo [DIKKAT] Aktarim sirasinda bir durum olustu. 
    echo Lutfen https://github.com/new adresinde deponun olusturuldugundan emin olun.
)
echo.
pause
