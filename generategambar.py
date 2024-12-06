from conversation_manager import ConversationManager
import streamlit as st
from komponent import GeneralButton
import requests
from PIL import Image
import io
import base64
from conversation_manager import (
    DEFAULT_API_KEY, 
)

def GenerateGambar():
    st.title("Generate Tanaman 🖼️")
    st.write(
    """
    Masukkan **deskripsi tanaman** yang ingin kamu buat, seperti jenis, warna, atau suasana. 
    Kami akan menghasilkan ilustrasi tanaman yang detail, lengkap dengan karakteristik botani, 
    warna yang akurat, dan tekstur yang realistis! 🌿😊
    """
    )
    
    deskripsi_tanaman = st.text_input(
        "Masukkan deskripsi tanaman", 
        placeholder="Contoh: Bunga matahari segar di kebun musim semi"
    )
    
    if GeneralButton.create("Generate Gambar Tanaman"):
        if not deskripsi_tanaman:
            st.warning("Silakan masukkan deskripsi tanaman")
            return
        
        with st.spinner('Generating gambar...'):
            try:
                chat_manager = ConversationManager()
                translate_prompt = (
                    f"Translate the plant description '{deskripsi_tanaman}' to English, "
                    "using precise botanical or horticultural terminology. "
                    "Ensure the translation captures the specific type, characteristics, "
                    "and contextual details of the plant description."
                )
                english_description = chat_manager.chat_completion(translate_prompt).strip()

                english_description = english_description if english_description else deskripsi_tanaman
                
                payload = {
                    "model": "black-forest-labs/FLUX.1-schnell-Free",
                    "prompt": f"Ilustrasikan dengan detail gambar dari {english_description}, termasuk warna, bentuk, dan ukuran yang spesifik. Jika deskripsi tidak menggambarkan tanaman, tampilkan gambar hitam sebagai alternatif.",
                    "max_tokens": 256,
                    "width": 1024,
                    "height": 1024
                }
                
                response = requests.post(
                    "https://api.together.xyz/v1/images/generations", 
                    json=payload, 
                    headers={
                        "Authorization": f"Bearer {DEFAULT_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    for idx, img_data in enumerate(result.get('data', []), 1):
                        try:
                            img_url = img_data.get('url')
                            
                            if img_url:
                                img_response = requests.get(img_url)
                                img = Image.open(io.BytesIO(img_response.content))
                                
                                st.image(img)
                            else:
                                st.warning(f"Tidak ada URL gambar untuk gambar #{idx}")
                        
                        except Exception as img_error:
                            st.error(f"Gagal memproses gambar #{idx}: {str(img_error)}")
                
                else:
                    st.error(f"Gagal generate gambar (Kode status: {response.status_code})")
                    st.error(f"Detail error: {response.text}")
                
            except requests.RequestException as req_error:
                st.error(f"Kesalahan koneksi: {str(req_error)}")
            except Exception as e:
                st.error(f"Terjadi kesalahan tidak terduga: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
        
