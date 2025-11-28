🎓 İKÜ Kampüs Asistanı (v1.0)
İstanbul Kültür Üniversitesi (İKÜ) öğrencileri için geliştirilmiş; yapay zeka destekli, gerçek zamanlı veriler sunan ve kampüs hayatını kolaylaştıran interaktif bir web asistanıdır.

🚀 Proje Hakkında
Öğrencilerin dağınık bilgiler (servis saatleri, yemek listesi, akademik takvim vb.) arasında kaybolmasını önlemek amacıyla geliştirilmiştir. Doğal Dil İşleme (NLP) teknolojisi kullanan bu asistan, soruları anlar ve en doğru cevabı verir.

✨ Temel Özellikler
🤖 Yapay Zeka Sohbet Botu: sentence-transformers ve Vektör Benzerliği (Cosine Similarity) kullanarak kullanıcı sorularını anlar. Sabit cevaplar yerine rastgele varyasyonlarla doğal bir sohbet deneyimi sunar.

🚌 Akıllı Ring Servisi Sayacı: Statik bir liste yerine, anlık saate göre bir sonraki servisin kalkmasına kaç dakika kaldığını otomatik hesaplar.

🌤️ Canlı Hava Durumu: Open-Meteo API entegrasyonu ile kampüs bölgesinin hava durumunu anlık gösterir (15 dk önbellekleme ile donma yapmaz).

🔐 Güvenli Giriş Sistemi: Regex tabanlı isim doğrulama ve oturum (session) yönetimi içerir.

🎨 Modern UI/UX:

Sticky Sidebar: Sayfa kaydırılsa bile menü sabit kalır.

Auto-Scroll: Mesaj yazıldığında sayfa otomatik odaklanır.

Karanlık Mod & Glassmorphism: Şık ve göz yormayan tasarım.

🧮 Öğrenci Araçları:

+/- Sistemine uygun GPA (Ortalama) Hesaplama.

Güncel Akademik Takvim.

Duyurular Panosu.

🛠️ Kullanılan Teknolojiler
Bu proje tamamen Python dili ile geliştirilmiştir.

Teknoloji,Amaç
<img width="507" height="124" alt="image" src="https://github.com/user-attachments/assets/ebdf1d8f-61d8-4597-83c2-2a6da4e10ac3" />

💻 Kurulum ve Çalıştırma
Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

Repoyu Klonlayın:
**git clone https://github.com/kullaniciadin/iku-kampus-asistani.git**
**cd iku-kampus-asistani**

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





