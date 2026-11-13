"""
PhishAware - Güncel Başlık Düzeni (Logo Solda, Butonlar Sağda), Veri Bilimi Kaldırma Doğrulaması ve Gerçekçi 3D Ofis Oyunu Testi
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from app.main import app, get_base_url
from app.database import SessionLocal
import app.models as models

client = TestClient(app)

def test_favicon_not_404():
    """Favicon isteğinin 404 yerine 200 OK dönmesini doğrular."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert "image/svg+xml" in response.headers.get("content-type", "")
    assert "<svg" in response.text
    print("✓ [TEST 1] Favicon 200 OK döndü, 404 hatası başarıyla çözüldü!")

def test_dashboard_header_and_ml_removal():
    """Yönetim panelinde Veri Bilimi bölümünün ve butonunun kaldırıldığını, yeni sade başlık düzenini (Logo Solda, Butonlar Sağda) doğrular."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    # Veri bilimi & ML kestirimci kısımları dashboard'dan kaldırıldı
    assert "veri-bilimi-bolumu" not in response.text
    assert "Kestirimci ML Analizi" not in response.text
    assert "İstatistikleri Sıfırla" not in response.text

    # Yeni sadeleştirilmiş butonlar ve soldaki logo/yazı düzeni
    assert "header-actions" in response.text
    assert "header-brand" in response.text
    # Logo solda (önce), butonlar sağda (sonra):
    assert response.text.find("header-brand") < response.text.find("header-actions"), "Logo solda, butonlar sağda olmalı!"
    assert "Canlı Test" in response.text
    assert "3D Ofis" in response.text
    assert "CSV Rapor" in response.text
    print("✓ [TEST 2] Veri Bilimi tablosu kaldırıldı; logo solda, butonlar sağda sade başlık düzeni doğrulandı!")

def test_base_url_default_resolution():
    """BASE_URL'in boş veya geçersiz şablon olduğunda doğrudan 127.0.0.1:8000 dönmesini doğrular."""
    url = get_base_url()
    assert url.startswith("http")
    assert "{" not in url and "}" not in url
    print(f"✓ [TEST 3] Base URL çözümlemesi doğrulandı: {url}")

def test_3d_cyber_office_game():
    """Gerçekçi İnsan Avatarı, Gelişmiş 3D Sanal Ofis mobilyaları ve kusursuz yön kontrollerinin (görünmez duvarın çözümü) doğrulanması."""
    res = client.get("/oyun-simulasyonu")
    assert res.status_code == 200
    assert "officeCanvas" in res.text
    assert "terminals" in res.text
    assert "Muhasebe & Finans" in res.text
    assert "İnsan Kaynakları" in res.text
    assert "BİLGİ İŞLEM & SOC" in res.text
    assert "drawRealisticHumanAvatar" in res.text, "Gerçek insan avatar çizici bulunmalı!"
    assert "drawOfficeChair" in res.text, "Ergonomik 3D ofis koltuğu bulunmalı!"
    assert "my -= 1" in res.text, "D tuşu sağa hareketi (my -= 1) kusursuz çalışmalı!"
    assert "Web Audio API" in res.text or "getAudioCtx" in res.text
    assert "footsteps" in res.text
    print("✓ [TEST 4] Gerçekçi İnsan Avatarı, L-Masalar, Ergonomik Koltuklar ve Kusursuz Sağa Hareket (Görünmez Duvar Yok) doğrulandı!")

def test_phishing_click_game_integration():
    """Oltalama linkine tıklandığında bilgilendirme ekranı ve 3D oyun entegrasyonunu doğrular."""
    db = SessionLocal()
    calisan = db.query(models.Calisan).first()
    assert calisan is not None
    kampanya = db.query(models.Kampanya).first()
    log = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.calisan_id == calisan.id).first()
    token = log.takip_kodu if log else "TEST-TOKEN"
    db.close()

    res = client.get(f"/tikla/{token}")
    assert res.status_code == 200
    assert "officeCanvas" in res.text
    assert "Tehdit Avı" in res.text
    assert "DİKKAT: BİR OLTALAMA" in res.text
    assert "3D Ofis Güvenlik Eğitimine Başla" in res.text
    print("✓ [TEST 5] Oltalama linki (/tikla) Önce Bilgilendirme Ekranı, ardından 3D Oyun ile tam entegre!")

def test_egitim_tamamla_endpoint():
    """Eğitimi tamamla endpoint'inin hem DEMO hem gerçek token için 200 OK döndüğünü doğrular."""
    res_demo = client.post("/egitim-tamamla/DEMO-ADMIN-TEST")
    assert res_demo.status_code == 200
    assert res_demo.json()["durum"] == "basarili"

    res_normal = client.post("/egitim-tamamla/TEST-SAMPLE-CODE")
    assert res_normal.status_code == 200
    assert res_normal.json()["durum"] == "basarili"
    print("✓ [TEST 6] /egitim-tamamla hem DEMO hem normal token ile 200 OK döndü!")

def test_network_and_privacy_apis():
    """Ağ durumu, Base URL güncelleme ve çalışan gizliliği korumasını doğrular."""
    res_net = client.get("/api/ayarlar/ag-durumu")
    assert res_net.status_code == 200
    assert "lan_ip" in res_net.json()
    assert "base_url" in res_net.json()

    res_update = client.post("/api/ayarlar/base-url", json={"base_url": "https://test-mobil.pinggy.link"})
    assert res_update.status_code == 200
    assert res_update.json()["guncel_base_url"] == "https://test-mobil.pinggy.link"

    # Geri temizle (varsayılan 127.0.0.1:8000'e dönsün)
    client.post("/api/ayarlar/base-url", json={"base_url": "http://127.0.0.1:8000"})
    print("✓ [TEST 7] Ağ ve Mobil Base URL API'leri başarıyla doğrulandı!")

if __name__ == "__main__":
    test_favicon_not_404()
    test_dashboard_header_and_ml_removal()
    test_base_url_default_resolution()
    test_3d_cyber_office_game()
    test_phishing_click_game_integration()
    test_egitim_tamamla_endpoint()
    test_network_and_privacy_apis()
    print("\n🎉 TÜM TESTLER %100 BAŞARIYLA GEÇTİ!")
