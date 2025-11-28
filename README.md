# 🎓 İKÜ Kampüs Asistanı (v1.0)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![AI](https://img.shields.io/badge/AI-Sentence--Transformers-green?style=for-the-badge)

**İstanbul Kültür Üniversitesi (İKÜ)** öğrencileri için geliştirilmiş; yapay zeka destekli, gerçek zamanlı veriler sunan ve kampüs hayatını kolaylaştıran interaktif bir web asistanıdır.

---

## 🚀 Proje Hakkında

Öğrencilerin kampüs hayatındaki dağınık bilgiler (servis saatleri, yemek listesi, akademik takvim vb.) arasında kaybolmasını önlemek amacıyla geliştirilmiştir. **Doğal Dil İşleme (NLP)** teknolojisi kullanan bu asistan, soruları anlar ve en doğru cevabı verir.

---

## ✨ Temel Özellikler

### 🤖 Yapay Zeka & Chatbot
* **NLP Teknolojisi:** `sentence-transformers` ve **Vektör Benzerliği (Cosine Similarity)** kullanarak kullanıcı sorularını anlar.
* **Doğal Sohbet:** Sabit cevaplar yerine rastgele varyasyonlarla robotik olmayan bir deneyim sunar.
* **Hata Yönetimi:** Anlamadığı sorularda dürüstçe cevap vererek yanlış yönlendirme yapmaz.

### 🚌 Gerçek Zamanlı Araçlar
* **Akıllı Ring Servisi Sayacı:** Statik bir liste yerine, anlık saate göre bir sonraki servisin kalkmasına **kaç dakika kaldığını** otomatik hesaplar.
* **Canlı Hava Durumu:** Open-Meteo API entegrasyonu ile kampüs bölgesinin hava durumunu anlık gösterir (15 dk önbellekleme ile performans optimizasyonu sağlar).

### 🎨 Modern UI/UX Tasarımı
* **Sticky Sidebar:** Sayfa aşağı kaydırılsa bile yan menü ve araçlar sabit kalarak kullanıcıyı takip eder.
* **Auto-Scroll:** Mesaj yazıldığında sayfa otomatik olarak en son mesaja odaklanır.
* **Güvenli Giriş:** Regex tabanlı isim doğrulama ve oturum (session) yönetimi içerir.
* **Karanlık Mod:** Göz yormayan, "Glassmorphism" efektli şık tasarım.

### 📚 Öğrenci Modülleri
* **GPA Hesaplama:** Okulun (+/-) not sistemine tam uyumlu ortalama hesaplayıcı.
* **Akademik Takvim:** Sınav ve tatil tarihlerini gösteren güncel takvim.
* **Duyurular Panosu:** Kampüs ile ilgili anlık bilgilendirmeler.

---

## 🛠️ Kullanılan Teknolojiler

Bu proje tamamen **Python** ekosistemi üzerine kurulmuştur.

| Teknoloji | Kullanım Amacı |
| :--- | :--- |
| **Streamlit** | Web arayüzü, frontend ve session yönetimi. |
| **Sentence-Transformers** | (`all-MiniLM-L12-v2`) Metinleri vektöre çevirme ve yapay zeka işlemleri. |
| **Requests** | Hava durumu API'sinden canlı veri çekmek için. |
| **Regex (re)** | Kullanıcı girişi güvenlik kontrolleri için. |
| **Streamlit Components** | JavaScript kodları ile otomatik kaydırma (auto-scroll) özelliği için. |

---

## 💻 Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda test etmek için aşağıdaki adımları izleyin:

**1. Repoyu Klonlayın**
```bash
git clone [https://github.com/kullaniciadin/iku-kampus-asistani.git](https://github.com/kullaniciadin/iku-kampus-asistani.git)
cd iku-kampus-asistani

**Gerekli Kütüphaneleri Yükleyin:**
**pip install streamlit sentence-transformers requests**

**Uygulamayı Başlatın:**
**streamlit run app.py**

📂 Proje Yapısı

iku-kampus-asistani/
├── app.py              # Ana uygulama motoru (Frontend + Backend)
├── veritabani.json     # Yapay zeka eğitim veri seti (Sorular & Cevaplar)
├── requirements.txt    # Gerekli kütüphaneler listesi
└── README.md           # Proje dokümantasyonu

🧠 Nasıl Çalışır? (Teknik Detay)
Vektörleştirme: veritabani.json içindeki tüm sorular, uygulama başladığında @st.cache_resource sayesinde bir kez vektör uzayına çevrilir ve RAM'e kaydedilir.

Benzerlik Arama: Kullanıcı bir soru sorduğunda (Örn: "Servis kaçta?"), bu cümle de vektöre çevrilir ve veritabanındaki en yakın vektörle (Cosine Similarity) eşleştirilir.

Eşik Değeri (Threshold): Eğer benzerlik oranı %45'in altındaysa, bot "Bunu anlamadım" diyerek yanlış cevap vermekten kaçınır.

📷 Ekran Görüntüleri

<img width="1917" height="950" alt="image" src="https://github.com/user-attachments/assets/5e3031f7-bfd4-4667-91e5-626f98a45646" />

<img width="1525" height="749" alt="image" src="https://github.com/user-attachments/assets/22820f83-7807-4a65-8ba5-2d2af0a27f90" />

<img width="1551" height="423" alt="image" src="https://github.com/user-attachments/assets/35fb75db-e636-4d2c-8b75-910e7cd0077d" />





