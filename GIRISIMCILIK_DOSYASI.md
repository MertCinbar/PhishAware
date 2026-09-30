# 🛡️ PhishAware - Girişimcilik & Jüri Sunum Dosyası

**Ders:** BSM3015 - Bilişim Sektöründe Girişimcilik  
**Öğrenci / Girişimci:** Mert Çinbar (Bilişim Sistemleri Mühendisliği 3. Sınıf - MSKÜ)  
**Proje Adı:** PhishAware (Şirketler İçin Otomatik Oltalama Simülasyonu ve Farkındalık Platformu)  
**Tarih:** 2026-2027 Güz Dönemi  

---

## 1. Girişimin Özeti (Executive Summary)

### Problem (Sorun)
Dünya genelinde siber güvenlik ihlallerinin **%91'i bir çalışanın oltalama (phishing) e-postasına tıklamasıyla** başlar. Şirketler bu riski azaltmak için yılda bir kez 2 saatlik sıkıcı video slayt eğitimleri düzenler. Çalışanlar bu slaytları izlemeden geçer ve ertesi gün gerçek bir sahte kargo veya fatura e-postası geldiğinde tuzağa düşer.

### Çözüm (PhishAware)
PhishAware, şirket çalışanlarına habersiz, kontrollü ve güvenli sahte oltalama tatbikatları düzenleyen yeni nesil bir **B2B SaaS** platformudur. 
* Tuzağa düşen çalışan anında **30 saniyelik interaktif farkındalık eğitimine** yönlendirilir.
* **%20 Yapay Zeka Desteği:** Gemini 3.8 Flash ile sektör ve departman psikolojisine özel gerçekçi yemleme şablonları üretir ve yönetim kuruluna (CISO) departman zaafiyet analitiğine göre 3 maddelik stratejik eylem planı sunar.

---

## 2. Mimari ve Mühendislik Dengesi (%80 Mühendislik + %20 Yapay Zeka)

Bu proje rastgele bir YZ sohbet botu değil; kurumsal ölçeklenebilirliği olan bir **Bilişim Sistemleri Mühendisliği** ürünüdür:

| Bileşen | Mühendislik Alanı (%80) | Yapay Zeka Katmanı (%20) |
| :--- | :--- | :--- |
| **Backend & API** | FastAPI, Asenkron Mimari, Pydantic Veri Doğrulama | - |
| **Veritabanı** | SQLite / PostgreSQL ORM (SQLAlchemy), 5 İlişkisel Tablo | - |
| **Takip Mekanizması** | Her çalışana özel 36 karakterlik benzersiz UUID Token sistemi | - |
| **Senaryo Üretimi** | - | **Gemini 3.8 Flash:** Sektör/Departman bazlı aciliyet içeren yem metni üretimi |
| **Yönetim & Analitik** | Departman tıklama yüzdeleri, kümülatif risk skorlama motoru | **Gemini 3.8 Flash:** Üst yönetim için CISO stratejik tavsiye raporu |
| **Raporlama & Arayüz** | Koyu Tema Glassmorphism Dashboard, CSV Export, Print A4 CSS | - |

---

## 3. İş Modeli Kanvası (Business Model Canvas - BMC)

### 1. Değer Önerisi (Value Proposition)
* **Gerçekçi Refleks:** Sıkıcı slaytlar yerine çalışanlara yaşayarak öğrenme refleksi kazandırır.
* **Terzi İşi Senaryolar:** Muhasebeciye sahte fatura, IT personeline sahte VPN güncellemesi, İK'ya sahte CV ile hedef odaklı tatbikat.
* **Yönetim İçin CISO Raporu:** Hangi departmanın daha savunmasız olduğunu netleştiren somut risk metrikleri.
* **Yasal Uyum:** KVKK, ISO 27001 ve BDDK siber güvenlik eğitim denetim gereksinimlerini tek tıkla resmi CSV raporuyla karşılar.

### 2. Müşteri Segmentleri (Customer Segments)
* **KOBİ'ler (50 - 500 Çalışan):** Kendi siber güvenlik uzmanı olmayan ancak dijital verilerini korumak zorunda olan şirketler.
* **E-Ticaret ve Lojistik:** Günlük yüzlerce sipariş ve kargo postası trafiğinde oltalanma riski en yüksek sektör.
* **Finans ve FinTech:** BDDK ve regülasyon baskısı altında personelini düzenli test etmek zorunda olan kurumlar.
* **Sağlık ve İlaç:** Hasta verilerini KVKK kapsamında koruması gereken klinikler ve hastaneler.

### 3. Kanallar (Channels)
* **B2B Doğrudan Satış & Demo:** Şirketlerin IT ve İK direktörlerine ücretsiz "İlk 10 Çalışan İçin Ücretsiz Oltalama Testi" sunarak soğuk satış.
* **Siber Güvenlik Danışmanlık Şirketleri:** MSP (Managed Service Provider) firmalarıyla gelir paylaşımı ortaklığı.
* **Dijital İçerik & LinkedIn:** "Şirketiniz Oltalama Saldırılarına Ne Kadar Hazır?" konulu vaka analizleri ve raporlar.

### 4. Müşteri İlişkileri (Customer Relationships)
* Self-service web yönetim portalı.
* Otomatik aylık CISO risk e-postaları.
* Başarılı tatbikat sonrası çalışanlara dijital farkındalık sertifikası.

