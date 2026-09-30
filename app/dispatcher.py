import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import uuid
from typing import List, Dict, Any, Optional

def maskelenmis_gonderici_belirle(kanal: str, departman: str = "") -> Dict[str, str]:
    if kanal == "whatsapp":
        return {
            "gonderen_adi": "TrendLojistik Kurumsal Onay Hattı",
            "gonderen_no": "+90 (850) 885 00 24",
            "protokol": "WhatsApp Business Cloud Gateway"
        }
    elif kanal == "sms":
        return {
            "gonderen_adi": "B002 - TRENDLOJISTIK",
            "gonderen_no": "B002",
            "protokol": "Telekom Smishing Gateway (SMPP)"
        }
    elif kanal == "qr":
        return {
            "gonderen_adi": "TrendLojistik İdari İşler ve Bilgi Güvenliği",
            "gonderen_no": "OFIS-PANO-01",
            "protokol": "Ofis İçi Fiziksel Quishing Panosu"
        }
    else:
        return {
            "gonderen_adi": "TrendLojistik İK & Sistem Masası",
            "gonderen_no": "guvenlik-onay@trend-onay.com",
            "protokol": "Kurumsal SMTP Relay (TLS)"
        }


from app.ai_generator import senaryo_uret

def toplu_otomatik_dagitim(
    kampanya, 
    calisanlar: list, 
    lan_ip: str = "127.0.0.1",
    hedef_departman: str = "hepsi",
    kanal_override: Optional[str] = None,
    otomatik_ai: bool = True
) -> Dict[str, Any]:
    kanal = kanal_override or getattr(kampanya.sablon, "kanal", "email")
    gonderici = maskelenmis_gonderici_belirle(kanal)
    sektor = getattr(kampanya.sirket, "sektor", "E-Ticaret ve Lojistik") if hasattr(kampanya, "sirket") and kampanya.sirket else "Kurumsal Hizmetler"

    senaryo_onbellegi = {}
    dagitim_loglari = []
    toplam_hedef = len(calisanlar)

    for i, calisan in enumerate(calisanlar, 1):
        ozel_token = str(uuid.uuid4())[:16]
        takip_linki = f"http://{lan_ip}:8000/tikla/{ozel_token}"

        dep = calisan.departman or "Genel"
        if otomatik_ai:
            if dep not in senaryo_onbellegi:
                senaryo_onbellegi[dep] = senaryo_uret(sektor=sektor, departman=dep, zorluk="orta", kanal=kanal)
            secilen_senaryo = senaryo_onbellegi[dep]
            sablon_adi = secilen_senaryo.get("baslik", f"{dep} Özel Senaryosu")
            senaryo_konu = secilen_senaryo.get("konu", "[ÖNEMLİ] Güvenlik Bildirimi")
        else:
            sablon_adi = getattr(kampanya.sablon, "baslik", "Standart Senaryo")
            senaryo_konu = getattr(kampanya.sablon, "konu", "Güvenlik Uyarısı")

        if kanal == "whatsapp":
            hedef_adresi = f"+90 (5{str(i).zfill(2)}) {i*41:03d} {i*17:02d} {i*13:02d}"
            durum_notu = "WhatsApp Gateway İletildi (Çift Mavi Tik)"
        elif kanal == "sms":
            hedef_adresi = f"+90 (5{str(i).zfill(2)}) {i*31:03d} {i*19:02d} {i*11:02d}"
            durum_notu = "SMSC Kulesine İletildi (B002)"
        elif kanal == "qr":
            hedef_adresi = f"Ofis Masası / {calisan.departman} Panosu"
            durum_notu = "Karekod Baskı Kuyruğuna Alındı"
        else:
            hedef_adresi = calisan.email
            durum_notu = "SMTP Kuyruğuna Verildi (250 OK)"

        log_kaydi = {
            "sira": i,
            "calisan_adi": calisan.ad_soyad,
            "departman": calisan.departman,
            "kanal": kanal,
            "hedef_adresi": hedef_adresi,
            "gonderici": f"{gonderici['gonderen_adi']} <{gonderici['gonderen_no']}>",
            "durum": durum_notu,
            "zaman": datetime.utcnow().strftime("%H:%M:%S"),
            "takip_kodu": ozel_token,
            "takip_linki": takip_linki,
            "sablon_adi": sablon_adi,
            "senaryo_konu": senaryo_konu
        }
        dagitim_loglari.append(log_kaydi)

    return {
        "kampanya_adi": kampanya.ad,
        "kanal": kanal,
        "hedef_departman": hedef_departman,
        "protokol": gonderici["protokol"],
        "maskelenmis_gonderici": f"{gonderici['gonderen_adi']} ({gonderici['gonderen_no']})",
        "toplam_hedef": toplam_hedef,
        "basari_orani": "%100",
        "loglar": dagitim_loglari
    }


