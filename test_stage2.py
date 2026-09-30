import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- AŞAMA 2 TESTLERİ BAŞLIYOR ---\n")

istek_veri = {
    "sirket_id": 1,
    "sablon_id": 1,
    "ad": "2026 Güz Dönemi İlk Oltalama Tatbikatı"
}
r_baslat = client.post("/kampanyalar/baslat", json=istek_veri)
assert r_baslat.status_code == 200, f"Hata: {r_baslat.text}"
kampanya_data = r_baslat.json()
kampanya_id = kampanya_data["kampanya_id"]

print(f"[OK] Kampanya Başlatıldı! ID: {kampanya_id}, Ad: {kampanya_data['kampanya_adi']}")
print(f"[OK] Hedeflenen Çalışan Sayısı: {kampanya_data['toplam_hedef_calisan']}")

hedefler = kampanya_data["hedefler"]
for h in hedefler:
    print(f"  -> Çalışan: {h['calisan_adi']} ({h['departman']}) | Link: {h['simule_link']}")

secilen_hedef = hedefler[0]
token = secilen_hedef["takip_kodu"]
print(f"\n[TEST] {secilen_hedef['calisan_adi']} linke tıklıyor: /tikla/{token}")

r_tikla = client.get(f"/tikla/{token}")
assert r_tikla.status_code == 200
assert "Oltalama" in r_tikla.text
print("[OK] Tıklama yakalandı ve Farkındalık Eğitimi HTML sayfası döndü!")

r_egitim = client.post(f"/egitim-tamamla/{token}")
assert r_egitim.status_code == 200
print(f"[OK] Eğitim tamamlandı API yanıtı: {r_egitim.json()['mesaj']}")

r_ozet = client.get(f"/kampanyalar/{kampanya_id}/ozet")
assert r_ozet.status_code == 200
ozet = r_ozet.json()
print("\n--- GÜNCEL KAMPANYA İSTATİSTİKLERİ ---")
print(f"Toplam Hedef: {ozet['toplam_hedef_calisan']}")
print(f"Tuzağa Düşen / Tıklayan: {ozet['tiklayan_sayisi']}")
print(f"Eğitimi Tamamlayan: {ozet['egitim_tamamlayan_sayisi']}")
print(f"Oltalama Başarı Oranı: %{ozet['tiklanma_orani_yuzde']}")

r_calisan = client.get(f"/calisanlar/?sirket_id=1")
calisanlar = r_calisan.json()
mert = next(c for c in calisanlar if c["ad_soyad"] == secilen_hedef["calisan_adi"])
print(f"\n[OK] {mert['ad_soyad']} yeni risk puanı: {mert['risk_puani']} (Başlangıç 0 idi, +10 eklendi)")

print("\n[TEBRIKLER] ASAMA 2 TUM TESTLERI BASARIYLA GECTI!")