### 5. Gelir Akışları (Revenue Streams - B2B SaaS)
* **Başlangıç Paketi (Starter - 50 Kişiye Kadar):** 3.500 TL / Ay (Ayda 1 simülasyon, standart şablonlar, CSV raporu).
* **Profesyonel Paket (Pro - 250 Kişiye Kadar):** 8.500 TL / Ay (Sınırsız YZ şablon üretimi, departman analitiği, AI Danışmanı).
* **Kurumsal Paket (Enterprise - 250+ Kişi):** Özel fiyatlandırma (Özel e-posta sunucusu, Active Directory/LDAP entegrasyonu, yılda 1 gün canlı siber tatbikat desteği).

### 6. Temel Kaynaklar (Key Resources)
* Yazılım fikri mülkiyeti (FastAPI tabanlı simülasyon motoru).
* Gemini API altyapısı ve senaryo yönlendirme şablonları (Prompt Engineering).
* Bulut sunucusu (Docker, PostgreSQL, Linux).

### 7. Temel Aktiviteler (Key Activities)
* Düzenli oltalama şablon kütüphanesini güncelleme.
* Güncel siber saldırı yöntemlerini (Deepfake, QR oltalama / Quishing) platforma entegre etme.
* Platform güvenliğini ve çalışan gizliliğini koruma.

### 8. Temel Ortaklıklar (Key Partners)
* Siber güvenlik danışmanları ve beyaz şapkalı hacker toplulukları.
* Teknokentler ve KOSGEB Ar-Ge Destek Programları.
* E-posta servis sağlayıcıları ve alan adı kayıt kuruluşları.

### 9. Maliyet Yapısı (Cost Structure)
* **Sunucu & Veritabanı:** ~500 TL / Ay (Başlangıç için bulut VPS).
* **LLM API Maliyeti:** Senaryo başına ~0.001$ (Gemini 3.8 Flash son derece maliyet etkin olduğundan brüt kâr marjı **>%90**).
* **Pazarlama & Satış:** Gelirin %20'si.

---

## 4. İki Dakikalık Jüri Sunumu (Elevator Pitch)

> *"Sayın jüri üyeleri, hocalarım ve arkadaşlarım;*  
>  
> *Bugün şirketlerin güvenlik açıklarının en büyük sebebi yazılımlardaki bug'lar değil, çalışanların dikkatsizliğidir. Siber saldırıların %91'i masum görünen bir oltalama e-postasıyla başlıyor. Şirketler personeline yılda bir kez saatlerce süren slaytlar izletiyor fakat ertesi gün 'Kargonuz teslim edilemedi' başlıklı bir mail geldiğinde o linke yine tıklanıyor.*  
>  
> *Biz **PhishAware** ile bu ezberi bozuyoruz. PhishAware, bilişim sistemleri mühendisliği prensipleriyle geliştirdiğimiz bir otomatik oltalama tatbikat platformudur. Şirketteki muhasebeciye sahte e-fatura, IT personeline sahte VPN güncellemesi yollayarak onları güvenli bir ortamda habersiz test ediyoruz. Tuzağa düşen personel cezalandırılmak yerine saniyeler içinde açılan modern bir farkındalık eğitimiyle bilinçlendiriliyor.*  
>  
> *Sistemimizin en güçlü yanı, %80 sağlam mühendislik altyapısının üzerine entegre ettiğimiz %20'lik yapay zeka katmanıdır. Gemini 3.8 Flash modelini kullanarak kurumun sektörüne özel gerçekçi senaryolar üretiyor ve şirket yönetimine departman bazlı zaafiyet analizi ile CISO düzeyinde stratejik eylem planları sunuyoruz.*  
>  
> *PhishAware, KOBİ'lerin siber dayanıklılığını artıran, KVKK ve ISO 27001 denetimlerini kolaylaştıran, yüksek kâr marjlı bir B2B SaaS girişimidir. Teşekkür ederim."*

---

## 5. Jüri Soru-Cevap Rehberi (Muhtemel Sorular ve Hazır Cevaplar)

**Soru 1: Piyasada KnowBe4 veya yerli siber güvenlik firmaları varken PhishAware neden tercih edilsin?**  
*Cevap:* Yabancı çözümler dolar kuru sebebiyle Türk KOBİ'leri için aşırı pahalıdır ve yerel Türk kültürüne/dinamiklerine (örneğin e-Devlet, SGK, HGS, yerel kargo şirketleri) uygun içerik üretemez. PhishAware, yerel YZ modelleriyle Türkiye'deki kurumsal dinamiklere birebir uyumlu senaryoları dakikalar içinde üretir ve çok daha uygun KOBİ dostu TL aboneliği sunar.

**Soru 2: Çalışanları habersiz test etmek KVKK açısından suç teşkil eder mi?**  
*Cevap:* Hayır. Kurumsal oltalama simülasyonları, şirketin iş sözleşmelerinde ve kabul edilebilir kullanım politikalarında yer alan "Bilgi Güvenliği Farkındalık Eğitimi" kapsamında uygulanır. PhishAware çalışanın kişisel verisini asla toplamaz veya saklamaz; yalnızca simülasyon linkine tıklanıp tıklanmadığını anonim bir token ile kayıt altına alır. Bu durum ISO 27001 kapsamında zorunlu bir denetim kriteridir.

**Soru 3: Neden %20 Yapay Zeka kullandınız? Projenin geri kalanı ne yapıyor?**  
*Cevap:* Yapay zekayı bir amaç değil, doğru yerde bir kaldıraç olarak kullandık. Sistemin omurgası olan token takibi, ilişkisel veri yönetimi, risk puanlama algoritmaları, asenkron API ve güvenlik paneli %80 oranında saf sistem mühendisliğiyle inşa edildi. Yapay zekayı ise yalnızca yaratıcılık ve stratejik karar desteği gerektiren iki alanda kullandık: Yem senaryosu yazımı ve CISO risk değerlendirmesi.
