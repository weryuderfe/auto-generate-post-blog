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
    st.title('Generate Artikel')
    st.subheader("Isi Url dibawah untuk generate")
    url_blog = st.text_input('Alamat Blog anda (http:// atau https://)')
    url_artikel_1 = st.text_input('Link Artikel referensi 1')
    url_artikel_2 = st.text_input('Link Artikel referensi 2')
    url_artikel_3 = st.text_input('Link Artikel referensi 3')
    num_len = st.slider("Length of Words", min_value=250, max_value=1000, step=250)

    input_prompt = [
        f"anda adalah seorang seo spesialis, anda sudah berpengalaman dalam membuat artikel seo yang gampang di index mesin pencarian. hasil penulisan anda memiliki daya tarik yang tinggi untuk setiap pembaca. saya ingin anda membantu saya untuk membantu saya dalam membuat artikel di blog saya yang beralamat di gudanginformatika.com, blog saya berfokus pada niche atau topik teknologi, gadget. nantinya saya akan memberikan link artikel sebagai referensi anda untuk menulis artikel blog. tugas anda adalah membuat judul yang di modifikasi sesuai teknik seo judul tidak boleh sama dengan judul artikel yang menjadi referensi, selanjutnya anda menuliskan artikel blog dengan referensi link yang saya berikan. usahakan tidak sama agar tidak terindikasi artikel plagiat dan link asli tidak di tampilkan. artikel harus \"{num_len} kata. Link 1 :\"{url_artikel_1}\"Link 2 :\"{url_artikel_2}\"Link 3 :\"{url_artikel_3}\". buatkan juga inbound link di awal isi artikel \"{url_blog}\"- [teruskan isi artikel]"
    ]

    if st.button('Generate Blog'):
        response = model.generate_content(input_prompt)
        st.write(response.text)
