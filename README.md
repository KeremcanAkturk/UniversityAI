# 🎓 İKÜ Kampüs Asistanı (v2.0)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlebard&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**İstanbul Kültür Üniversitesi (İKÜ)** öğrencileri için geliştirilmiş; **Google Gemini LLM** destekli, veritabanı yönetimli ve gerçek zamanlı kampüs asistanıdır.

Geleneksel chatbotların aksine, bu asistan **RAG (Retrieval-Augmented Generation)** mimarisini kullanır. Yani okul hakkındaki bilgileri kendi veritabanından doğrular ve Google Gemini'nin doğal dil yeteneği ile öğrenciye sunar.

---

## 🚀 Yenilikler (v2.0)
* **🧠 Hibrit Zeka:** Sadece önceden yazılmış cevapları vermez; veritabanındaki bilgiyi okur, yorumlar ve Gemini AI ile sohbet eder gibi cevaplar.
* **🔐 Yönetici (Admin) Paneli:** Şifre korumalı panel üzerinden kod yazmadan yeni bilgi eklenebilir.
* **📂 Excel/CSV ile Toplu Veri Yükleme:** Yüzlerce akademik veriyi (hoca listesi, dersler vb.) tek tıkla sisteme yükleme özelliği.
* **💾 SQLite Veritabanı:** Veriler kalıcı olarak `.db` dosyasında tutulur, uygulama kapansa bile kaybolmaz.

---

## ✨ Temel Özellikler

### 🤖 Yapay Zeka & RAG Mimarisi
* **Akıllı Vektör Arama:** `sentence-transformers` kullanarak kullanıcının sorusunu matematiksel vektöre çevirir ve veritabanındaki en alakalı bilgiyi bulur.
* **Google Gemini Pro Entegrasyonu:** Bulunan bilgiyi alır, öğrenciye samimi ve doğal bir dille açıklar.
* **Dinamik Hafıza:** Admin panelinden eklenen bir bilgi anında AI tarafından öğrenilir.

### 🛠️ Yönetim ve Admin Paneli
* **Güvenli Giriş:** Özel yönetici şifresi ile erişilen panel.
* **Veri Yönetimi:** Tek tek soru-cevap ekleme, düzenleme ve ID ile silme özelliği.
* **Bulk Upload:** `.xlsx` veya `.csv` dosyalarını sürükle-bırak yöntemiyle veritabanına işleme.

### 🚌 Öğrenci Dostu Araçlar
* **Ring Servisi Sayacı:** Anlık saate göre bir sonraki servisin kalkmasına **kaç dakika kaldığını** otomatik hesaplar.
* **Canlı Hava Durumu:** Kampüs bölgesinin anlık hava durumunu gösterir.
* **GPA Hesaplama & Takvim:** Not ortalaması hesaplayıcı ve akademik takvim entegrasyonu.

### 🎨 UI/UX Tasarımı
* **Oto-Scroll (JavaScript):** Mesajlaşıldığında ekran otomatik olarak en son mesaja kayar.
* **Responsive Yan Menü:** Kullanıcıyı takip eden araçlar menüsü.

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Kullanım Amacı |
| :--- | :--- |
| **Streamlit** | Modern web arayüzü ve session yönetimi. |
| **Google Generative AI** | (Gemini 1.5 Pro) Doğal dil üretimi ve sohbet yeteneği. |
| **Sentence-Transformers** | Metinleri vektöre çevirme (Embedding) ve benzerlik araması. |
| **SQLite3** | Soruların ve cevapların tutulduğu yerel veritabanı. |
| **Pandas & Openpyxl** | Excel ve CSV dosyalarını işlemek ve tablo yönetimi için. |

---

## 💻 Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için:

**1. Repoyu Klonlayın**
```bash
git clone [https://github.com/kullaniciadin/iku-kampus-asistani.git](https://github.com/kullaniciadin/iku-kampus-asistani.git)
cd iku-kampus-asistani
```

**2. Gerekli Kütüphaneleri Yükleyin**
```
pip install streamlit google-generativeai sentence-transformers pandas openpyxl
```


**3. API Anahtarını Ayarlayın app.py dosyasını açın ve Google AI Studio'dan aldığınız API anahtarını ilgili alana yapıştırın:**
```
SABIT_API_KEY = "BURAYA_GOOGLE_API_KEY_GELECEK"
```

**4. Uygulamayı Başlatın**
```
streamlit run app.py
# Veya oluşturulan Baslat.bat dosyasına çift tıklayın.
```

📂 Proje Yapısı
```
iku-kampus-asistani/
├── app.py              # Ana uygulama (Frontend + Backend + AI Mantığı)
├── kampus.db           # SQLite Veritabanı (Sorular ve Cevaplar burada tutulur)
├── Baslat.bat          # Tek tıkla kurulum ve başlatma dosyası
├── requirements.txt    # Kütüphane listesi
└── README.md           # Dokümantasyon
```

###🧠 Nasıl Çalışır? (Teknik Akış)
Soru Sorma: Kullanıcı bir soru sorar (Örn: "Erdem Yücesan kimdir?").

Vektör Arama: Sistem, bu soruyu vektöre çevirir ve kampus.db içindeki en benzer soruyu bulur.

Güven Kontrolü: Benzerlik oranı %40'ın üzerindeyse, bulunan veriyi "Bağlam (Context)" olarak alır.

LLM Yanıtı: Bulunan bilgi ve kullanıcının sorusu Google Gemini'ye gönderilir.

Cevap: Gemini, elindeki kesin bilgiyi kullanarak öğrenciye doğal bir cevap üretir.



###📷 Ekran Görüntüleri



<img width="1916" height="937" alt="image" src="https://github.com/user-attachments/assets/f356d10f-4dbf-4f68-a928-6446162fee73" />

<img width="1599" height="534" alt="image" src="https://github.com/user-attachments/assets/9c179222-bdce-4a0e-85b7-f89dc8ef27da" />

<img width="1591" height="643" alt="image" src="https://github.com/user-attachments/assets/d50f7e06-ae27-4674-bae2-865452a8ce89" />

<img width="186" height="136" alt="image" src="https://github.com/user-attachments/assets/473d4b84-36e8-48b1-961f-393d609dc32f" />



