import os
import json
import re
import requests

def _api_anahtarini_al():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        break
    return key

def senaryo_uret(sektor: str, departman: str, zorluk: str = "orta", kanal: str = "email") -> dict:
    api_key = _api_anahtarini_al()

    kanal_aciklama = {
        "email": "Kurumsal E-posta formatında profesyonel oltalama e-postası",
        "sms": "160 karakteri geçmeyen, acil işlem gerektiren sahte kurumsal SMS (Smishing) metni",
        "whatsapp": "Kurumsal WhatsApp onay mesajı (emojiler, resmi şirket bildirimi ve ek doğrulama bağlantısı içeren)",
        "qr": "Ofis veya şirket içi panoya asılacak merak uyandırıcı QR Kod Oltalama (Quishing) afiş metni"
    }.get(kanal, "Kurumsal E-posta")

    prompt = f"""
    Sen siber güvenlik farkındalık tatbikatları için çok kanallı (Omnichannel) oltalama simülasyon şablonu hazırlayan uzman bir siber güvenlik analistisin.

    HEDEF BİLGİLERİ:
    - Şirket Sektörü: {sektor}
    - Hedef Departman: {departman}
    - İletim Kanalı: {kanal.upper()} ({kanal_aciklama})
    - Zorluk Seviyesi: {zorluk}

    GÖREV:
    Bu sektör ve departmandaki bir çalışanın aciliyet, merak veya endişe nedeniyle tıklayabileceği, {kanal.upper()} kanalına uygun gerçekçi bir sahte senaryo yaz.
    ÖNEMLİ KURAL: Tıklanacak düğme, link veya bağlantı href adresine TAM OLARAK '{{{{LINK}}}}' yazmalısın.

    Lütfen yanıtını SADECE geçerli bir JSON formatında ver (başka hiçbir açıklama yazma):
    {{
        "baslik": "Kısa Şablon Başlığı",
        "konu": "Mesaj Konusu veya SMS/WhatsApp Başlığı",
        "gonderen_adi": "Görünen Gönderici Adı (Örn: B002-IK_BILDIRIM veya Kurumsal Destek)",
        "icerik_html": "Mesaj gövdesi (Kanalına göre HTML/metin)... <a href='{{{{LINK}}}}'>Tıklayınız</a>",
        "ipuclari": [
            "Çalışanın şüphelenmesi gereken 1. ipucu",
            "Çalışanın şüphelenmesi gereken 2. ipucu",
            "Çalışanın şüphelenmesi gereken 3. ipucu"
        ]
    }}
    """

    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "responseMimeType": "application/json"
                }
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                clean_json = raw_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                return json.loads(clean_json.strip())
        except Exception as e:
            print(f"[Yapay Zeka API Uyarısı]: Gemini API hatası ({e}), yerel yedek motor devrede.")

    return _yerel_yedek_senaryo(sektor, departman, kanal)


def risk_analizi_yorumu(departman_verileri: list) -> dict:
    api_key = _api_anahtarini_al()

    veri_metni = "\n".join([
        f"- {d['departman']}: Toplam {d['toplam']} çalışan, {d['tiklayan']} kişi tuzağa düştü (Tıklama Oranı: %{d['oran']})"
        for d in departman_verileri
    ])

    prompt = f"""
    Sen kıdemli bir Kurumsal Siber Güvenlik Danışmanısın (CISO Advisor).
    Aşağıda bir şirketin son oltalama simülasyon tatbikatının departman bazlı sonuçları yer alıyor:

    {veri_metni}

    GÖREV:
    Yönetim kurulu için kısa, çarpıcı ve profesyonel bir siber risk özeti çıkar.
    Lütfen yanıtını SADECE geçerli bir JSON olarak ver:
    {{
        "en_riskli_departman": "En çok tuzağa düşen departman adı",
        "genel_degerlendirme": "2-3 cümlelik kurumsal durum özeti",
        "aksiyon_onerileri": [
            "Yönetimin atması gereken 1. somut adım",
            "Yönetimin atması gereken 2. somut adım",
            "Yönetimin atması gereken 3. somut adım"
        ]
    }}
    """

    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.6,
                    "responseMimeType": "application/json"
                }
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                clean_json = raw_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                return json.loads(clean_json.strip())
        except Exception as e:
            print(f"[AI Risk Analizi Uyarısı]: Gemini API çağrısı sırasında hata ({e}), yerel analiz devrede.")

    en_riskli = max(departman_verileri, key=lambda x: x["oran"]) if departman_verileri else {"departman": "Belirsiz", "oran": 0}
    return {
        "en_riskli_departman": en_riskli["departman"],
        "genel_degerlendirme": f"Son simülasyon verilerine göre en yüksek zaafiyet %{en_riskli['oran']} tıklama oranı ile {en_riskli['departman']} biriminde gözlemlenmiştir. Finansal ve operasyonel etki riski yüksektir.",
        "aksiyon_onerileri": [
            f"{en_riskli['departman']} personeline özel 15 dakikalık zorunlu 'Sosyal Mühendislik ve Fatura Doğrulama' mikro eğitimi atanmalı.",
            "Tüm departmanlar için 14 gün içerisinde farklı bir yem şablonuyla habersiz ikinci bir doğrulama tatbikatı yapılmalı.",
            "E-posta ağ geçidinde (Gateway) harici bağlantılar için görsel uyarı bayrakları (External Email Banner) zorunlu kılınmalı."
        ]
    }


