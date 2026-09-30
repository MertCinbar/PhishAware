# 🛡️ PhishAware - Otonom Oltalama Simülasyonu ve Çalışan Güvenlik Farkındalık Platformu

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy_2.0-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Aktif_Tatbikat-10b981?style=for-the-badge)](http://127.0.0.1:8000/dashboard)

**PhishAware**, modern kurumlarda insan kaynaklı siber güvenlik zaafiyetlerini proaktif olarak tespit etmek, çalışanların oltalama (phishing) farkındalığını artırmak ve denetim raporları sunmak için geliştirilmiş yeni nesil **B2B SaaS oltalama simülasyon ve eğitim platformudur**.

---

## ⚡ Neden PhishAware?

Dünyadaki siber saldırıların **%91'inden fazlası** sistem açıklarından değil, bir çalışanın dikkatsizliğinden kaynaklanmaktadır. PhishAware, klasik sıkıcı eğitim slaytları yerine **"Siber Aşı" ve "Dijital Yangın Tatbikatı"** mantığıyla çalışır. Çalışanlara habersiz, güvenli ve kontrollü tuzaklar göndererek hata anında canlı farkındalık kazandırır.

### 🌟 Öne Çıkan Özellikler

- **Çok Kanallı (Omnichannel) Tatbikat Desteği:**
  - ✉️ **E-Posta (Spear Phishing):** Departmana özel hazırlanmış maskelenmiş kurumsal e-postalar.
  - 💬 **WhatsApp & SMS (Smishing):** Mobil çalışanları hedefleyen fatura, kargo veya hesap doğrulama senaryoları.
  - 📱 **Dinamik QR Kod (Quishing):** Dinamik SVG/PNG QR kodları ile fiziksel ve dijital tarama testleri.
- **Departman Bazlı Akıllı Yapay Zeka Eşleme (%20 YZ / %80 Mühendislik):**
  - Tek tıkla ister tüm şirkete, ister belirli bir birime (IT, İK, Finans, Satış vb.) uygun senaryolar atanır.
  - IT personeline SSH/yama uyarısı, İK personeline bordro/yan haklar, Finans birimine IBAN/fatura iptali senaryosu otomatik üretilir.
- **Benzersiz Güvenlik Takip Tokenları (UUID4):**
  - Her bir personele özel 36 karakterlik tekil takip kodları ile sıfır sahte pozitif (false-positive).
- **İnteraktif İhlal ve Anında Eğitim Ekranı (Landing Page):**
  - Tuzağa düşen personele virüs bulaşmaz; sakinleştirici, hatasını gösteren ve 3 kritik güvenlik ipucunu anlatan interaktif bir mikro eğitim sunulur.
- **Siber Kahraman (PhishAlert) İhbar Mekanizması:**
  - Oltalamayı fark edip bildiren çalışanlara pozitif ödül puanı verilir; risk puanları düşürülür.
- **Yönetici ve CISO Operasyon Masası:**
  - Canlı radar göstergeli neon siber dashboard, departman risk matrisi, Excel/CSV UTF-8 BOM denetim raporu indirme ve A4 baskı formatı.

---

## 🏗️ Mimari ve Teknoloji Yığını

```text
PhishAware/
├── app/
│   ├── database.py         # SQLAlchemy ORM motoru ve SQLite oturum yöneticisi
│   ├── models.py           # 5 İlişkisel ORM Tablosu (Sirket, Calisan, Sablon, vb.)
│   ├── schemas.py          # Pydantic v2 veri doğrulama şemaları
│   ├── ai_generator.py     # Gemini Flash API motoru ve zengin yerel senaryo matrisi
│   ├── dispatcher.py       # Çok kanallı akıllı dağıtım, SMTP ve maskeleme motoru
│   └── main.py             # FastAPI çekirdeği, Analitik motoru, CSV export & Dashboard
├── seed_corporate_data.py  # 22 çalışanlı kurumsal TrendLojistik demo veritabanı kurulumu
├── seed.py                 # Temel başlangıç test verileri
├── baslat.bat              # Tek tıkla sunucuyu başlatıp dashboard'u açan betik
├── requirements.txt        # Python bağımlılıkları
├── .env.example            # Güvenli çevre değişkenleri şablonu
└── .gitignore              # Gizlilik ve güvenlik filtreleri
```

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **ORM & Veritabanı:** SQLAlchemy 2.0, SQLite
- **Yapay Zeka:** Google Gemini API (İsteğe bağlı) + Zengin Çevrimdışı Kurumsal Senaryo Matrisi
- **Arayüz:** Vanilla HTML5, CSS3 (Orijinal Neon Siber Tema), CSS Telemetri Animasyonları

---

## 🚀 Hızlı Başlangıç

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/MertCinbar/PhishAware.git
cd PhishAware
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Çevre Değişkenlerini Ayarlayın (İsteğe Bağlı)
```bash
cp .env.example .env
```
> *.env dosyasında `GEMINI_API_KEY` ve `SMTP_*` bilgilerini girebilirsiniz. Boş bırakırsanız sistem çevrimdışı kurumsal senaryolarla ve güvenli simülasyon kuyruğuyla çalışır.*

### 4. Kurumsal Örnek Veritabanını Oluşturun
```bash
python seed_corporate_data.py
```
*(TrendLojistik A.Ş. bünyesinde 7 departmana dağılmış 22 gerçekçi personel veritabanına işlenir).*

### 5. Sunucuyu Başlatın
**Windows için tek tıkla:** `baslat.bat` dosyasına çift tıklayabilirsiniz.  
**Veya terminalden:**
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🖥️ Kullanıcı Portalları ve Endpoint'ler

Sunucu ayağa kalktığında tarayıcınızdan erişebilirsiniz:

| Bağlantı | Açıklama |
| :--- | :--- |
| **[http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)** | 🛡️ **Yönetim & Operasyon Masası:** Canlı tatbikat başlatma, risk metrikleri ve raporlar. |
| **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** | 📑 **Interactive Swagger UI:** Tüm REST API uç noktalarının canlı testi. |
| **[http://127.0.0.1:8000/rapor/csv/1](http://127.0.0.1:8000/rapor/csv/1)** | 📥 **Resmi Denetim Raporu:** UTF-8 BOM destekli Türkçe Excel/CSV indirme. |

---

## 🔒 Güvenlik, Gizlilik ve Etik Beyan

- **Eğitim ve Savunma Amaçlıdır:** PhishAware, yalnızca yetkili kurumların kendi çalışanlarına yönelik farkındalık tatbikatları ve akademik araştırma amacıyla tasarlanmıştır.
- **İzin ve Yetkilendirme:** Sistem, hedef personelin açık rızası ve kurum yönetiminin yasal izni olmadan üçüncü şahıslara karşı kullanılamaz.
- **Kişisel Veri Gizliliği:** Depo içerisine hiçbir gerçek kimlik bilgisi, parola, token veya gizli anahtar dahil edilmemiştir. `.gitignore` ve `.env.example` standartlarına tam uyumludur.

---

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakabilirsiniz.

---

**Geliştirici:** [Mert Çinbar](https://github.com/MertCinbar)  
*Muğla Sıtkı Koçman Üniversitesi - Bilişim Sistemleri Mühendisliği*
