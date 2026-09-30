from app.database import SessionLocal, Base, engine
import app.models as models
from datetime import datetime, timedelta
import uuid

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[1/4] Şirket kaydı kontrol ediliyor...")
    sirket = db.query(models.Sirket).first()
    if not sirket:
        sirket = models.Sirket(ad="TrendLojistik A.Ş.", sektor="Lojistik ve Tedarik Zinciri")
        db.add(sirket)
        db.commit()
        db.refresh(sirket)
    else:
        sirket.ad = "TrendLojistik A.Ş."
        sirket.sektor = "Lojistik ve Tedarik Zinciri"
        db.commit()

    print(f"Hedef Şirket: {sirket.ad} (ID: {sirket.id})")

    personeller = [
        {"ad": "Ayşe Yılmaz", "email": "ayse.yilmaz@trendlojistik.com", "departman": "Muhasebe ve Finans", "risk": 45, "unvan": "Mali İşler Müdürü"},
        {"ad": "Burak Kaya", "email": "burak.kaya@trendlojistik.com", "departman": "Muhasebe ve Finans", "risk": 70, "unvan": "Kıdemli Muhasebe Uzmanı"},
        {"ad": "Selin Özkan", "email": "selin.ozkan@trendlojistik.com", "departman": "Muhasebe ve Finans", "risk": 65, "unvan": "Bordro ve Ödemeler Sorumlusu"},
        {"ad": "Emre Şahin", "email": "emre.sahin@trendlojistik.com", "departman": "Muhasebe ve Finans", "risk": 30, "unvan": "Cari Hesap Denetçisi"},

        {"ad": "Caner Doğan", "email": "caner.dogan@trendlojistik.com", "departman": "Satış ve Pazarlama", "risk": 75, "unvan": "Kurumsal Satış Direktörü"},
        {"ad": "Melis Çelik", "email": "melis.celik@trendlojistik.com", "departman": "Satış ve Pazarlama", "risk": 60, "unvan": "Dijital Pazarlama & PR Uzmanı"},
        {"ad": "Volkan Erdem", "email": "volkan.erdem@trendlojistik.com", "departman": "Satış ve Pazarlama", "risk": 80, "unvan": "B2B Portföy Yöneticisi"},
        {"ad": "Ebru Aydın", "email": "ebru.aydin@trendlojistik.com", "departman": "Satış ve Pazarlama", "risk": 35, "unvan": "Saha Satış Temsilcisi"},

        {"ad": "Serkan Bulut", "email": "serkan.bulut@trendlojistik.com", "departman": "Operasyon ve Tedarik", "risk": 55, "unvan": "Filo Operasyon Şefi"},
        {"ad": "Pınar Kurt", "email": "pinar.kurt@trendlojistik.com", "departman": "Operasyon ve Tedarik", "risk": 30, "unvan": "Gümrük ve Dış Ticaret Uzmanı"},
        {"ad": "Hakan Güler", "email": "hakan.guler@trendlojistik.com", "departman": "Operasyon ve Tedarik", "risk": 60, "unvan": "Lojistik Depo Sorumlusu"},
        {"ad": "Tuğba Yavuz", "email": "tugba.yavuz@trendlojistik.com", "departman": "Operasyon ve Tedarik", "risk": 20, "unvan": "Satın Alma Sorumlusu"},

        {"ad": "Mehmet Demir", "email": "mehmet.demir@trendlojistik.com", "departman": "İnsan Kaynakları (İK)", "risk": 20, "unvan": "İK Direktörü"},
        {"ad": "Gamze Aksoy", "email": "gamze.aksoy@trendlojistik.com", "departman": "İnsan Kaynakları (İK)", "risk": 50, "unvan": "İşe Alım & Yetenek Uzmanı"},
        {"ad": "Zeynep Koç", "email": "zeynep.koc@trendlojistik.com", "departman": "İnsan Kaynakları (İK)", "risk": 30, "unvan": "Eğitim ve Gelişim Uzmanı"},

        {"ad": "Mert Çinbar", "email": "mert.cinbar@trendlojistik.com", "departman": "Bilgi İşlem (IT)", "risk": 5, "unvan": "Sistem ve Siber Güvenlik Yöneticisi"},
        {"ad": "Deniz Arslan", "email": "deniz.arslan@trendlojistik.com", "departman": "Bilgi İşlem (IT)", "risk": 10, "unvan": "Bulut & Altyapı Mühendisi"},
        {"ad": "Oğuzhan Yıldız", "email": "oguzhan.yildiz@trendlojistik.com", "departman": "Bilgi İşlem (IT)", "risk": 15, "unvan": "IT Destek ve Helpdesk Uzmanı"},

        {"ad": "Av. Gizem Çetin", "email": "gizem.cetin@trendlojistik.com", "departman": "Hukuk ve Uyum", "risk": 10, "unvan": "Kurumsal Baş Hukuk Müşaviri"},
        {"ad": "Berk Akın", "email": "berk.akin@trendlojistik.com", "departman": "Hukuk ve Uyum", "risk": 15, "unvan": "KVKK ve Bilgi Güvenliği Uyum Yöneticisi"},

        {"ad": "Kerem Soylu", "email": "kerem.soylu@trendlojistik.com", "departman": "Üst Yönetim", "risk": 10, "unvan": "Genel Müdür / CEO"},
        {"ad": "Hande Tezcan", "email": "hande.tezcan@trendlojistik.com", "departman": "Üst Yönetim", "risk": 15, "unvan": "Genel Müdür Yardımcısı / COO"},
    ]

    print("[2/4] Çalışan kayıtları senkronize ediliyor...")
    calisan_obj_list = []
    for p in personeller:
        c = db.query(models.Calisan).filter(models.Calisan.email == p["email"]).first()
        if not c:
            c = db.query(models.Calisan).filter(models.Calisan.ad_soyad == p["ad"]).first()

        if c:
            c.ad_soyad = p["ad"]
            c.email = p["email"]
            c.departman = p["departman"]
            c.risk_puani = p["risk"]
        else:
            c = models.Calisan(
                ad_soyad=p["ad"],
                email=p["email"],
                departman=p["departman"],
                risk_puani=p["risk"],
                sirket_id=sirket.id
            )
            db.add(c)
        db.commit()
        db.refresh(c)
        calisan_obj_list.append(c)

    print(f"Toplam {len(calisan_obj_list)} çalışan başarıyla veritabanına işlendi.")

    print("[3/4] Omnichannel Şablonlar kontrol ediliyor...")
    sablon_listesi = [
        {
            "baslik": "Q3 Acil E-Fatura Onay Bildirimi",
            "konu": "Önemli: 2026/Q3 Cari Hesap Mutabakat ve Bekleyen Fatura Onayı",
            "gonderen": "TrendLojistik Muhasebe Masası",
            "icerik": "Sayın {isim}, şirketiniz adına kesilmiş 42.500 TL tutarındaki bekleyen faturayı incelemek ve onaylamak için kurumsal portala giriş yapınız.",
            "kanal": "email"
        },
        {
            "baslik": "WhatsApp - İK Özel Sağlık Sigortası Yenileme",
            "konu": "TrendLojistik İK Özel Bildirim",
            "gonderen": "TrendLojistik İK Onay Hattı",
            "icerik": "Merhaba {isim}, 2026 dönemi tamamlayıcı sağlık sigortası poliçeniz hazırlanmıştır. Poliçenizi onaylamak ve aile fertlerinizi eklemek için son gün bugündür: {link}",
            "kanal": "whatsapp"
        },
        {
            "baslik": "SMS (Smishing) - Banka Şüpheli Transfer Uyarısı",
            "konu": "Banka Güvenlik Uyarısı (B002)",
            "gonderen": "B002 - TrendFinans",
            "icerik": "Sayın {isim}, kurumsal hesabınızdan saat 09:14'te 18.450 TL transfer talimatı verilmiştir. İşlem size ait değilse acilen iptal ediniz: {link}",
            "kanal": "sms"
        },
        {
            "baslik": "QR Kod - Yemek Kartı Bakiye Yükleme Afişi",
            "konu": "Ofis Yemekhanesi ve Mutfak Afişi",
            "gonderen": "TrendLojistik İdari İşler",
            "icerik": "Değerli TrendLojistik Personeli; 2026 Güz dönemi yemek kartı bakiye yüklemeleri için telefonunuzun kamerasıyla afişteki karekodu taratarak kimliğinizi doğrulayınız.",
            "kanal": "qr"
        }
    ]

    sablon_obj_list = []
    for s_data in sablon_listesi:
        s = db.query(models.Sablon).filter(models.Sablon.baslik == s_data["baslik"]).first()
        if not s:
            s = models.Sablon(
                baslik=s_data["baslik"],
                konu=s_data["konu"],
                gonderen_adi=s_data["gonderen"],
                icerik_html=s_data["icerik"],
                yapay_zeka_ile_mi=True,
                kanal=s_data["kanal"]
            )
            db.add(s)
            db.commit()
            db.refresh(s)
        sablon_obj_list.append(s)

    print("[4/4] 2026 Çok Kanallı Siber Güvenlik Tatbikatı oluşturuluyor...")
    kampanya_adi = "2026 Çok Kanallı Siber Güvenlik Tatbikatı (Q4)"
    kampanya = db.query(models.Kampanya).filter(models.Kampanya.ad == kampanya_adi).first()
    if not kampanya:
        kampanya = models.Kampanya(
            ad=kampanya_adi,
            sirket_id=sirket.id,
            sablon_id=sablon_obj_list[1].id,
            durum="aktif"
        )
        db.add(kampanya)
        db.commit()
        db.refresh(kampanya)


    durum_haritasi = {
        "ayse.yilmaz@trendlojistik.com": {"tiklandi": True, "egitim": True, "kahraman": False},
        "burak.kaya@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "selin.ozkan@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "emre.sahin@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": False},

        "caner.dogan@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "melis.celik@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "volkan.erdem@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "ebru.aydin@trendlojistik.com": {"tiklandi": True, "egitim": True, "kahraman": False},

        "serkan.bulut@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "pinar.kurt@trendlojistik.com": {"tiklandi": True, "egitim": True, "kahraman": False},
        "hakan.guler@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "tugba.yavuz@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": False},

        "mehmet.demir@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": False},
        "gamze.aksoy@trendlojistik.com": {"tiklandi": True, "egitim": False, "kahraman": False},
        "zeynep.koc@trendlojistik.com": {"tiklandi": True, "egitim": True, "kahraman": False},

        "mert.cinbar@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": True},
        "deniz.arslan@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": True},
        "oguzhan.yildiz@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": False},

        "gizem.cetin@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": True},
        "berk.akin@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": False},

        "kerem.soylu@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": False},
        "hande.tezcan@trendlojistik.com": {"tiklandi": False, "egitim": False, "kahraman": False},
    }

    db.query(models.SimulasyonLog).filter(models.SimulasyonLog.kampanya_id == kampanya.id).delete()
    db.commit()

    for c in calisan_obj_list:
        cfg = durum_haritasi.get(c.email, {"tiklandi": False, "egitim": False, "kahraman": False})
        log = models.SimulasyonLog(
            kampanya_id=kampanya.id,
            calisan_id=c.id,
            takip_kodu=uuid.uuid4().hex[:16],
            tiklandi_mi=cfg["tiklandi"],
            tiklanma_tarihi=datetime.utcnow() - timedelta(hours=3) if cfg["tiklandi"] else None,
            egitim_tamamlandi_mi=cfg["egitim"],
            supheli_bildirildi_mi=cfg["kahraman"]
        )
        db.add(log)
    db.commit()

    print("[TAMAMLANDI] 22 çalışan, zengin departman verileri ve simülasyon logları başarıyla yüklendi!")
    db.close()

if __name__ == "__main__":
    seed()
