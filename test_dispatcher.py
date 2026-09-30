import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
import app.models as models

client = TestClient(app)

def test_dispatcher():
    print("--- 1. Testing Automated Omnichannel Bulk Dispatch ---")
    db = SessionLocal()
    sirket = db.query(models.Sirket).first()
    sablon = db.query(models.Sablon).first()
    db.close()

    assert sirket is not None
    assert sablon is not None

    res = client.post("/kampanyalar/baslat", json={
        "ad": "2026 Otomatik Otonom Dağıtım Tatbikatı",
        "sirket_id": sirket.id,
        "sablon_id": sablon.id
    })
    assert res.status_code == 200, f"Kampanya başlatılamadı: {res.text}"
    data = res.json()
    assert "dagitim_raporu" in data, "dagitim_raporu bulunamadı!"
    rapor = data["dagitim_raporu"]
    print(f"[OK] Otomatik Dağıtım Başarılı: {rapor['toplam_hedef']} personele dağıtıldı.")
    print(f"[OK] Maskelenmiş Gönderici: {rapor['maskelenmis_gonderici']}")
    assert len(rapor["loglar"]) == 22, f"Beklenen 22 hedef, gelen: {len(rapor['loglar'])}"

    print("\n--- 2. Testing Live Email Test Endpoint (Simulation Fallback) ---")
    res_mail = client.post(f"/simulasyon/canli-mail-testi?alici_email=test.guvenlik@ornek.com&sablon_id={sablon.id}")
    assert res_mail.status_code == 200
    mail_data = res_mail.json()
    assert mail_data["durum"] in ["simule", "basarili", "hata"]
    print(f"[OK] Canlı Mail Test Yanıtı: {mail_data['durum']} - {mail_data['mesaj'][:60]}...")

    print("\n--- 3. Testing Live Email Test with Custom SMTP Params (Mock/Invalid Host) ---")
    res_smtp = client.post(
        f"/simulasyon/canli-mail-testi?alici_email=test.guvenlik@ornek.com&sablon_id={sablon.id}&smtp_host=127.0.0.1&smtp_port=9999&smtp_user=test@mu.edu.tr&smtp_pass=testpass&kaydet=false"
    )
    assert res_smtp.status_code == 200
    smtp_data = res_smtp.json()
    assert smtp_data["durum"] == "hata"
    print(f"[OK] SMTP Parametre Testi: {smtp_data['durum']} (Beklendiği gibi bağlantı hatası yakalandı)")

    print("\n--- 4. Testing Dashboard Rendering with Terminal & Email Modals ---")
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    html = res_dash.text
    assert "modalTerminal" in html
    assert "modalEpostaTest" in html
    assert "akisliDagitimGoster" in html
    assert "smtpAyarGovde" in html
    assert "smtpHazirPreset" in html
    assert "toggleSmtpAyar" in html
    print("[OK] Dashboard contains Live Terminal Dispatch Console, SMTP Accordion & Email Test Modal!")

    print("\n[SUCCESS] ALL DISPATCHER TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_dispatcher()
