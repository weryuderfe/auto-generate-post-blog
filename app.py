import os
import google.generativeai as genai
import requests
import streamlit as st
from bs4 import BeautifulSoup
import json
import urllib.parse

# --- Fungsi Bing Image Search ---
def get_soup(url, header):
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

def bing_image_search(query, num_images=4, alt_base=None):
    try:
        query_str = '+'.join(query.split())
        url = f"http://www.bing.com/images/search?q={query_str}&FORM=HDRSC2"
        header = {'User-Agent': "Mozilla/5.0"}
        soup = get_soup(url, header)
        image_results_raw = soup.find_all("a", {"class": "iusc"})[:num_images]  # Ambil sesuai setting user
        image_html_list = []
        for idx, image_result_raw in enumerate(image_results_raw):
            m = json.loads(image_result_raw["m"])
            murl = m["murl"]
            mdesc = m.get("desc", "No description available")
            # SEO-friendly alt
            alt_text = f"{alt_base if alt_base else query} gambar {idx+1}"
            image_html_list.append(
                f'<div style="text-align: center; margin: 20px 0;">'
                f'<img src="{murl}" alt="{alt_text}" width="400" style="border: 2px solid black;">'
                f'<div style="font-size: 13px; color: gray;">{mdesc}</div>'
                f'</div>'
            )
        return image_html_list
    except Exception as e:
        return f"Error dalam pencarian gambar: {str(e)}"

# --- Fungsi validasi API Gemini ---
def validate_google_gemini_api_key(api_key):
    headers = {'Content-Type': 'application/json'}
    params = {'key': api_key}
    json_data = {'contents': [{'role': 'user', 'parts': [{'text': 'Give me five subcategories of jazz?'}]}]}
    response = requests.post(
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
        params=params, headers=headers, json=json_data
    )
    return response.status_code == 200

# --- Fungsi keyword suggestion ---
def get_keyword_suggestions(topic, api_key):
    prompt = f"""
                Buatkan 3 keyword dari judul \"{topic}\". tuliskan keyword secara langsung dengan format : keyword 1,keyword 2,keyword 3."""
    generation_config = {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    response = model.generate_content(prompt)
    return [keyword.strip() for keyword in response.text.split(',') if keyword.strip()]

# --- Streamlit App ---
st.set_page_config(layout='wide')

if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

st.title('Generate Artikel SEO dengan AI')
st.subheader("Buat Artikel SEO Berkualitas dengan Kemudahan AI")

with st.sidebar:
    st.title("Auto Generate Artikel")
    st.subheader('nidichy')
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
    topik_artikel = st.text_input('Topik Artikel', placeholder="Masukkan topik artikel di sini")
    # Setting jumlah gambar
    num_images = st.slider("Jumlah Gambar", min_value=1, max_value=8, value=4)
    if st.button('Get Keyword Suggestions'):
        if topik_artikel:
            with st.spinner('Mengambil saran kata kunci...'):
                keyword_suggestions = get_keyword_suggestions(topik_artikel, st.session_state.api_key)
                if keyword_suggestions:
                    st.session_state.keywords = st.multiselect(
                        'Pilih atau tambahkan kata kunci SEO', 
                        options=keyword_suggestions,
                        default=keyword_suggestions
                    )
                else:
                    st.error('Tidak dapat mengambil saran kata kunci.')
        else:
            st.error('Topik artikel belum diisi.')
    gaya_bahasa = st.radio("Gaya Bahasa",
                           ["Informatif", "Naratif", "Kasual","Formal","Kreatif"],
                           captions=["Memberikan informasi yang akurat dan bermanfaat kepada pembaca",
                                     "Menceritakan sebuah kisah yang menarik dan engaging bagi pembaca.",
                                     "Meyakinkan pembaca untuk mengambil tindakan tertentu, seperti membeli produk, mendaftar newsletter, atau mendukung suatu opini.",
                                     "Menciptakan suasana yang santai dan bersahabat dengan pembaca.",
                                     "Menyampaikan informasi yang serius dan kredibel kepada pembaca.",
                                     "Menyampaikan informasi dengan cara yang unik dan imajinatif."])
    num_len = st.slider("Jumlah Kata Artikel", min_value=500, max_value=2000, step=100, value=1000)
    if st.button('Generate Artikel'):
        if 'keywords' in st.session_state and topik_artikel:
            with st.spinner('Memproses artikel...'):
                keywords = ', '.join(st.session_state.keywords)
                prompt = f"""
                Anda adalah seorang spesialis SEO dengan pengalaman dalam membuat artikel SEO berkualitas. 
                Topik artikel ini adalah \"{topik_artikel}\". Kata kunci SEO yang harus digunakan dalam artikel ini adalah \"{keywords}\". 
                Tulis artikel blog dengan gaya penulisan {gaya_bahasa}. Artikel harus memiliki jumlah kata {num_len}. 
                Pastikan artikel ini relevan, informatif, dan sesuai dengan standar SEO untuk memaksimalkan visibilitas di mesin pencari.
                """
                generation_config = {
                    "temperature": 1.0,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
                }
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                )
                response = model.generate_content(prompt)
                article_content = response.text.strip()
                st.write("Artikel yang Dihasilkan:")
                # --- Gambar disisipkan sesuai paragraf jika lebih dari satu ---
                images_html = bing_image_search(topik_artikel, num_images=num_images, alt_base=topik_artikel)
                if not isinstance(images_html, list):
                    st.warning(images_html)
                    images_html = []
                # Pisahkan artikel jadi paragraf
                paragraphs = [p.strip() for p in article_content.split('\n') if p.strip()]
                num_paragraphs = len(paragraphs)
                img_idx = 0
                output_blocks = []
                if num_images == 1 or num_paragraphs == 0:
                    # Jika hanya satu gambar atau tidak ada paragraf, tampilkan gambar di awal
                    if images_html:
                        st.markdown(images_html[0], unsafe_allow_html=True)
                    for para in paragraphs:
                        st.write(para)
                else:
                    # Sisipkan gambar di antara paragraf secara merata
                    step = max(1, num_paragraphs // num_images)
                    para_with_img = set([i*step for i in range(num_images)])
                    for idx, para in enumerate(paragraphs):
                        st.write(para)
                        if img_idx < len(images_html) and idx in para_with_img:
                            st.markdown(images_html[img_idx], unsafe_allow_html=True)
                            img_idx += 1
                    # Jika masih ada gambar sisa, tampilkan di akhir
                    while img_idx < len(images_html):
                        st.markdown(images_html[img_idx], unsafe_allow_html=True)
                        img_idx += 1
                edited_content = st.text_area("Edit Artikel", article_content, height=300)
                st.download_button("Download Artikel", data=edited_content, file_name="artikel_seo.txt", mime="text/plain")
        else:
            st.error("Topik artikel atau kata kunci belum diisi.")
