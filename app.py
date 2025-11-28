import streamlit as st
import json
import os
import datetime
import random
import requests
import re
from sentence_transformers import SentenceTransformer, util
import streamlit.components.v1 as components

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="Kampüs Asistanı",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. GİRİŞ EKRANI (GÜVENLİK KONTROLLÜ) ---
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
    st.stop()# --- 3. STİL VE CSS (GARANTİLİ SABİT MENÜ) ---
st.markdown("""
<style>
    /* 1. Sohbet Balonları */
    .stChatMessage {border-radius: 15px; padding: 10px;}
    .stButton button {width: 100%; border-radius: 10px;}
    .stTable {width: 100% !important;}
    
    /* 2. Yan Menü Yazı Boyutları */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 20px !important;
        white-space: normal;
    }
    
    /* 3. KRİTİK DÜZELTME: Sütunların Eşit Uzamasını Engelle */
    /* Bu kod, sağdaki menünün soldaki sohbetle birlikte gereksiz uzamasını önler */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* 4. SAĞ MENÜYÜ SABİTLEME (STICKY) */
    /* Artık sütun kısa olduğu için sticky özelliği çalışacak */
    div[data-testid="column"]:nth-of-type(2) {
        position: sticky !important;
        top: 80px !important;     /* Tavandan boşluk */
        z-index: 1000 !important;
        
        /* Menünün belirgin olması için arka plan efekti */
        background-color: rgba(20, 20, 20, 0.8); /* Yarı saydam siyah */
        backdrop-filter: blur(10px); /* Buzlu cam efekti */
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1); /* İnce bir çerçeve */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); /* Gölgelendirme */
    }
</style>
""", unsafe_allow_html=True)
# --- 4. FONKSİYONLAR (CACHE VE HIZ) ---

@st.cache_resource
def kaynaklari_yukle():
    """Modeli ve Veritabanını hafızada tutar, hız kazandırır."""
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    dosya_konumu = os.path.dirname(os.path.abspath(__file__))
    json_yolu = os.path.join(dosya_konumu, 'veritabani.json')
    
    try:
        with open(json_yolu, 'r', encoding='utf-8') as file:
            data = json.load(file)
        sorular = []
        etiketler = []
        for intent in data["intents"]:
            for pattern in intent["patterns"]:
                sorular.append(pattern)
                etiketler.append(intent["tag"])
        soru_vektorleri = model.encode(sorular, convert_to_tensor=True)
        return model, data, soru_vektorleri, etiketler
    except FileNotFoundError:
        return None, None, None, None

model, veri, soru_vektorleri, soru_etiketleri = kaynaklari_yukle()

# HIZ AYARI: ttl=900 saniye (15 Dakika) boyunca hafızada tutar.
@st.cache_data(ttl=900)
def hava_durumu_getir():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=41.0082&longitude=28.9784&current_weather=true&timezone=auto"
        response = requests.get(url, timeout=1) # Timeout süresini kıstık
        data = response.json()
        sicaklik = data['current_weather']['temperature']
        durum_kodu = data['current_weather']['weathercode']
        
        durum_text = "Açık"
        if durum_kodu in [1, 2, 3]: durum_text = "Bulutlu"
        elif durum_kodu in [45, 48]: durum_text = "Sisli"
        elif durum_kodu in [51, 61, 80]: durum_text = "Yağmurlu"
        elif durum_kodu >= 95: durum_text = "Fırtınalı"
        return f"{sicaklik}°C", durum_text
    except:
        return "--°C", "Veri Yok"
    

    # YENİ: GERÇEK SERVİS SAATLERİ HESAPLAYICI
def sonraki_servisi_bul():
    simdi = datetime.datetime.now()
    
    # Görselden çıkarılan "Ataköy'den Kalkış" saatleri (Tüm güzergahlar birleştirildi)
    saatler_listesi = [
        "07:20", "08:00", "08:15", "08:30", "08:50", "09:00", "09:30", 
        "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", 
        "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "17:00", "18:05"
    ]
    
    for saat_str in saatler_listesi:
        saat, dakika = map(int, saat_str.split(":"))
        # Bugünün tarihiyle servis saatini birleştiriyoruz
        servis_vakti = simdi.replace(hour=saat, minute=dakika, second=0, microsecond=0)
        
        # Eğer servis saati şu andan ilerideyse, o servisi yakala
        if servis_vakti > simdi:
            fark = servis_vakti - simdi
            dakika_kaldi = int(fark.total_seconds() / 60)
            return f"{dakika_kaldi} dk", saat_str # (Örn: "12 dk", "14:30")
            
    return "Bitti", "Yarın" # Günün saatleri bittiyse

