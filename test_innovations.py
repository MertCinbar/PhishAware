import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
import app.models as models

client = TestClient(app)

def test_innovations():
    print("--- 1. Testing AI Template Generation with Multi-Channel ---")
    res = client.post("/ai/sablon-uret", json={
        "sektor": "Finans ve Bankacılık",
        "departman": "Muhasebe ve Finans",
        "zorluk": "orta",
        "kanal": "whatsapp"
    })
    assert res.status_code == 200, f"AI generation failed: {res.text}"
    wa_data = res.json()
    print(f"[OK] WhatsApp Template Generated: {wa_data['baslik']} (Kanal: {wa_data['kanal']})")
    assert wa_data["kanal"] == "whatsapp"

    res = client.post("/ai/sablon-uret", json={
        "sektor": "Lojistik ve Taşımacılık",
        "departman": "İnsan Kaynakları (İK)",
        "zorluk": "kolay",
        "kanal": "sms"
    })
    assert res.status_code == 200, f"SMS AI generation failed: {res.text}"
    sms_data = res.json()
    print(f"[OK] SMS Template Generated: {sms_data['baslik']} (Kanal: {sms_data['kanal']})")
    assert sms_data["kanal"] == "sms"

    print("\n--- 2. Testing Campaign Launch with WhatsApp Template ---")
    db = SessionLocal()
    sirket = db.query(models.Sirket).first()
    db.close()
    assert sirket is not None, "Şirket bulunamadı!"

    res = client.post("/kampanyalar/baslat", json={
        "ad": "2026 WhatsApp & Smishing Farkındalık Tatbikatı",
        "sirket_id": sirket.id,
        "sablon_id": wa_data["id"]
    })
    assert res.status_code == 200, f"Campaign launch failed: {res.text}"
    kampanya = res.json()
    print(f"[OK] Campaign started: {kampanya['kampanya_adi']} with {kampanya['toplam_hedef_calisan']} targets")

    print("\n--- 3. Testing Landing Page (Trap & Breach Simulation) ---")
    db = SessionLocal()
    hedef_log = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.kampanya_id == kampanya["kampanya_id"]).first()
    assert hedef_log is not None, "SimulasyonLog bulunamadı!"
    takip_kodu = hedef_log.takip_kodu
    eski_risk = hedef_log.calisan.risk_puani
    db.close()

    res = client.get(f"/tikla/{takip_kodu}")
    assert res.status_code == 200, f"Landing page failed: {res.status_code}"
    html = res.text
    assert "screenTrap" in html
    assert "screenBreach" in html
    assert "screenHero" in html
    assert "PhishAlert" in html
    print("[OK] Personalized Multi-Stage Breach & Hero Landing Page Loaded Successfully!")

    print("\n--- 4. Testing Siber Kahraman (PhishAlert) Reporting ---")
    res = client.post(f"/bildir/{takip_kodu}")
    assert res.status_code == 200, f"PhishAlert report failed: {res.text}"
    bildir_data = res.json()
    print(f"[OK] PhishAlert Response: {bildir_data['mesaj']}")
    assert bildir_data["durum"] == "basarili"

    db = SessionLocal()
    hedef_log = db.query(models.SimulasyonLog).filter(models.SimulasyonLog.takip_kodu == takip_kodu).first()
    assert hedef_log.supheli_bildirildi_mi == True
    print(f"[OK] Risk Score rewarded: {eski_risk} -> {hedef_log.calisan.risk_puani}")
    db.close()

    print("\n--- 5. Testing Dashboard Rendering with Channel and Hero Badge ---")
    res = client.get("/dashboard")
    assert res.status_code == 200
    d_html = res.text
    assert "Siber Kahraman" in d_html
    assert "WhatsApp" in d_html
    print("[OK] Dashboard displays Kanal badge and Siber Kahraman status correctly!")

    print("\n[SUCCESS] ALL INNOVATION TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_innovations()
