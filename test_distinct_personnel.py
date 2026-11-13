import sys, os
sys.path.insert(0, r'c:\Users\pc\Desktop\DERS\PhishAware')
sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
import app.models as models

client = TestClient(app)

def test_distinct_target_personnel_live_tests():
    """Canlı testler tekrar tekrar gönderildiğinde hedef personel sayısının artmadığını doğrular."""
    db = SessionLocal()
    # Mevcut kampanya ve çalışanları al
    kampanya = db.query(models.Kampanya).order_by(models.Kampanya.id.desc()).first()
    assert kampanya is not None
    sablon = db.query(models.Sablon).first()
    assert sablon is not None
    calisan = db.query(models.Calisan).first()
    assert calisan is not None
    db.close()

    # Dashboard başlangıç hedef personel sayısını al
    res_dash1 = client.get("/dashboard")
    assert res_dash1.status_code == 200

    import re
    # <div class="stat-value">22</div> gibi bir değer yakala
    matches = re.findall(r'<div class="stat-value">(.*?)</div>', res_dash1.text)
    assert len(matches) > 0
    baslangic_hedef_sayisi = int(matches[0].strip())
    print(f"Başlangıç Hedef Personel Sayısı: {baslangic_hedef_sayisi}")

    # Canlı Mail Testi 1 Gönder (Mert Çinbar)
    res_mail1 = client.post(
        f"/simulasyon/canli-mail-testi?alici_email={calisan.email}&sablon_id={sablon.id}"
    )
    assert res_mail1.status_code == 200

    # Dashboard'ı kontrol et - sayı artmamalı!
    res_dash2 = client.get("/dashboard")
    matches2 = re.findall(r'<div class="stat-value">(.*?)</div>', res_dash2.text)
    hedef_sayisi2 = int(matches2[0].strip())
    assert hedef_sayisi2 == baslangic_hedef_sayisi, f"Hedef sayısı {baslangic_hedef_sayisi}'den {hedef_sayisi2}'ye arttı! HATA!"
    print(f"✓ 1. Test Sonrası Hedef Sayısı Korundu: {hedef_sayisi2}")

    # Canlı Mail Testi 2 Gönder (Aynı personele tekrar)
    res_mail2 = client.post(
        f"/simulasyon/canli-mail-testi?alici_email={calisan.email}&sablon_id={sablon.id}"
    )
    assert res_mail2.status_code == 200

    # Dashboard'ı kontrol et - sayı yine artmamalı!
    res_dash3 = client.get("/dashboard")
    matches3 = re.findall(r'<div class="stat-value">(.*?)</div>', res_dash3.text)
    hedef_sayisi3 = int(matches3[0].strip())
    assert hedef_sayisi3 == baslangic_hedef_sayisi, f"Hedef sayısı {baslangic_hedef_sayisi}'den {hedef_sayisi3}'e arttı! HATA!"
    print(f"✓ 2. Test Sonrası Hedef Sayısı Korundu: {hedef_sayisi3}")

    # Canlı Telegram Testi Gönder (Aynı personele)
    res_tg = client.post(
        f"/simulasyon/canli-telegram-testi?calisan_id={calisan.id}"
    )
    assert res_tg.status_code == 200

    # Dashboard'ı kontrol et - sayı yine artmamalı!
    res_dash4 = client.get("/dashboard")
    matches4 = re.findall(r'<div class="stat-value">(.*?)</div>', res_dash4.text)
    hedef_sayisi4 = int(matches4[0].strip())
    assert hedef_sayisi4 == baslangic_hedef_sayisi, f"Hedef sayısı {baslangic_hedef_sayisi}'den {hedef_sayisi4}'e arttı! HATA!"
    print(f"✓ Telegram Testi Sonrası Hedef Sayısı Korundu: {hedef_sayisi4}")

    print("🎉 TÜM TEKİL HEDEF PERSONEL TESTLERİ %100 BAŞARIYLA GEÇTİ!")

if __name__ == "__main__":
    test_distinct_target_personnel_live_tests()
