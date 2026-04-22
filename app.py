
import streamlit as st

from audio_recorder_streamlit import audio_recorder

import speech_recognition as sr

import re

from difflib import SequenceMatcher



# --- KONFIGURASI HALAMAN ---

st.set_page_config(page_title="Maharah Kalam Quiz", page_icon="🎙️")



st.title("🎙️ Maharah Kalam Quiz")

st.write("Silakan jawab pertanyaan di bawah ini menggunakan Bahasa Arab melalui lisan (kalam).")



# --- FUNGSI PENGUKUR KEMIRIPAN ---

def hitung_kemiripan(a, b):

    return SequenceMatcher(None, a, b).ratio()



# --- FUNGSI NORMALISASI ---

def normalisasi_kalam(text):

    if not text: return ""

    angka_map = {"1":"واحد", "2":"اثnan", "3":"ثلاثة", "4":"اربعة", "5":"خمسة",

                 "١":"واحد", "٢":"اثنان", "٣":"ثلاثة", "٤":"اربعة", "٥":"خمسة"}

    for num, txt in angka_map.items():

        text = text.replace(num, txt)

    text = re.sub(r'[\u064B-\u0652]', '', text)

    text = re.sub(r'[أإآءؤئ]', 'ا', text)

    text = re.sub(r'ة', 'ه', text)

    text = re.sub(r'ى', 'ي', text)

    text = re.sub(r'\bال', '', text) 

    text = text.replace(" ال", " ")

    text = re.sub(r'[^\u0621-\u064A]', '', text)

    return text



# --- DATA SOAL ---

if 'current_question' not in st.session_state:

    st.session_state.current_question = 0

    st.session_state.scores = {}



questions = [

    {"soal": "Sebutkan Bahasa Arab dari 'Sekolah'?", "kunci": "مدرسة"},

    {"soal": "Apa Bahasa Arabnya 'Saya seorang siswa'?", "kunci": "أنا طالب"},

    {"soal": "Apa Bahasa Arab dari 'Buku'!", "kunci": "كتاب"},

    {"soal": "Apa Bahasa Arab dari 'Selamat Pagi'?", "kunci": "صباح الخير"},

    {"soal": "Terjemahkan ke Bahasa Arab: 'Di mana rumahmu?'", "kunci": "أين بيتك"},

    {"soal": "Sebutkan Bahasa Arab dari kata 'Membaca'!", "kunci": "قرأ"},

    {"soal": "Bahasa Arabkanlah kalimat: 'Saya pergi ke Masjid'", "kunci": "أذهب إلى المسجد"},

    {"soal": "Apa bahasa Arabnya 'Papan Tulis'?", "kunci": "سبورة"},

    {"soal": "Sebutkan angka 1-5 dalam bahasa Arab!", "kunci": "واحد اثنان ثلاثة اربعة خمسة"},

    {"soal": "Apa jawaban dari lafadz ini : 'كيف حالك؟'", "kunci": "أنا بخير"}

]



# --- LOGIKA KUIS ---

if st.session_state.current_question < len(questions):

    q_idx = st.session_state.current_question

    st.divider()

    st.info(f"**Soal {q_idx + 1} dari 10**")

    st.subheader(questions[q_idx]['soal'])

    

    is_answered = q_idx in st.session_state.scores



    audio_bytes = audio_recorder(

        text="Klik untuk Bicara" if not is_answered else "Sudah Terjawab",

        recording_color="#e8b62c",

        neutral_color="#6aa36f" if not is_answered else "#808080",

        icon_size="3x",

        key=f"audio_student_v2_{q_idx}"

    )



    if audio_bytes and not is_answered:

        with open("temp_audio.wav", "wb") as f:

            f.write(audio_bytes)

        

        r = sr.Recognizer()

        with sr.AudioFile("temp_audio.wav") as source:

            audio_data = r.record(source)

            try:

                # Proses di balik layar tetap mendeteksi teks

                text_result = r.recognize_google(audio_data, language="ar-SA").strip()

                

                hasil_ai = normalisasi_kalam(text_result)

                kunci_jawaban = normalisasi_kalam(questions[q_idx]['kunci'])

                kemiripan = hitung_kemiripan(hasil_ai, kunci_jawaban)

                

                # Penilaian (Hasil Suara tidak ditampilkan lagi)

                if kemiripan >= 0.7:

                    st.success("✅ Jawabanmu Benar!")

                    st.session_state.scores[q_idx] = 10

                else:

                    st.error("⚠️ Jawabanmu Belum Tepat.")

                    st.session_state.scores[q_idx] = 0

                

                # Tampilkan kunci jawaban sebagai referensi belajar

                st.info(f"Kunci Jawaban: **{questions[q_idx]['kunci']}**")

                

            except:

                st.warning("⚠️ Suara tidak terdeteksi dengan jelas. Silakan klik mic dan ulangi pengucapanmu.")



    if is_answered:

        st.info(f"Kunci Jawaban: **{questions[q_idx]['kunci']}**")

        if st.button("Lanjut ke Soal Berikutnya ➡️"):

            st.session_state.current_question += 1

            st.rerun()

    elif q_idx in st.session_state.scores:

        st.button("Lanjut ke Soal Berikutnya ➡️", on_click=lambda: setattr(st.session_state, 'current_question', q_idx + 1))



else:

    # --- HASIL AKHIR ---

    st.balloons()

    st.success("🎉 Alhamdulillah, Tes Selesai!")

    total_skor = sum(st.session_state.scores.values())

    st.metric(label="Skor Akhir Siswa", value=f"{total_skor} / 100")

    

    with st.expander("Lihat Detail Hasil"):

        for i, q in enumerate(questions):

            skor = st.session_state.scores.get(i, 0)

            st.write(f"{'✅' if skor > 0 else '❌'} Soal {i+1}: {q['kunci']}")



    if st.button("Ulangi Tes 🔄"):

        st.session_state.current_question = 0

        st.session_state.scores = {}

        st.rerun()

