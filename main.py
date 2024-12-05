import streamlit as st
from streamlit_option_menu import option_menu
from chatbot import Chatbot
from rekomendasi import Rekomendasi
from deteksi import Deteksi
from generategambar import GenerateGambar
from conversation_manager import ConversationManager
from komponent import SidebarButton


def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def setup_sidebar():
    with st.sidebar:
        instance_id = get_instance_id()
        st.markdown(
                f"""
                <div style="
                    background-color: white; 
                    padding: 15px; 
                    border-radius: 10px; 
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); 
                    text-align: center; 
                    font-size: 14px; 
                    color: #333;
                    margin-bottom: 20px;">
                    <b>Instance ID:</b>
                    <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
                    {instance_id}
                </div>
                """,
                unsafe_allow_html=True,
            )
        selected = option_menu(
            "Menu Utama",
            ["Chatbot", "Rekomendasi", "Generate", "Deteksi"],
            icons=['chat', 'lightbulb', 'image', 'search'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "white"},
                "icons": {"color": "#00491e", "font-size": "30px"},
                "nav-link": {
                    "font-size": "16px",
                    "color": "#00491e",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#f0f0f0",
                },
                "nav-link-selected": {
                    "background-color": "#00491e",
                    "color": "white",
                    "border-radius": "5px",
                    "box-shadow": "0 0 10px rgba(0, 0, 0, 0.1)",
                },
                "menu-title": {
                    "font-size": "25px",
                    "color": "#00491e",
                    "font-weight": "bold",
                    "border-bottom": "2px solid #e0e0e0",
                },
            },
        )
        configure_settings()
    return selected


def configure_settings():
    if 'chat_manager' not in st.session_state:
        st.session_state['chat_manager'] = ConversationManager()

    chat_manager = st.session_state['chat_manager']

    if 'settings_visible' not in st.session_state:
        st.session_state['settings_visible'] = False

    if not st.session_state.settings_visible:
        if SidebarButton.create("Tampilkan Pengaturan"):
            st.session_state.settings_visible = True
            st.rerun()

    if st.session_state.settings_visible:
        chat_manager.max_tokens = st.sidebar.slider(
            "Max Tokens Per Message", 10, 500, int(chat_manager.max_tokens), 10
        )
        chat_manager.temperature = st.sidebar.slider(
            "Temperature", 0.0, 1.0, float(chat_manager.temperature), 0.01
        )

        if SidebarButton.create("Reset Conversation History"):
            chat_manager.reset_conversation_history()
            st.success("Conversation history reset!")

        if SidebarButton.create("Tutup Pengaturan"):
            st.session_state.settings_visible = False
            st.rerun()


def get_instance_id():
    try:
        import requests
        token = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=1,
        ).text
        instance_id = requests.get(
            "http://169.254.169.254/latest/meta-data/instance-id",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=1,
        ).text
        return instance_id
    except:
        return "Instance ID not available (running locally or error in retrieval)"


def show_default_page():
    st.title("🌱 Selamat Datang di PlantPal!")
    st.subheader("Yuk, Cari Tanaman yang Cocok Buat Kamu")
    st.markdown(
        """
        Selamat datang di **PlantPal**, tempat terbaik buat konsultasi tanaman!  
        Mau jadi ahli kebun atau cuma coba-coba aja, aplikasi ini bakal bantu kamu nemuin tanaman yang cocok sama tempat tinggal dan kebutuhan kamu 😊.
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🌟 Kenapa Pilih PlantPal?")
    st.write(
        """
        - 🌍 **Rekomendasi Berdasarkan Lokasi:** Cari tanaman yang cocok dengan lingkungan kamu.
        - 🔍 **Filter Sesuai Kebutuhan:** Pilih tanaman berdasarkan jenis, cara perawatan, dan lainnya.
        - 📸 **Deteksi Tanaman dari Gambar:** Upload gambar tanaman, dan kami bantu analisis jenisnya.
        - 🎨 **Lihat Gambar Tanaman:** Lihat tampilan tanaman yang direkomendasi langsung di aplikasi.
        - 🤝 **Tips dari Komunitas:** Dapatkan dan bagikan tips berkebun dari komunitas kita.
        """
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Mulai Sekarang", type="primary"):
            st.session_state["page"] = "Chatbot"

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Dibuat dengan ❤️ oleh Tim 8"
        "</div>",
        unsafe_allow_html=True,
    )


def main():
    local_css("./style.css")
    if 'chat_manager' not in st.session_state:
        st.session_state['chat_manager'] = ConversationManager()

    selected = setup_sidebar()

    if st.session_state.get('default_page', True) or not selected:
        st.session_state['default_page'] = False
        show_default_page()
    elif selected == "Chatbot":
        Chatbot()
    elif selected == "Rekomendasi":
        Rekomendasi()
    elif selected == "Deteksi":
        Deteksi()
    elif selected == "Generate":
        GenerateGambar()


if __name__ == "__main__":
    main()