def en_yakin_cevabi_bul(kullanici_girdisi):
    if model is None: return "Veritabanı hatası.", None
    girdi_vektoru = model.encode(kullanici_girdisi, convert_to_tensor=True)
    skorlar = util.cos_sim(girdi_vektoru, soru_vektorleri)[0]
    
    if float(skorlar.max()) < 0.55:
        bilinmeyen_cevaplar = [
            "Bunu tam anlayamadım, tekrar eder misin?",
            "Şu an sadece okul, dersler ve etkinlikler hakkında bilgim var.",
            "Ne demek istediğini çözemedim 🤔"
        ]
        return random.choice(bilinmeyen_cevaplar), "bilinmiyor"
    
    bulunan_etiket = soru_etiketleri[int(skorlar.argmax())]
    for intent in veri["intents"]:
        if intent["tag"] == bulunan_etiket:
            return random.choice(intent["responses"]), bulunan_etiket
    return "Bir hata oluştu.", None

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
    
    # Servis Bilgisini Hesapla (Yukarıdaki fonksiyonu çağırıyoruz)
    kalan_sure, servis_saati = sonraki_servisi_bul()
    
    c1, c2 = st.columns(2)
    with c1: 
        st.metric("🌤️ Hava", sicaklik, durum)
    
    # DİNAMİK SERVİS SAYACI
    with c2: 
        if kalan_sure == "Bitti":
             st.metric("🚌 Servis", "Bitti", "Yarın 07:20")
        else:
             # Örn: 14:30 servisine 12 dk kaldı
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
tab1, tab2, tab3, tab4 = st.tabs(["💬 Asistan", "📅 Takvim", "📢 Duyurular", "🧮 Ort. Hesapla"])

# --- CHAT ---
with tab1:
    col1, col2 = st.columns([3, 1]) 
    with col1:
        if "mesajlar" not in st.session_state:
            ilk_mesajlar = [
                f"Merhaba {st.session_state['kullanici_adi']}! Sana nasıl yardımcı olabilirim?",
                f"Selam {st.session_state['kullanici_adi']}, bugün kampüste ne yapmak istersin?"
            ]
            st.session_state["mesajlar"] = [{"role": "assistant", "content": random.choice(ilk_mesajlar), "tag": "selamlasma"}]

        for mesaj in st.session_state["mesajlar"]:
            with st.chat_message(mesaj["role"], avatar="🤖" if mesaj["role"]=="assistant" else "👤"):
                st.write(mesaj["content"])
                
                # Görseller
                if mesaj.get("tag") == "ulasim_atakoy":
                    st.info("📍 **Ataköy Yerleşkesi**")
                    st.markdown("[🗺️ Haritada Aç](https://www.google.com/maps/search/?api=1&query=İstanbul+Kültür+Üniversitesi+Ataköy+Yerleşkesi)")
                    st.image("https://aday.iku.edu.tr/uploads/images/1753269823_2NOLn8kOFwupLzkY.jpeg", use_container_width=True)
                
                if mesaj.get("tag") == "ulasim_basin":
                    st.info("📍 **Basın Ekspres Yerleşkesi**")
                    st.markdown("[🗺️ Haritada Aç](https://www.google.com/maps/search/?api=1&query=İstanbul+Kültür+Üniversitesi+Basın+Ekspres+Yerleşkesi)")
                    st.image("https://aday.iku.edu.tr/uploads/images/1753258206_Yerle%C5%9Fke-Bas%C4%B1n.jpg", use_container_width=True)
                
                if mesaj.get("tag") == "yemekhane":
                    st.success("🍽️ **Günün Menüsü:**\n\n- Ezogelin Çorba\n- Püreli Köfte\n- Bulgur Pilavı\n- Mozaik Pasta")

        prompt = st.chat_input("Sorunu yaz...")
        
    with col2:
        st.markdown("### ⚡ Hızlı Menü")
        if st.button("🍔 Yemek Listesi"): prompt = "Yemekte ne var?"
        if st.button("🎉 Şenlikler"): prompt = "Bahar şenliği ne zaman?"
        if st.button("📚 Kütüphane"): prompt = "Kütüphane nerede?"
        if st.button("🚌 Ulaşım Bilgisi"): prompt = "Okula nasıl gidilir?"

    # --- BURAYI DEĞİŞTİRİYORUZ ---
    if prompt:
        if st.session_state["mesajlar"][-1]["content"] != prompt:
             st.session_state["mesajlar"].append({"role": "user", "content": prompt})
             
             with st.spinner('Yazıyor...'):
                 cevap, etiket = en_yakin_cevabi_bul(prompt)
             
             st.session_state["mesajlar"].append({"role": "assistant", "content": cevap, "tag": etiket})
             
             # OTO-SCROLL (JavaScript ile en alta odaklanma)
             components.html("""
                <script>
                    var elements = window.parent.document.querySelectorAll('.stChatMessage');
                    if (elements.length > 0) {
                        elements[elements.length - 1].scrollIntoView({behavior: "smooth", block: "end"});
                    }
                </script>
             """, height=0)
             
             st.rerun()

# --- TAKVİM (GERİ GELDİ!) ---
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

# --- DUYURULAR (GERİ GELDİ!) ---
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

# --- GPA HESAPLAMA (GERİ GELDİ!) ---
with tab4:
    st.header("🧮 Not Ortalaması Hesapla")
    if 'dersler' not in st.session_state: st.session_state.dersler = []

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: d_adi = st.text_input("Ders Adı", key="d_adi")
    with c2: d_kredi = st.number_input("Kredi", min_value=1, max_value=10, value=3, key="d_kredi")
    
    # DETAYLI NOT LİSTESİ
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