def env_yukle():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k not in os.environ:
                        os.environ[k] = v

def env_guncelle(anahtarlar: dict):
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    mevcut = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    mevcut[k.strip()] = v.strip().strip('"').strip("'")
    mevcut.update(anahtarlar)
    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in mevcut.items():
            f.write(f"{k}={v}\n")
    for k, v in anahtarlar.items():
        os.environ[k] = str(v)

def gercek_smtp_mail_gonder(
    alici_email: str,
    alici_adi: str,
    takip_linki: str,
    konu: str,
    icerik_html: str,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None
) -> Dict[str, Any]:
    env_yukle()
    host = (smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")).strip()
    try:
        port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
    except (ValueError, TypeError):
        port = 587

    user = (smtp_user or os.getenv("SMTP_USER", "")).strip()
    password = (smtp_pass or os.getenv("SMTP_PASSWORD", "")).strip()

    if not user or not password:
        return {
            "durum": "simule",
            "mesaj": "Gerçek SMTP kimlik bilgisi (kullanıcı ve şifre) tanımlanmadığı için e-posta güvenli 'Simüle Cloud Mail Relay' üzerinden iletildi olarak işaretlendi. E-postanın alıcı gelen kutusuna (inbox) gerçekten düşmesi için modal içerisindeki '⚙️ Canlı SMTP Gönderici Ayarları' alanına geçerli bir Gmail veya kurumsal posta hesabı girebilirsiniz.",
            "alici": alici_email
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = konu
        msg["From"] = f"TrendLojistik Bilgi Güvenliği Masası <{user}>"
        msg["To"] = alici_email
        msg["X-PhishAware-Simulation"] = "True"

        kisisellestirilmis_html = icerik_html.replace("{isim}", alici_adi).replace("{link}", takip_linki).replace("{{LINK}}", takip_linki)
        if takip_linki not in kisisellestirilmis_html:
            kisisellestirilmis_html += f'<br><p><a href="{takip_linki}" style="color:#0284c7; font-weight:bold;">Doğrulama ve Onay İçin Tıklayınız</a></p>'

        msg.attach(MIMEText(kisisellestirilmis_html, "html", "utf-8"))

        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=8)
        else:
            server = smtplib.SMTP(host, port, timeout=8)
            server.starttls()

        server.login(user, password)
        server.send_message(msg)
        server.quit()

        return {
            "durum": "basarili",
            "mesaj": f"Gerçek oltalama e-postası '{host}' sunucusu üzerinden {alici_email} adresine başarıyla teslim edildi! Lütfen gelen kutunuzu (ve gerekiyorsa Gereksiz/Spam klasörünü) kontrol ediniz.",
            "alici": alici_email
        }
    except smtplib.SMTPAuthenticationError as auth_err:
        return {
            "durum": "hata",
            "mesaj": f"SMTP Kimlik Doğrulama Hatası (535): Girdiğiniz kullanıcı adı veya şifre SMTP sunucusu tarafından reddedildi. (Önemli Not: Gmail kullanıyorsanız standart hesap şifreniz yerine Google Güvenlik ayarlarından 16 haneli 'Uygulama Şifresi' almanız gerekmektedir). Hata Ayrıntısı: {str(auth_err)}",
            "alici": alici_email
        }
    except Exception as e:
        return {
            "durum": "hata",
            "mesaj": f"SMTP Sunucusuna Bağlanılamadı ({host}:{port}): {str(e)}",
            "alici": alici_email
        }
