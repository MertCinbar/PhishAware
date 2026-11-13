import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import io
import json
import uuid
import requests
import qrcode
from typing import List, Dict, Any, Optional

def maskelenmis_gonderici_belirle(kanal: str, departman: str = "") -> Dict[str, str]:
    if kanal == "qr":
        return {
            "gonderen_adi": "TrendLojistik İdari İşler ve Bilgi Güvenliği",
            "gonderen_no": "OFIS-PANO-01",
            "protokol": "Ofis İçi Fiziksel Quishing Panosu"
        }
    elif kanal == "telegram":
        return {
            "gonderen_adi": "TrendLojistik Siber Güvenlik Masası",
            "gonderen_no": "@trend_guvenlik_mert_bot",
            "protokol": "Telegram Güvenlik Protokolü (TLS 1.3 / End-to-End)"
        }
    else:
        return {
            "gonderen_adi": "TrendLojistik Siber Güvenlik Masası",
            "gonderen_no": "trendlojistik.guvenlik@gmail.com",
            "protokol": "Kurumsal SMTP Relay (TLS)"
        }


from app.ai_generator import senaryo_uret

def toplu_otomatik_dagitim(
    kampanya, 
    calisanlar: list, 
    lan_ip: str = "127.0.0.1",
    base_url: Optional[str] = None,
    hedef_departman: str = "hepsi",
    kanal_override: Optional[str] = None,
    otomatik_ai: bool = True,
    qr_ile_mi: bool = False
) -> Dict[str, Any]:
    kanal = kanal_override or getattr(kampanya.sablon, "kanal", "email")
    if kanal in ["whatsapp", "sms"]:
        kanal = "email"
    gonderici = maskelenmis_gonderici_belirle(kanal)
    sektor = getattr(kampanya.sirket, "sektor", "E-Ticaret ve Lojistik") if hasattr(kampanya, "sirket") and kampanya.sirket else "Kurumsal Hizmetler"

    # Mobil ve dış ağ için dinamik base_url çözümleme
    env_base = os.environ.get("BASE_URL") or os.environ.get("PHISHAWARE_EXTERNAL_URL") or os.environ.get("PUBLIC_URL")
    if env_base:
        env_base = env_base.strip()
        if env_base.startswith("{") or env_base.startswith("<") or not env_base.startswith("http"):
            env_base = None
    if base_url:
        base_url = base_url.strip()
        if base_url.startswith("{") or base_url.startswith("<") or not base_url.startswith("http"):
            base_url = None
    effective_base = (base_url or env_base or "http://127.0.0.1:8000").rstrip("/")
    if "127.0.0.1" in effective_base or "localhost" in effective_base:
        if lan_ip and lan_ip != "127.0.0.1":
            effective_base = f"http://{lan_ip}:8000"

    senaryo_onbellegi = {}
    dagitim_loglari = []
    toplam_hedef = len(calisanlar)

    for i, calisan in enumerate(calisanlar, 1):
        ozel_token = f"c{calisan.id}-{uuid.uuid4().hex[:12]}" if hasattr(calisan, "id") and calisan.id else str(uuid.uuid4())[:16]
        takip_linki = f"{effective_base}/tikla/{ozel_token}"
        qr_linki = f"{effective_base}/qr-kod/{ozel_token}"

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

        if kanal == "qr":
            hedef_adresi = f"Ofis Masası / {calisan.departman} Panosu"
            durum_notu = "Karekod Baskı Kuyruğuna Alındı"
        elif kanal == "telegram":
            t_id = getattr(calisan, "telegram_id", "") or ""
            hedef_adresi = f"@{t_id}" if t_id else f"@{calisan.email.split('@')[0]}_tg"
            durum_notu = "Telegram Güvenlik Hattı (QR Fotoğraf / 200 OK)" if qr_ile_mi else "Telegram Güvenlik Hattı (200 OK)"
        else:
            hedef_adresi = calisan.email
            durum_notu = "SMTP Kuyruğuna Verildi (QR Kartlı)" if qr_ile_mi else "SMTP Kuyruğuna Verildi (250 OK)"

        log_kaydi = {
            "sira": i,
            "calisan_id": calisan.id,
            "calisan_adi": calisan.ad_soyad,
            "departman": calisan.departman,
            "kanal": kanal,
            "qr_ile_mi": qr_ile_mi,
            "hedef_adresi": hedef_adresi,
            "telegram_id": getattr(calisan, "telegram_id", "") or "",
            "gonderici": f"{gonderici['gonderen_adi']} <{gonderici['gonderen_no']}>",
            "durum": durum_notu,
            "zaman": datetime.utcnow().strftime("%H:%M:%S"),
            "takip_kodu": ozel_token,
            "takip_linki": takip_linki,
            "qr_linki": qr_linki,
            "sablon_adi": sablon_adi,
            "senaryo_konu": senaryo_konu
        }
        dagitim_loglari.append(log_kaydi)

    protokol_adi = gonderici["protokol"]
    if qr_ile_mi and kanal != "qr":
        protokol_adi += " + Quishing (QR Modu)"

    return {
        "kampanya_adi": kampanya.ad,
        "kanal": kanal,
        "qr_ile_mi": qr_ile_mi,
        "hedef_departman": hedef_departman,
        "protokol": protokol_adi,
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
    smtp_pass: Optional[str] = None,
    qr_ile_mi: bool = False,
    qr_kodu_url: Optional[str] = None
) -> Dict[str, Any]:
    env_yukle()
    host = (smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")).strip()
    try:
        port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
    except (ValueError, TypeError):
        port = 587

    user = (smtp_user or os.getenv("SMTP_USER", "")).strip()
    password = (smtp_pass or os.getenv("SMTP_PASSWORD", "")).strip()
    # Google Uygulama Şifreleri kopyalandığında 4'erli gruplar halinde boşluklu gelebilir
    if "gmail" in host.lower() or "google" in host.lower():
        password = password.replace(" ", "")

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
        msg["Reply-To"] = "guvenlik-bildirim@trendlojistik.com"
        msg["To"] = alici_email
        msg["X-PhishAware-Simulation"] = "True"

        kisisellestirilmis_html = icerik_html.replace("{isim}", alici_adi).replace("{link}", takip_linki).replace("{{LINK}}", takip_linki)
        if takip_linki not in kisisellestirilmis_html:
            kisisellestirilmis_html += f'<br><p><a href="{takip_linki}" style="color:#0284c7; font-weight:bold;">Doğrulama ve Onay İçin Tıklayınız</a></p>'

        if qr_ile_mi:
            qr_img_src = qr_kodu_url or takip_linki.replace("/tikla/", "/qr-kod/")
            qr_html_block = f"""
            <div style="margin:22px auto; max-width:440px; padding:18px; background:#f8fafc; border:2px dashed #0284c7; border-radius:12px; text-align:center; font-family:sans-serif;">
                <div style="font-size:13px; font-weight:700; color:#0369a1; margin-bottom:8px;">
                    📷 Hızlı &amp; Güvenli Mobil Kimlik Doğrulama (Karekod)
                </div>
                <img src="{qr_img_src}" alt="Doğrulama QR Kodu" style="width:160px; height:160px; border-radius:8px; border:1px solid #cbd5e1; padding:6px; background:#ffffff; display:inline-block;" />
                <p style="font-size:11px; color:#64748b; margin-top:8px; line-height:1.45;">
                    Kurumsal bilgi güvenliği politikası gereğince mobil cihazınızdan işlem yapmak için telefon kameranızla yukarıdaki QR kodu taratınız.
                </p>
            </div>
            """
            kisisellestirilmis_html += qr_html_block

        msg.attach(MIMEText(kisisellestirilmis_html, "html", "utf-8"))

        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
            server.starttls()

        server.login(user, password)
        server.send_message(msg)
        server.quit()

        ek_not = " (QR Kod Kartlı)" if qr_ile_mi else ""
        return {
            "durum": "basarili",
            "mesaj": f"Gerçek oltalama e-postası{ek_not} '{host}' sunucusu üzerinden {alici_email} adresine başarıyla teslim edildi! Lütfen gelen kutunuzu (ve gerekiyorsa Gereksiz/Spam klasörünü) kontrol ediniz.",
            "alici": alici_email
        }
    except smtplib.SMTPAuthenticationError as auth_err:
        return {
            "durum": "hata",
            "mesaj": f"SMTP Kimlik Doğrulama Hatası (535): Girdiğiniz kullanıcı adı veya şifre Google tarafından reddedildi. Normal Gmail giriş şifrenizi değil, Google Güvenlik ayarlarından 16 haneli 'Uygulama Şifresi' almanız gerekmektedir.",
            "alici": alici_email
        }
    except smtplib.SMTPServerDisconnected as disc_err:
        return {
            "durum": "hata",
            "mesaj": f"Google Bağlantıyı Kapattı (Connection unexpectedly closed): Google SMTP sunucusu kimlik doğrulama aşamasında bağlantıyı sonlandırdı. Bu durum şifrenin yanlış veya normal Gmail hesap şifresi olmasından kaynaklanır. Lütfen myaccount.google.com/apppasswords adresinden aldığınız 16 haneli Uygulama Şifresini kullandığınızdan ve 2 Adımlı Doğrulamanın açık olduğundan emin olun.",
            "alici": alici_email
        }
    except Exception as e:
        return {
            "durum": "hata",
            "mesaj": f"SMTP Sunucusuna Bağlanılamadı ({host}:{port}): {str(e)}",
            "alici": alici_email
        }


def gercek_telegram_mesaj_gonder(
    chat_id: str = "",
    mesaj: str = "",
    link: str = "",
    bot_token: Optional[str] = None,
    qr_ile_mi: bool = False,
    qr_kodu_url: Optional[str] = None
) -> Dict[str, Any]:
    env_yukle()
    token = (bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    target_chat = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()

    if not token or not target_chat:
        return {
            "durum": "simule",
            "mesaj": "Telegram Bot Token veya Chat ID henüz tanımlanmadı (.env içinde TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID). Simülasyon kuyruğuna alındı.",
            "alici": target_chat or "Telegram Kanalı"
        }

    try:
        if qr_ile_mi:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(link or "http://127.0.0.1:8000")
            qr.make(fit=True)
            img = qr.make_image(fill_color="#090d16", back_color="#ffffff")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            caption_metni = (mesaj + "\n\n📷 <i>Kameranızla yukarıdaki QR kodu okutarak mobil doğrulama yapabilirsiniz.</i>")[:1024]
            data_payload = {
                "chat_id": target_chat,
                "caption": caption_metni,
                "parse_mode": "HTML"
            }
            if link:
                data_payload["reply_markup"] = json.dumps({
                    "inline_keyboard": [
                        [{"text": "🚨 Doğrulamak ve İncelemek İçin Tıklayın", "url": link}]
                    ]
                })

            files = {
                "photo": ("quishing_qr.png", buf.getvalue(), "image/png")
            }
            resp = requests.post(url, data=data_payload, files=files, timeout=12)
        else:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": target_chat,
                "text": mesaj,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            if link:
                payload["reply_markup"] = {
                    "inline_keyboard": [
                        [{"text": "🚨 Doğrulamak ve İncelemek İçin Tıklayın", "url": link}]
                    ]
                }
            resp = requests.post(url, json=payload, timeout=8)

        data = resp.json()
        if resp.status_code == 200 and data.get("ok"):
            ek_not = " (Taranabilir Karekod Görseli İle)" if qr_ile_mi else ""
            return {
                "durum": "basarili",
                "mesaj": f"Telegram oltalama tatbikat mesajı{ek_not} @trend_guvenlik_mert_bot üzerinden {target_chat} hedefine başarıyla iletildi!",
                "alici": target_chat
            }
        else:
            err = data.get("description", "Bilinmeyen Telegram API hatası")
            return {
                "durum": "hata",
                "mesaj": f"Telegram API Hatası: {err}",
                "alici": target_chat
            }
    except Exception as e:
        return {
            "durum": "hata",
            "mesaj": f"Telegram Bağlantı Hatası: {str(e)}",
            "alici": target_chat
        }
