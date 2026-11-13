@echo off
chcp 65001 >nul
title PhishAware - Mobil ve Dış Ağ Erişim Tüneli
cd /d "%~dp0"

echo ================================================================
echo   PhishAware - Mobil ve Dış Ağ Erişim Yardımcısı
echo ================================================================
echo.
echo Telefondan e-posta veya Telegram linklerini açarken:
echo.
echo [1] KİŞİSEL ERİŞİM NOKTASI (HOTSPOT) YÖNTEMİ (Tünelsiz):
echo     Bilgisayarınızı telefonunuzun Mobil Erişim Noktasına bağlarsanız,
echo     aynı özel alt ağda olacağınız için telefonunuz linkleri doğrudan açar.
echo.
echo [2] ÜCRETSİZ CANLI HTTPS TÜNELİ (Pinggy.io):
echo     Hiçbir program yüklemeden, Windows SSH ile port 8000 için
echo     dünyanın her yerinden (4G/5G dahil) erişilebilir canlı bir
echo     HTTPS bağlantısı ve karekod üretir.
echo.
echo [3] LOCALHOST.RUN TÜNELİ:
echo     Alternatif anlık ücretsiz HTTPS tüneli.
echo.
echo ================================================================
echo.
set /p secim="Seçiminiz (Varsayılan 2 - Pinggy Tüneli) [1/2/3]: "

if "%secim%"=="1" goto hotspot_info
if "%secim%"=="3" goto localhost_run

:pinggy
echo.
echo [*] Pinggy üzerinden ücretsiz HTTPS tüneli başlatılıyor...
echo [*] Terminalde beliren https://xxxx.pinggy.link adresini kopyalayıp
echo     Yönetim Paneli > 'Ağ / Mobil Erişim' alanına yapıştırabilir veya
echo     .env dosyasındaki BASE_URL alanına yazabilirsiniz.
echo.
ssh -p 443 -R0:localhost:8000 qr@a.pinggy.io
pause
exit /b

:localhost_run
echo.
echo [*] Localhost.run üzerinden ücretsiz HTTPS tüneli başlatılıyor...
echo.
ssh -R 80:localhost:8000 nokey@localhost.run
pause
exit /b

:hotspot_info
echo.
echo [!] Bilgisayarınızı cep telefonunuzun Wi-Fi paylasimina bagladiktan sonra
echo     yeni IP adresinizi ogrenmek icin Enter'a basiniz.
pause >nul
ipconfig | findstr /i "IPv4"
echo.
echo Lutfen telefonun bagli oldugu IP adresini kontrol ediniz.
pause
exit /b
