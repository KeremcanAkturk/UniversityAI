import streamlit as st
import streamlit.components.v1 as components
import os
import datetime
import random
import requests
import re
import sqlite3
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
import pandas as pd
import time

SABIT_API_KEY = "SİZİN API KEYİNİZ"
ADMIN_SIFRESI = "BEŞİKTAŞ"

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="Kampüs Asistanı AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GİRİŞ EKRANI ---
if "kullanici_adi" not in st.session_state:
    st.markdown("## 👋 Kampüs Asistanına Hoş Geldin!")
    st.info("Devam etmek için lütfen adını gir.")
    isim_girisi = st.text_input("Adınız:", placeholder="Örn: Hüseyin", max_chars=20)
    
    if st.button("Giriş Yap"):
        if not isim_girisi:
            st.warning("Lütfen bir isim yazın.")
        elif len(isim_girisi) < 2:
            st.warning("İsim çok kısa!")
        elif not re.match(r"^[a-zA-ZçğıöşüÇĞİÖŞÜ\s]+$", isim_girisi):
            st.error("⚠️ Sadece harf kullanabilirsiniz!")
        else:
            st.session_state["kullanici_adi"] = isim_girisi.strip().title()
            st.rerun()
    st.stop()

# --- 3. STİL VE CSS ---
st.markdown("""
<style>
    /* Sohbet Balonları */
    .stChatMessage {border-radius: 15px; padding: 10px;}
    .stButton button {width: 100%; border-radius: 10px;}
    .stTable {width: 100% !important;}
    
    /* Yan Menü Yazı Boyutları */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 20px !important;
        white-space: normal;
    }
    
    /* Sütunların Eşit Uzamasını Engelle */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* SAĞ MENÜYÜ SABİTLEME (STICKY) */
    div[data-testid="column"]:nth-of-type(2) {
        position: sticky !important;
        top: 80px !important;
        z-index: 1000 !important;
        background-color: rgba(20, 20, 20, 0.8);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)
@st.cache_resource
def kaynaklari_yukle():
    """Modeli ve SQLite veritabanını hazırlar."""
    # Vektör modeli (Embedding için)
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # Veritabanı Yolu
    db_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kampus.db')
    
    conn = sqlite3.connect(db_yolu, check_same_thread=False)
    cursor = conn.cursor()
    
    # Tabloyu Oluştur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sorular (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Etiket TEXT,
            SoruCumlesi TEXT,
            Cevap TEXT
        )
    ''')
    
    # Örnek Veri Kontrolü ve Ekleme
    cursor.execute("SELECT COUNT(*) FROM Sorular")
    if cursor.fetchone()[0] == 0:
        ilk_veriler = [
            ('selamlasma', 'Merhaba', 'Ben İKÜ Asistanı. Öğrencilere yardım etmek için buradayım.'),
            ('yemekhane', 'Yemekte ne var?', 'Yemekhanemiz Ataköy yerleşkesi B1 katındadır.\nMenü: Ezogelin Çorba, Püreli Köfte, Bulgur Pilavı.'),
            ('kutuphane', 'Kütüphane nerede?', 'Kütüphane Ataköy ana binada. Vize haftaları 7/24 açıktır.'),
            ('ulasim_atakoy', 'Okula nasıl gelirim?', 'Ataköy kampüsü E-5 kenarında. Yenibosna durağında inmen yeterli.'),
            ('wifi', 'Wifi şifresi', 'Eduroam ağına öğrenci numaran ve Orion şifrenle bağlanabilirsin.'),
            ('sinavlar', 'Sınavlar ne zaman?', 'Finaller 24 Aralık 2025 tarihinde başlıyor.')
        ]
        cursor.executemany("INSERT INTO Sorular (Etiket, SoruCumlesi, Cevap) VALUES (?, ?, ?)", ilk_veriler)
        conn.commit()
    
    # Verileri Çek
    cursor.execute("SELECT SoruCumlesi, Cevap FROM Sorular")
    rows = cursor.fetchall()
    
    bilgi_listesi = [row[1] for row in rows] 
    soru_kaliplari = [row[0] for row in rows] 
    
    # Soruları Vektöre Çevir
    soru_vektorleri = model.encode(soru_kaliplari, convert_to_tensor=True)
    
    # --- DÜZELTME BURADA ---
    # return satırı fonksiyonun hizasında (içeride) olmalı!
    return model, soru_vektorleri, soru_kaliplari, bilgi_listesi

# Fonksiyon çağrısı en solda (dışarıda) olmalı
model, soru_vektorleri, soru_kaliplari, bilgi_listesi = kaynaklari_yukle()
@st.cache_data(ttl=900)
def hava_durumu_getir():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=41.0082&longitude=28.9784&current_weather=true&timezone=auto"
        response = requests.get(url, timeout=1)
        data = response.json()
        sicaklik = data['current_weather']['temperature']
        return f"{sicaklik}°C", "Açık"
    except:
        return "--°C", "Veri Yok"

def sonraki_servisi_bul():
    simdi = datetime.datetime.now()
    # Ataköy Kalkış Saatleri
    saatler_listesi = [
        "07:20", "08:00", "08:15", "08:30", "08:50", "09:00", "09:30", 
        "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", 
        "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "17:00", "18:05"
    ]
    for saat_str in saatler_listesi:
        saat, dakika = map(int, saat_str.split(":"))
        servis_vakti = simdi.replace(hour=saat, minute=dakika, second=0, microsecond=0)
        if servis_vakti > simdi:
            fark = servis_vakti - simdi
            dakika_kaldi = int(fark.total_seconds() / 60)
            return f"{dakika_kaldi} dk", saat_str
    return "Bitti", "Yarın"


def yeni_veri_ekle(etiket, soru, cevap):
    db_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kampus.db')
    conn = sqlite3.connect(db_yolu, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO Sorular (Etiket, SoruCumlesi, Cevap) VALUES (?, ?, ?)", (etiket, soru, cevap))
    conn.commit()
    conn.close()
    
    # Cache'i temizle ki yeni veriler hemen yüklensin
    st.cache_resource.clear()




# --- 🧠 GEMINI API FONKSİYONU (SABİT KEY İLE) ---
def gemini_cevap_ver(kullanici_sorusu):
    # Dışarıdan api_key istemiyoruz, yukarıdaki SABIT_API_KEY'i kullanıyoruz.
    
    try:
        genai.configure(api_key=SABIT_API_KEY)
        
        # --- OTOMATİK MODEL BULUCU ---
        kullanilabilir_modeller = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    kullanilabilir_modeller.append(m.name)
        except:
            pass

        # Model Seçimi (Önce Pro, sonra Flash, sonra herhangi biri)
        secilen_model = None
        for m in kullanilabilir_modeller:
            if "gemini-1.5-pro" in m: # Önce güçlü modeli dene
                secilen_model = m
                break
        
        if not secilen_model:
             for m in kullanilabilir_modeller:
                if "flash" in m:
                    secilen_model = m
                    break
        
        if not secilen_model and kullanilabilir_modeller:
            secilen_model = kullanilabilir_modeller[0]

        if not secilen_model:
            return "❌ API Key hatası veya model bulunamadı. Key'i kontrol et.", "hata"

        gemini_n = genai.GenerativeModel(secilen_model)
        
        # Vektör Arama
        girdi_vektoru = model.encode(kullanici_sorusu, convert_to_tensor=True)
        skorlar = util.cos_sim(girdi_vektoru, soru_vektorleri)[0]
        ek_bilgi = ""
        if float(skorlar.max()) > 0.40:
            en_iyi_index = int(skorlar.argmax())
            ek_bilgi = f"\n[BİLGİ]: {bilgi_listesi[en_iyi_index]}"
        
        prompt = f"Soru: {kullanici_sorusu}\n{ek_bilgi}\nCevap:"
        response = gemini_n.generate_content(prompt)
        return response.text, "ai"

    except Exception as e:
        return f"Hata oluştu: {str(e)}", "hata"
    
# --- 5. YAN MENÜ ---
with st.sidebar:
    st.markdown("""
        <div style="background-color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <img src="https://images.seeklogo.com/logo-png/30/1/istanbul-kultur-universitesi-logo-png_seeklogo-307985.png" width="160" style="display: block; margin: 0 auto;">
        </div>
    """, unsafe_allow_html=True)
    
    kullanici_adi = st.session_state["kullanici_adi"]
    with st.container():
        st.markdown(f"""
        <div style="background-color: #262730; padding: 10px; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin:0; font-weight:bold;">👤 {kullanici_adi}</p>
            <p style="margin:0; font-size:12px; color: #aaa;">Öğrenci</p>
            <p style="margin:0; font-size:12px; color: #4CAF50;">● Çevrimiçi</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📡 Kampüs Durumu")
    sicaklik, durum = hava_durumu_getir()
    kalan_sure, servis_saati = sonraki_servisi_bul()
    
    c1, c2 = st.columns(2)
    with c1: st.metric("🌤️ Hava", sicaklik, durum)
    with c2: 
        if kalan_sure == "Bitti":
             st.metric("🚌 Servis", "Bitti", "Yarın 07:20")
        else:
             st.metric(f"🚌 Servis ({servis_saati})", f"{kalan_sure}", "Kalkıyor")

    st.markdown("---")
    anlik = datetime.datetime.now()
    st.write(f"📅 **Bugün:** {anlik.strftime('%d.%m.%Y')}")
    
    final_tarihi = datetime.datetime(2025, 6, 10) 
    kalan_gun = (final_tarihi - anlik).days
    if kalan_gun > 0:
        st.info(f"Finallere **{kalan_gun} gün** kaldı!")
        st.progress(min(100, max(0, 100 - kalan_gun)))
    else:
        st.success("Sınavlar Başladı!")

    st.markdown("---")
    st.markdown("### 🔗 Hızlı Erişim")
    col_link1, col_link2 = st.columns(2)
    with col_link1: st.link_button("SAP Orion", "https://orion.iku.edu.tr/")
    with col_link2: st.link_button("CATS", "https://cats.iku.edu.tr/")
    
    if st.button("Çıkış Yap"):
        del st.session_state["kullanici_adi"]
        st.rerun()

# --- 6. ANA EKRAN ---
st.title(f"🎓 Merhaba {st.session_state['kullanici_adi']}, Nasıl Yardımcı Olabilirim?")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 AI Asistan", "📅 Takvim", "📢 Duyurular", "🧮 GPA Hesapla", "📚 Veri Ekle"])
# --- TAB 1: AI CHAT (DÜZELTİLMİŞ AUTO-SCROLL) ---
with tab1:
    col1, col2 = st.columns([3, 1]) 
    with col1:
        # Mesaj geçmişini başlat
        if "mesajlar" not in st.session_state:
            st.session_state["mesajlar"] = [{"role": "assistant", "content": f"Merhaba {kullanici_adi}! Ben yapay zeka destekli asistanım. Bana her şeyi sorabilirsin."}]

        # Mesajları Ekrana Yazdır
        for mesaj in st.session_state["mesajlar"]:
            with st.chat_message(mesaj["role"], avatar="🤖" if mesaj["role"]=="assistant" else "👤"):
                st.write(mesaj["content"])

        # Kullanıcıdan Girdi Al
        prompt = st.chat_input("Bir şeyler sor (Örn: Servis kaçta?)...")
        
    with col2:
        st.markdown("### ⚡ Hızlı Menü")
        if st.button("🍔 Yemek Listesi"): prompt = "Yemekte ne var?"
        if st.button("🎉 Şenlikler"): prompt = "Bahar şenliği ne zaman?"
        if st.button("📚 Kütüphane"): prompt = "Kütüphane nerede?"
        if st.button("🚌 Ulaşım Bilgisi"): prompt = "Okula nasıl gidilir?"

    # Eğer bir prompt varsa (Butondan veya Inputtan)
    if prompt:
        # 1. Kullanıcı mesajını ekle
        st.session_state["mesajlar"].append({"role": "user", "content": prompt})
        st.rerun() # Sayfayı yenile ki mesaj hemen görünsün

    # Sayfa yenilendi, son mesaj kullanıcıdan ise AI cevap versin
    if st.session_state["mesajlar"][-1]["role"] == "user":
        with col1:
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Yazıyor..."):
                    # Fonksiyonu çağır (API Key artık otomatik alınıyor)
                    cevap, tag = gemini_cevap_ver(st.session_state["mesajlar"][-1]["content"])
                    st.write(cevap)
        
        # 2. AI cevabını ekle
        st.session_state["mesajlar"].append({"role": "assistant", "content": cevap})
        st.rerun() # Tekrar yenile ki cevap listeye girsin ve scroll çalışsın

    # --- KESİN ÇÖZÜM: OTO-SCROLL KODU ---
    # Bu kod her zaman çalışacak ve ekranı en son mesaja odaklayacak
    import streamlit.components.v1 as components
    components.html("""
    <script>
        function scrollAsagi() {
            var mesajlar = window.parent.document.querySelectorAll('.stChatMessage');
            if (mesajlar.length > 0) {
                // Son mesajı bul ve oraya kaydır
                mesajlar[mesajlar.length - 1].scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});
            }
        }
        // Sayfa yüklendikten 100 milisaniye sonra kaydır (Garanti olsun diye)
        setTimeout(scrollAsagi, 100);
    </script>
    """, height=0)
# --- TAB 2: TAKVİM (Önceki Detaylı Hali) ---
with tab2:
    st.subheader("📅 2025-2026 Güz Akademik Takvimi")
    col_takvim1, col_takvim2 = st.columns(2)
    
    with col_takvim1:
        st.info("🎓 **15 Eylül 2025**\n\n**Derslerin Başlangıcı**\nOkulların açıldığı ilk gün.")
        st.warning("🔄 **6 - 10 Ekim 2025**\n\n**Ders Ekleme-Bırakma Haftası**\nDers programında değişiklik yapmak için son hafta.")
        st.error("🚫 **17 - 21 Kasım 2025**\n\n**Dersten Çekilme Haftası**\nBaşarısız olacağını düşündüğün dersten çekilme tarihi.")
    
    with col_takvim2:
        st.success("🏁 **23 Aralık 2025**\n\n**Derslerin Bitişi**\nDönem sonu, son dersler.")
        st.error("📝 **24 Aralık 2025 - 7 Ocak 2026**\n\n**Final Sınavları**\nYarıyıl sonu sınav dönemi.")
        st.warning("♻️ **19 - 23 Ocak 2026**\n\n**Bütünleme Sınavları**\nFinallerde kalınan derslerin telafi sınavları.")

# --- TAB 3: DUYURULAR (Renkli Liste) ---
with tab3:
    st.header("📢 Güncel Duyurular")
    duyurular_listesi = [
        {"tip": "error",   "mesaj": "🚧 **Otopark:** İnşaat çalışmaları nedeniyle arka otopark geçici olarak kapatılmıştır."},
        {"tip": "success", "mesaj": "🌍 **Erasmus:** Yabancı dil sınav sonuçları açıklandı! Orion sistemi üzerinden kontrol edebilirsiniz."},
        {"tip": "info",    "mesaj": "📚 **Kütüphane:** Vize haftası sebebiyle kütüphane bu hafta 7/24 hizmet verecektir."},
        {"tip": "warning", "mesaj": "⚡ **Sistem Bakımı:** Bu gece 02:00 - 04:00 saatleri arasında sisteme erişim sağlanamayacaktır."},
        {"tip": "success", "mesaj": "💼 **Kariyer Günleri:** Çarşamba günü ana fuaye alanında 30 farklı şirket stant açacaktır."},
        {"tip": "error",   "mesaj": "⏳ **Burs Başvuruları:** Yemek bursu başvuruları için son gün Cuma saat 17:00!"},
        {"tip": "info",    "mesaj": "🎭 **Tiyatro Kulübü:** 'Lüküs Hayat' oyunu seçmeleri Salı günü yapılacaktır."},
        {"tip": "warning", "mesaj": "☂️ **Kayıp Eşya:** Danışmada mavi bir şemsiye bulunmaktadır."},
        {"tip": "success", "mesaj": "🚌 **Ring Servisleri:** Sınav döneminde servisler 15 dakikada bir kalkacaktır."}
    ]
    for duyuru in duyurular_listesi:
        if duyuru["tip"] == "error": st.error(duyuru["mesaj"])
        elif duyuru["tip"] == "success": st.success(duyuru["mesaj"])
        elif duyuru["tip"] == "warning": st.warning(duyuru["mesaj"])
        else: st.info(duyuru["mesaj"])

# --- TAB 4: GPA HESAPLAMA (Tam Liste) ---
with tab4:
    st.header("🧮 Not Ortalaması Hesapla")
    if 'dersler' not in st.session_state: st.session_state.dersler = []

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: d_adi = st.text_input("Ders Adı", key="d_adi")
    with c2: d_kredi = st.number_input("Kredi", min_value=1, max_value=10, value=3, key="d_kredi")
    
    with c3: d_not = st.selectbox("Harf Notu", 
                                  options=[
                                      ("A", 4.0), ("A-", 3.7), 
                                      ("B+", 3.3), ("B", 3.0), ("B-", 2.7),
                                      ("C+", 2.3), ("C", 2.0), ("C-", 1.7),
                                      ("D+", 1.3), ("D", 1.0), ("F", 0.0)
                                  ], 
                                  format_func=lambda x: x[0])

    if st.button("Listeye Ekle"):
        if d_adi:
            st.session_state.dersler.append({"Ders": d_adi, "Kredi": d_kredi, "Harf": d_not[0], "Puan": d_not[1]})
        else: st.warning("Lütfen ders adı gir.")

    if st.session_state.dersler:
        st.write("### Eklenen Dersler")
        st.table(st.session_state.dersler)
        toplam_puan = sum(d["Kredi"] * d["Puan"] for d in st.session_state.dersler)
        toplam_kredi = sum(d["Kredi"] for d in st.session_state.dersler)
        
        if toplam_kredi > 0:
            gno = toplam_puan / toplam_kredi
            st.metric(label="Genel Ortalama (GNO)", value=f"{gno:.2f}")
            if gno >= 3.0: st.balloons()
        
        if st.button("Temizle"):
            st.session_state.dersler = []
            st.rerun()
# --- TAB 5: SÜPER ADMİN PANELİ (EXCEL YÜKLEME + YÖNETİM) ---
with tab5:
    # 1. OTURUM KONTROLÜ
    if "admin_giris" not in st.session_state:
        st.session_state["admin_giris"] = False

    # A) GİRİŞ EKRANI
    if not st.session_state["admin_giris"]:
        st.markdown("### 🔒 Yönetici Girişi")
        c_pass, c_btn = st.columns([3, 1])
        with c_pass:
            girilen_sifre = st.text_input("Şifre", type="password", key="admin_pass", label_visibility="collapsed")
        with c_btn:
            if st.button("Giriş Yap", use_container_width=True):
                if girilen_sifre == ADMIN_SIFRESI:
                    st.session_state["admin_giris"] = True
                    st.rerun()
                else:
                    st.error("❌ Hatalı Şifre!")

    # B) YÖNETİM PANELİ
    else:
        # Üst Bar
        c1, c2 = st.columns([6, 1])
        with c1: st.success("🔓 Yönetici Paneli Açık")
        with c2: 
            if st.button("Çıkış"):
                st.session_state["admin_giris"] = False
                st.rerun()

        # --- SEKMELER: TEK EKLE vs TOPLU YÜKLE ---
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["✍️ Tek Veri Ekle", "📂 CSV ile Toplu Yükle", "🗑️ Veri Sil/Düzenle"])

        # --- 1. TEK VERİ EKLEME ---
        with admin_tab1:
            with st.form("tek_veri_form", clear_on_submit=True):
                yeni_etiket = st.text_input("Konu Etiketi", placeholder="Örn: akademik")
                yeni_soru = st.text_input("Soru", placeholder="Örn: Prof. Dr. Ahmet kimdir?")
                yeni_cevap = st.text_area("Cevap", placeholder="Bilgisayar Mühendisliği bölüm başkanıdır.")
                if st.form_submit_button("💾 Kaydet"):
                    yeni_veri_ekle(yeni_etiket, yeni_soru, yeni_cevap)
                    st.success("Eklendi!")
                    st.rerun()

       # --- 2. CSV İLE TOPLU YÜKLEME (SORUNSUZ VERSİYON) ---
        with admin_tab2:
            st.info("💡 CSV dosyası yükleyerek toplu veri girişi yapabilirsiniz.")
            
            # Artık CSV dosyası istiyoruz
            uploaded_file = st.file_uploader("CSV Dosyasını Sürükleyin", type=['csv'])
            
            if uploaded_file is not None:
                try:
                    # read_excel yerine read_csv kullanıyoruz (Ekstra kütüphane istemez)
                    df_excel = pd.read_csv(uploaded_file)
                    
                    st.dataframe(df_excel.head()) 
                    
                    if st.button(f"🚀 {len(df_excel)} Adet Veriyi Yükle"):
                        bar = st.progress(0)
                        db_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kampus.db')
                        conn = sqlite3.connect(db_yolu)
                        cursor = conn.cursor()
                        
                        for index, row in df_excel.iterrows():
                            cursor.execute("INSERT INTO Sorular (Etiket, SoruCumlesi, Cevap) VALUES (?, ?, ?)", 
                                         (str(row['Etiket']), str(row['Soru']), str(row['Cevap'])))
                            bar.progress((index + 1) / len(df_excel))
                            
                        conn.commit()
                        conn.close()
                        st.cache_resource.clear()
                        st.success("✅ Veriler yüklendi!")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"Hata: {e}")
        # --- 3. VERİ SİLME ---
        with admin_tab3:
            db_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kampus.db')
            conn = sqlite3.connect(db_yolu)
            df = pd.read_sql_query("SELECT ID, Etiket, SoruCumlesi FROM Sorular ORDER BY ID DESC", conn)
            conn.close()

            if not df.empty:
                sil_id = st.selectbox("Silinecek Veri", df['ID'].tolist(), format_func=lambda x: f"{x} - {df[df['ID']==x]['SoruCumlesi'].values[0]}")
                if st.button("🗑️ Seçiliyi Sil"):
                    conn = sqlite3.connect(db_yolu)
                    conn.cursor().execute("DELETE FROM Sorular WHERE ID=?", (sil_id,))
                    conn.commit()
                    conn.close()
                    st.cache_resource.clear()
                    st.rerun()
            
            # Tüm tabloyu göster
            conn = sqlite3.connect(db_yolu)
            st.dataframe(pd.read_sql_query("SELECT * FROM Sorular", conn), use_container_width=True)

            conn.close()
