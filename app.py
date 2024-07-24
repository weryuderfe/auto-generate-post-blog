import os
import google.generativeai as genai
import requests
import streamlit as st

# Validasi API Key Google Gemini
def validate_google_gemini_api_key(api_key):
    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        'key': api_key,
    }

    json_data = {
        'contents': [
            {
                'role': 'user',
                'parts': [
                    {
                        'text': 'Give me five subcategories of jazz?',
                    },
                ],
            },
        ],
    }

    response = requests.post(
        'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent',
        params=params,
        headers=headers,
        json=json_data,
    )
    return response.status_code == 200

# Set page config
st.set_page_config(layout='wide')

# Initialize session state for API key
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
st.title('Generate Artikel')
st.subheader("Buat Artikel Mudah dengan AI")
with st.sidebar:
    st.title("Auto Generate Artikel")
    st.subheader('by gudanginformatika.com')

    if not st.session_state.api_key_valid:
        api_key = st.text_input('Masukkan API Key Google Gemini Anda', type='password')
        if st.button('Validate API Key'):
            if validate_google_gemini_api_key(api_key):
                st.session_state.api_key_valid = True
                st.session_state.api_key = api_key
                st.success('API Key valid!')
            else:
                st.error('API Key tidak valid')
    
if st.session_state.api_key_valid:
    genai.configure(api_key=st.session_state.api_key)
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Tampilkan Form Generate Artikel
    judul_artikel = st.text_input('Judul Artikel')
    gaya_bahasa = st.radio("Gaya Bahasa",
                             ["Informatif", "Naratif", "Kasual","Formal","Kreatif"],
                             captions=["Memberikan informasi yang akurat dan bermanfaat kepada pembaca",
                                       "Menceritakan sebuah kisah yang menarik dan engaging bagi pembaca.",
                                       "Meyakinkan pembaca untuk mengambil tindakan tertentu, seperti membeli produk, mendaftar newsletter, atau mendukung suatu opini.",
                                       "Menciptakan suasana yang santai dan bersahabat dengan pembaca.",
                                       "Menyampaikan informasi yang serius dan kredibel kepada pembaca.",
                                       "Menyampaikan informasi dengan cara yang unik dan imajinatif."])
    num_len = st.slider("Length of Words", min_value=500, max_value=2000, step=100)

    input_prompt = f"""
    Anda adalah seorang SEO spesialis dengan pengalaman dalam membuat artikel SEO yang mudah diindeks mesin pencari dan menarik bagi pembaca. Tugas Anda adalah membuat artikel blog dengan judul artikel yang harus Anda buat adalah {judul_artikel}. Jika judul ini tidak berstandar SEO, modifikasi judulnya sesuai teknik SEO untuk memastikan optimalisasi mesin pencari. Selanjutnya, tulis artikel blog dengan judul yang telah diberikan. Gunakan gaya penulisan {gaya_bahasa} untuk memastikan daya tarik yang tinggi. Artikel harus memiliki jumlah kata {num_len}. Pastikan artikel relevan, informatif, dan sesuai dengan standar SEO untuk memaksimalkan visibilitas di mesin pencari.
    """

    if st.button('Generate Artikel'):
        response = model.generate_content(input_prompt)
        st.write(response.text)
