# PhishAware - 3D Sanal Ofis İnteraktif Siber Güvenlik Mini Oyunu (Unity & WebGL)

Bu modül, PhishAware kurumsal oltalama simülasyonu kapsamında tuzağa düşen çalışanları sıkıcı metin sayfaları yerine **3D Sanal Ofis (Cyber Office Simulation)** mini oyununa sokarak eğitmek için geliştirilmiştir.

---

## 🎮 Oyunlaştırma ve Senaryo Mimarisi
1. **İzometrik / Birinci Şahıs PlayerController (`PlayerController.cs`)**:
   - WASD / Yön tuşları ile ofis içinde fizik tabanlı hareket.
   - Shift ile koşma modu.
   - Terminallere yaklaşıldığında otomatik tespit (`Physics.OverlapSphere`) ve `[E]` etkileşim istemi.

2. **3 Ayrı Departman İstasyonu (`OfficeTerminal.cs`)**:
   - **Terminal 1 (Muhasebe Masası):** Sahte IBAN değişikliği ve acil fatura ödeme oltası analizi.
   - **Terminal 2 (İK Masası):** "Maaş Zammı & Yan Haklar Listesi (Makro İçeren Ek)" senaryosu.
   - **Terminal 3 (Sistem Odası / IT Masası):** Gerçek vs Sahte parola yenileme e-postasını ayırt etme testi.

3. **Kritik Kural:**
   - Çalışan 3 terminaldeki e-postaları doğru analiz edip başarıyla tamamlamadan eğitim modülünden çıkamaz!

4. **FastAPI & WebGL Köprüsü (`PhishAwareBridge.jslib` & `GameManager.cs`)**:
   - Oyun bittiğinde `NotifyTrainingCompleted(token)` fonksiyonu çağrılır.
   - Arka planda `POST /egitim-tamamla/{takip_kodu}` uç noktasına istek atılarak çalışanın zaafiyeti silinir ve siber farkındalık sertifikası verilir.

---

## 🛠️ Unity Kurulum & WebGL Build Alma
1. Unity Hub üzerinden **Unity 2022.3 LTS** veya **Unity 2023 LTS** sürümünü açın (WebGL Build Support modülü yüklü olmalıdır).
2. `Assets/Scenes/CyberOfficeScene.unity` sahnesini oluşturun.
3. `File > Build Settings > WebGL` platformunu seçin ve `Switch Platform` butonuna tıklayın.
4. `Player Settings > Resolution and Presentation` altından WebGL şablonunu seçin.
5. `Build` diyerek çıktıyı doğrudan PhishAware'in `app/static/game` klasörüne aktarın.