def _yerel_yedek_senaryo(sektor: str, departman: str, kanal: str = "email") -> dict:
    dep_lower = departman.lower()

    if any(k in dep_lower for k in ["bilgi işlem", "bilgi islem", "it", "yazılım", "yazilim", "sistem", "network", "güvenlik", "guvenlik"]):
        if kanal == "whatsapp":
            return {
                "baslik": "IT - Kritik VPN & SSH Kimlik Doğrulama",
                "konu": "💬 Kurumsal IT Destek: SSH Anahtar & VPN Doğrulaması",
                "gonderen_adi": "TrendLojistik IT Güvenlik Ekibi",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 Kurumsal IT Güvenlik Masası</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sn. {departman} Uzmanı,</strong></p>
                        <p style="margin:0 0 10px 0;">Altyapı sunucularında SSH anahtar rotasyonu ve VPN sertifika güncellemesi başlatılmıştır. 2 saat içinde onay vermeyen hesaplar güvenlik duvarı tarafından kısıtlanacaktır. 💻</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">Erişimi Doğrula ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">10:42 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "IT yöneticileri SSH anahtar doğrulamasını asla WhatsApp linki üzerinden yapmaz.",
                    "Sertifika ve anahtar yönetimi iç ağ yönetim konsolundan yürütülmelidir.",
                    "Bağlantı adresi şirket alan adı dışındadır."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": "IT - Sunucu Güvenlik Yaması & 2FA Askıya Alma",
                "konu": "📱 B002 - IT_DESTEK",
                "gonderen_adi": "B002-IT_SECURITY",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-IT_SECURITY</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. IT Personeli, kritik güvenlik yamasi nedeniyle root/SSH erisim yetkiniz askiya alinmistir. 15 dk icinde aktive edin: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "SMS üzerinden root veya SSH yetkilendirme linki paylaşılmaz.",
                    "15 dakikalık aciliyet baskısı sosyal mühendislik göstergesidir.",
                    "URL şirket sistemleri ile eşleşmemektedir."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "IT - Sunucu Odası & WPA3 Güvenlik Sertifikası",
                "konu": "🔳 Sunucu Odası Wi-Fi WPA3 Sertifikası",
                "gonderen_adi": "Bilgi Teknolojileri Altyapı Direktörlüğü",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">🔐 IT Altyapı & WPA3 Kurumsal Wi-Fi Sertifikası</h3>
                    <p style="font-size:13px; color:#475569;">Sunucu odası ve IT laboratuvarı yeni 802.1X kurumsal ağ profiline bağlanmak için QR kodu okutun:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Kurumsal 802.1X sertifikaları MDM (Mobile Device Management) üzerinden dağıtılır.",
                    "Fiziksel panolardaki QR kodlar tahrif edilmiş olabilir."
                ]
            }
        else:
            return {
                "baslik": "Kritik Altyapı Güvenlik Yaması & SSH Doğrulama",
                "konu": "[ACİL-IT] Kritik Güvenlik Açığı (CVE-2026-8812) Yaması & SSH Yenileme",
                "gonderen_adi": "Kurumsal IT Güvenlik Masası",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #dc2626; margin-top:0;">⚠️ Kritik Güvenlik Açığı & SSH Erişim Doğrulaması</h3>
                    <p>Sayın {departman} Uzmanı,</p>
                    <p>Altyapı sunucularında tespit edilen <strong>CVE-2026-8812</strong> kodlu kritik zero-day zafiyeti nedeniyle tüm IT personeli SSH anahtarlarını ve VPN sertifikalarını 2 saat içinde yenilemek zorundadır.</p>
                    <p>Doğrulanmayan hesaplar otomatik olarak kilitlenecektir.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            SSH & VPN Anahtarını Doğrula
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Zafiyet yamaları ve SSH anahtarları e-posta bağlantısı üzerinden yenilenmez.",
                    "2 saatlik panik baskısı ile çalışan hata yapmaya yönlendirilir.",
                    "Gönderici domaini resmi şirket e-posta ağ geçidi ile eşleşmemektedir."
                ]
            }

    elif any(k in dep_lower for k in ["ik", "insan kaynakları", "insan kaynaklari", "bordro", "özlük", "ozluk"]):
        if kanal == "whatsapp":
            return {
                "baslik": "İK - 2026 Bordro & Avans Onay Dosyası",
                "konu": "💬 Kurumsal İK: 2026 Bordro & Avans Onayı",
                "gonderen_adi": "TrendLojistik İK Masası",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 İnsan Kaynakları Portalı</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sayın {departman} Çalışanı,</strong></p>
                        <p style="margin:0 0 10px 0;">2026 yılı performans primi, yan haklar ve SGK matrah dosyanız hazırlanmıştır. İmzalı bordronuzu incelemek için dokunun: 📄</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">Bordroyu İncele ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">09:15 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Şirket İK departmanı bordroları WhatsApp üzerinden link ile dağıtmaz.",
                    "Resmi bordrolar şirket intranetindeki ERP/İK portalından görüntülenir."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": "İK - Yıllık İzin & SGK Devir Bildirimi",
                "konu": "📱 B002 - IK_BILDIRIM",
                "gonderen_adi": "B002-IK_PORTAL",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-IK_PORTAL</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. Personel, 2026 yillik izin devir bakiyeniz ve performans prim listeniz hazirlandi. Onaylamak icin: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "Bilinmeyen SMS başlıklarından gelen izin ve prim linklerine tıklanmamalıdır.",
                    "İzin onayları şirket iç sistemi üzerinden kontrol edilmelidir."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "İK - 2026 Personel Yan Haklar & Yemek Portalı",
                "konu": "🔳 Personel Sosyal Haklar Afişi",
                "gonderen_adi": "İnsan Kaynakları ve Sosyal Hizmetler",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">👥 2026 Personel Yan Haklar & Yemekhane İndirim Portalı</h3>
                    <p style="font-size:13px; color:#475569;">Yeni dönem özel sağlık sigortası ve yemek kartı ek bakiyenizi etkinleştirmek için kameranızla QR kodu okutun:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Yemek kartı veya sigorta işlemleri fiziksel panodaki QR kodla değil doğrudan İK portalıyla yapılır.",
                    "QR kodun açtığı domain sahte olabilir."
                ]
            }
        else:
            return {
                "baslik": "2026 Yan Haklar, SGK & İzin Portalı Güncellemesi",
                "konu": "2026-2027 Dönemi Kalan İzin Günleriniz ve Prim Bildirimi",
                "gonderen_adi": "İnsan Kaynakları Portalı",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #1e3a8a; margin-top:0;">Özlük Hakları ve İzin Güncellemesi</h3>
                    <p>Değerli Çalışanımız,</p>
                    <p>2026 yılı son çeyrek öncesi kullanılmayan yıllık izin haklarınız ve performans prim onay listeniz güncellenmiştir.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            İzin ve Prim Listemi Onayla
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Prim ve izin konuları çalışanların en hızlı tıkladığı sosyal mühendislik yemidir.",
                    "Şirket içi İK portalları harici web adreslerine yönlendirme yapmaz."
                ]
            }

    elif any(k in dep_lower for k in ["muhasebe", "finans", "mali"]):
        if kanal == "whatsapp":
            return {
                "baslik": "Finans - 42.850 TL Fatura & IBAN Mutabakatı",
                "konu": "💬 Finans Masası: Fatura Mutabakat Uyuşmazlığı",
                "gonderen_adi": "TrendLojistik Finans ve Gelir Masası",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 Muhasebe & Mutabakat Bildirim Hattı</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sayın Finans Yetkilisi,</strong></p>
                        <p style="margin:0 0 10px 0;">Adınıza kayıtlı 42.850 TL tutarlı e-arşiv faturada vergi dairesi ve IBAN uyuşmazlığı tespit edilmiştir. İade ve cezai işlem öncesi faturayı düzeltin: 📄</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">Faturayı İncele ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">11:20 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "WhatsApp üzerinden fatura veya IBAN mutabakatı yapılmaz.",
                    "Vergi dairesi bildirimleri Gelir İdaresi Başkanlığı resmi portalından kontrol edilir."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": "Finans - E-Fatura Askıya Alma Uyarısı",
                "konu": "📱 B002 - FINANS_ONAY",
                "gonderen_adi": "B002-FINANS_ONAY",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-FINANS_ONAY</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. Muhasebe Yetkilisi, 42.850 TL tutarli e-arsiv faturaniz bloke edilmistir. Cezai islem uygulanmamasi icin dogrulayin: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "SMS ile gelen fatura uyuşmazlığı ve bloke tehditlerine şüpheyle yaklaşılmalıdır.",
                    "Maliye veya banka işlemleri SMS linkiyle yürütülmez."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "Finans - E-Fatura & Masraf Onay Kiosku",
                "konu": "🔳 Fatura & Masraf Giriş Kiosku",
                "gonderen_adi": "Mali İşler Direktörlüğü",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">💰 Hızlı E-Fatura & Kurumsal Masraf Giriş Kiosku</h3>
                    <p style="font-size:13px; color:#475569;">Şirket kredi kartı harcamaları ve masraf fişlerinizi hızlıca sisteme aktarmak için QR kodu okutun:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Şirket masraf ve fatura girişleri QR kod ile değil şirket ERP'si üzerinden yapılmalıdır."
                ]
            }
        else:
            return {
                "baslik": "E-Arşiv Fatura İptal İhbarnamesi & IBAN Doğrulama",
                "konu": "[ACİL] Adınıza Düzenlenen 42.850 TL Tutarlı E-Arşiv Fatura Askıya Alındı",
                "gonderen_adi": "Gelir & Fatura Kontrol Merkezi",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #b91c1c; margin-top:0;">Fatura Mutabakat Uyarısı</h3>
                    <p>Sayın {departman} Yetkilisi,</p>
                    <p>Şirketiniz adına <strong>{sektor}</strong> operasyonları kapsamında kesilen <strong>#FAT-2026-981</strong> numaralı e-faturada IBAN ve vergi no uyumsuzluğu tespit edilmiştir.</p>
                    <p>Cezai işlem uygulanmaması için 2 saat içerisinde portal üzerinden bilgileri doğrulamanız gerekmektedir.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Faturayı İncele ve Düzelt
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "2 saatlik aciliyet dili kullanıcıyı panikletmek amacıyla kurgulanmıştır.",
                    "E-fatura iptalleri Gelir İdaresi sistemi dışındaki harici linklerden yapılmaz."
                ]
            }

    elif any(k in dep_lower for k in ["satış", "satis", "pazarlama", "marketing"]):
        if kanal == "whatsapp":
            return {
                "baslik": "Satış - Kurumsal Müşteri Teklifi & Q4 Prim Tablosu",
                "konu": "💬 Satış Direktörlüğü: Yeni Müşteri Teklifi & Prim Listesi",
                "gonderen_adi": "TrendLojistik Satış Yönetimi",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 Satış & Pazarlama Operasyon Masası</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sn. Satış Temsilcisi,</strong></p>
                        <p style="margin:0 0 10px 0;">Yeni bir kurumsal müşteri için hazırlanan 1.250.000 TL bütçeli teklif şartnamesi ve onaylanan Q4 satış primi tablonuz sisteme yüklendi. İncelemek için dokunun: 📈</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">Teklif Dosyasını Aç ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">14:30 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Müşteri teklifleri ve prim tabloları şirket CRM sistemi üzerinden takip edilmelidir.",
                    "WhatsApp üzerinden gelen bilinmeyen dosya linklerine tıklanmamalıdır."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": "Satış - Q4 Hedef Prim Onaylandı",
                "konu": "📱 B002 - SATIS_BILDIRIM",
                "gonderen_adi": "B002-SATIS_BILDIRIM",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-SATIS_BILDIRIM</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. Satis Temsilcisi, Q4 hedef prim tutariniz onaylanmistir. Hesap detaylarinizi onaylamak icin linke dokunun: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "Satış kotaları ve prim bildirimleri SMS bağlantıları ile dağıtılmaz."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "Satış - CRM & Müşteri Ziyaret Portalı",
                "konu": "🔳 CRM Müşteri Ziyaret Portalı",
                "gonderen_adi": "Satış ve Müşteri İlişkileri Masası",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">📊 Yeni Satış & CRM Mobil Portalı</h3>
                    <p style="font-size:13px; color:#475569;">Müşteri ziyaretlerinizi ve teklif girişlerinizi hızlandırmak için yeni mobil CRM uygulamasını QR kod ile indirin:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Kurumsal mobil uygulamalar şirket MDM veya resmi uygulama mağazalarından kurulur."
                ]
            }
        else:
            return {
                "baslik": "Yeni İhale Şartnamesi & Q4 Prim Tablosu Güncellemesi",
                "konu": "[YENİ TEKLİF] 1.250.000 TL Bütçeli Kurumsal İhale Şartnamesi Ektedir",
                "gonderen_adi": "Kurumsal Satış ve İhale Masası",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #0284c7; margin-top:0;">Yeni İhale ve Prim Güncellemesi</h3>
                    <p>Değerli {departman} Personelimiz,</p>
                    <p>Şirketimize iletilen yeni kurumsal ihale şartnamesi ve 2026 yılı Q4 satış komisyon tablonuz ekte yer almaktadır. Teklifi sunmadan önce onaylamanız gerekmektedir.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            İhale Şartnamesini Görüntüle
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Yüksek meblağlı teklifler merak uyandırmak amacıyla sıkça kullanılır.",
                    "Dosya indirme linklerinin güvenilirliği şirket güvenlik standartlarıyla teyit edilmelidir."
                ]
            }

    elif any(k in dep_lower for k in ["operasyon", "tedarik", "lojistik", "depo", "sevkiyat"]):
        if kanal == "whatsapp":
            return {
                "baslik": "Operasyon - Sevkiyat İrsaliyesi & Yakıt Kartı",
                "konu": "💬 Saha Lojistik: Sevkiyat İrsaliye & Araç Onayı",
                "gonderen_adi": "TrendLojistik Filo ve Operasyon",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 Saha & Lojistik Koordinasyon Masası</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sn. Operasyon Sorumlusu,</strong></p>
                        <p style="margin:0 0 10px 0;">Araç filosu yakıt kartı limit artırımı ve bekleyen sevkiyat irsaliyeniz onay beklemektedir. İncelemek için dokunun: 🚚</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">İrsaliyeyi Onayla ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">08:45 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Saha operasyonlarında irsaliye onayları şirket içi ERP terminalinden verilir."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": "Operasyon - Yakıt Kartı Limit Onayı",
                "konu": "📱 B002 - FILO_LOJISTIK",
                "gonderen_adi": "B002-FILO_LOJISTIK",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-FILO_LOJISTIK</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. Yetkili, filo tasit yakit kartiniz limit asimi nedeniyle kilitlenmistir. Kilidi acmak icin linke tiklayin: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "Yakıt kartı blokajları SMS üzerinden kimlik bilgisi talep etmez."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "Operasyon - Depo & Sevkiyat Kabul Panosu",
                "konu": "🔳 Depo Sevkiyat Panosu",
                "gonderen_adi": "Depo ve Lojistik Yönetimi",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">📦 Hızlı Kargo & Sevkiyat Mal Kabul QR Kodu</h3>
                    <p style="font-size:13px; color:#475569;">Gelen palet ve kargoları el terminali olmadan doğrudan telefonunuzla teslim almak için QR kodu taratın:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Depo mal kabul işlemleri şirket lisanslı el terminalleri ile barkod okutularak yapılır."
                ]
            }
        else:
            return {
                "baslik": "Sevkiyat İrsaliyesi Onayı & Taşıt Yakıt Kartı Limit Bildirimi",
                "konu": "[ACİL] Sevkiyat İrsaliye Uyuşmazlığı & Filo Yakıt Kartı Onayı",
                "gonderen_adi": "Filo ve Tedarik Zinciri Masası",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #d97706; margin-top:0;">Sevkiyat & İrsaliye Bildirimi</h3>
                    <p>Sayın {departman} Yöneticisi,</p>
                    <p>2026 üçüncü çeyrek tedarikçi teslimat irsaliyesinde barkod uyuşmazlığı tespit edilmiştir. Dağıtımın aksamaması için irsaliyeyi doğrulayınız.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #d97706; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            İrsaliyeyi İncele ve Onayla
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Operasyonel aksama korkusu çalışanların linke tıklamasına sebep olan psikolojik bir taktiktir."
                ]
            }

    elif any(k in dep_lower for k in ["hukuk", "uyum", "avukat", "legal", "kvkk"]):
        if kanal == "whatsapp":
            return {
                "baslik": "Hukuk - Noter İhtarnamesi & Gizlilik Protokolü",
                "konu": "💬 Hukuk Müşavirliği: Noter İhtarnamesi Tebliği",
                "gonderen_adi": "TrendLojistik Hukuk ve Müşavirlik",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 Hukuk & Mevzuat Müşavirliği</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sayın Hukuk Müşaviri,</strong></p>
                        <p style="margin:0 0 10px 0;">Şirketimiz aleyhine 1. Noterlik üzerinden iletilen gizli ihtarname ve KVKK inceleme tebligatı sisteme yüklenmiştir. Evrakı görüntülemek için dokunun: ⚖️</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">Tebligatı İncele ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">16:05 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Resmi noter tebligatları WhatsApp üzerinden dosya linki olarak iletilmez, UETS üzerinden tebliğ edilir."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": "Hukuk - Resmi Dava Dosyası Tebligatı",
                "konu": "📱 B002 - HUKUK_UYARISI",
                "gonderen_adi": "B002-HUKUK_UYARISI",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-HUKUK_UYARISI</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. Hukuk Yetkilisi, sirket adina kayitli icra takip dosyasi sisteme eklenmistir. 24 saat icinde itiraz linki: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "İcra ve mahkeme takipleri Ulusal Yargı Ağı Bilişim Sistemi (UYAP) üzerinden incelenir."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "Hukuk - KVKK Uyum & Gizlilik Panosu",
                "konu": "🔳 Şirket İçi KVKK Panosu",
                "gonderen_adi": "Hukuk ve Uyum Masası",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">⚖️ KVKK 2026 Yeni Veri İşleme & Gizlilik Taahhüdü</h3>
                    <p style="font-size:13px; color:#475569;">Yıllık zorunlu KVKK uyum taahhüdünü dijital imzalamak için QR kodu okutun:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Hukuki taahhütnameler şirketin resmi belge yönetim sistemi (EBYS) üzerinden imzalanır."
                ]
            }
        else:
            return {
                "baslik": "Gizlilik Sözleşmesi (NDA) & KVKK İhtarname İncelemesi",
                "konu": "[GİZLİ & İVEDİ] 2026/144 Nolu Noter İhtarnamesi ve KVKK Denetim Tutanağı",
                "gonderen_adi": "Kurumsal Hukuk ve Müşavirlik Masası",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #7c3aed; margin-top:0;">Gizli Hukuki Tebligat</h3>
                    <p>Sayın {departman} Yetkilisi,</p>
                    <p>Şirketimize tebliğ edilen <strong>#2026/144</strong> yevmiye nolu noter ihtarnamesi ve gizlilik protokolü incelemeniz için yüklenmiştir. Süresi içinde itiraz için evrakı inceleyin.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #7c3aed; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Hukuki Evrakı Görüntüle
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Hukukçuları hedef alan saldırılarda resmi evrak dili ve noter jargonu taklit edilir."
                ]
            }

    elif any(k in dep_lower for k in ["üst yönetim", "ust yonetim", "yönetim", "yonetim", "icra", "ceo", "ciso", "genel müdür"]):
        if kanal == "whatsapp":
            return {
                "baslik": "Üst Yönetim - Yönetim Kurulu Raporu & Oylama",
                "konu": "💬 İcra Kurulu: 2026 Q3 Faaliyet Raporu & Karar Metni",
                "gonderen_adi": "TrendLojistik İcra Kurulu Sekreteryası",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 Yönetim Kurulu ve İcra Masası</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sayın Yönetim Kurulu Üyesi,</strong></p>
                        <p style="margin:0 0 10px 0;">2026 Q3 bağımsız dış denetim raporu ve yönetim kurulu olağanüstü karar taslağı onayınıza sunulmuştur. Güvenli erişim için dokunun: 🏛️</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">Raporu İncele & Onayla ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">17:15 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Yönetim kurulu kararları güvenli yönetim kurulu portalları üzerinden yürütülür."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": "Üst Yönetim - Acil Denetim Onayı",
                "konu": "📱 B002 - YONETIM_KURULU",
                "gonderen_adi": "B002-YONETIM",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-YONETIM</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. Yonetim Kurulu Uyesi, bagimsiz denetim taslagi acil imzaya acilmistir. E-imza icin dokunun: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "Yönetim kurulu üyelerine yönelik 'Whaling' saldırılarında prestij ve gizlilik temaları kullanılır."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "Üst Yönetim - V.I.P. Salonu Güvenli Erişim",
                "konu": "🔳 V.I.P. Toplantı Salonu Erişim Panosu",
                "gonderen_adi": "Genel Sekreterlik",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">🏛️ Yönetim Kurulu & V.I.P. Güvenli Toplantı Odası</h3>
                    <p style="font-size:13px; color:#475569;">Görüşme salonu şifreli ekran ve sunum paylaşımına bağlanmak için QR kodu okutun:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Toplantı salonlarındaki QR kodlar üzerinden cihaz ele geçirme girişimleri yapılabilir."
                ]
            }
        else:
            return {
                "baslik": "Yönetim Kurulu Yetkilendirme & Dış Denetim Taslak Raporu",
                "konu": "[ÇOK GİZLİ] 2026 Q3 Bağımsız Dış Denetim Raporu ve Yönetim Kurulu Karar Taslağı",
                "gonderen_adi": "Yönetim Kurulu ve İcra Sekreteryası",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #047857; margin-top:0;">Yönetim Kurulu Karar Taslağı</h3>
                    <p>Sayın Yönetim Kurulu Üyemiz,</p>
                    <p>Şirketimizin 2026 üçüncü çeyrek bağımsız denetim raporu ve imza sirküleri yetkilendirme belgesi onayınıza açılmıştır.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #047857; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Karar Metnini İncele ve İmzala
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Whaling (üst düzey yönetici oltalama) saldırıları genellikle yüksek gizlilik düzeyli finansal/hukuki rapor süsü verilerek yapılır."
                ]
            }

    else:
        if kanal == "whatsapp":
            return {
                "baslik": f"WhatsApp - {departman} Kurumsal Güvenlik Onayı",
                "konu": "💬 Kurumsal Onay Hattı: Kimlik Doğrulama",
                "gonderen_adi": f"{sektor} Sistem Masası",
                "icerik_html": f"""
                <div style="background:#075e54; color:#fff; padding:15px; border-radius:10px 10px 0 0; font-family:sans-serif;">
                    <strong>🟢 Kurumsal Bilgi Güvenliği Bildirim Servisi</strong>
                </div>
                <div style="background:#e5ddd5; color:#111; padding:15px; border-radius:0 0 10px 10px; font-family:sans-serif;">
                    <div style="background:#dcf8c6; padding:12px; border-radius:8px; max-width:85%; box-shadow:0 1px 2px rgba(0,0,0,0.15);">
                        <p style="margin:0 0 8px 0;"><strong>Sayın {departman} Personeli,</strong></p>
                        <p style="margin:0 0 10px 0;">Kurumsal hesabınızın oturum süresi dolmak üzeredir. İşlemlerinizin aksamaması için doğrulayın:</p>
                        <a href="{{{{LINK}}}}" style="display:inline-block; background:#25d366; color:#fff; font-weight:bold; padding:8px 16px; border-radius:6px; text-decoration:none;">Oturumu Doğrula ↗</a>
                        <span style="display:block; font-size:10px; color:#666; text-align:right; margin-top:5px;">10:42 ✔️✔️</span>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "WhatsApp üzerinden kurumsal hesap oturumu uzatılmaz."
                ]
            }
        elif kanal == "sms":
            return {
                "baslik": f"SMS - {departman} Hesap Doğrulama",
                "konu": "📱 B002 - KURUMSAL_HESAP",
                "gonderen_adi": "B002-HESAP",
                "icerik_html": f"""
                <div style="background:#1e293b; color:#f8fafc; padding:16px; border-radius:12px; font-family:monospace; border:1px solid #334155;">
                    <div style="color:#94a3b8; font-size:11px; margin-bottom:8px;">[SMS] Gönderen: B002-HESAP</div>
                    <p style="font-size:14px; margin:0 0 12px 0;">Sn. Personel, sirket hesabinizdaki 2 faktörlu dogrulama suresi dolmustur. 15 dk icinde yenileyin: {{{{LINK}}}}</p>
                    <a href="{{{{LINK}}}}" style="color:#38bdf8; text-decoration:underline; font-weight:bold;">{{{{LINK}}}}</a>
                </div>
                """,
                "ipuclari": [
                    "SMS ile gelen acil güncelleme linklerine tıklanmamalıdır."
                ]
            }
        elif kanal == "qr":
            return {
                "baslik": "QR Kod - Yeni Ofis Wi-Fi & Personel Ağı",
                "konu": "🔳 Şirket İçi Wi-Fi Panosu",
                "gonderen_adi": "İdari İşler Masası",
                "icerik_html": f"""
                <div style="background:#ffffff; color:#0f172a; padding:24px; border-radius:12px; font-family:Arial, sans-serif; text-align:center; border:2px dashed #cbd5e1;">
                    <h3 style="margin-top:0; color:#0f172a;">📶 2026 Yeni Personel Wi-Fi Ağı</h3>
                    <p style="font-size:13px; color:#475569;">Yüksek hızlı yeni kurumsal kablosuz ağa otomatik bağlanmak için kameranızla QR kodu okutun:</p>
                    <div style="margin:20px 0;">
                        <a href="{{{{LINK}}}}" style="display:inline-block; padding:12px; background:#f8fafc; border:1px solid #94a3b8; border-radius:8px; text-decoration:none;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{{{LINK}}}}" alt="QR Kod" style="width:140px; height:140px; display:block;" />
                            <span style="display:block; font-size:11px; color:#2563eb; margin-top:8px; font-weight:bold;">[QR Kodu Okutun veya Tıklayın]</span>
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Kurumsal ağlara bağlanırken QR kod yerine resmi yönergeler izlenmelidir."
                ]
            }
        else:
            return {
                "baslik": f"Kritik {departman} Sistem Güncellemesi ve Parola Yenileme",
                "konu": "[ZORUNLU] Güvenlik Protokolü Nedeniyle Oturumunuz Kapatılacaktır",
                "gonderen_adi": "Kurumsal IT & Güvenlik Masası",
                "icerik_html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                    <h3 style="color: #ea580c; margin-top:0;">Zorunlu Güvenlik Güncellemesi</h3>
                    <p>Sayın Çalışanımız, oturumunuzu açık tutmak için doğrulayınız.</p>
                    <div style="margin: 25px 0;">
                        <a href="{{{{LINK}}}}" style="background: #ea580c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Oturumumu Güvenle Doğrula
                        </a>
                    </div>
                </div>
                """,
                "ipuclari": [
                    "Şirket bilgi işlem birimleri asla e-posta linkiyle parola doğrulamaz."
                ]
            }
