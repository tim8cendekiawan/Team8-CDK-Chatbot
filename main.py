from openai import OpenAI
import tiktoken
import requests
import os
import streamlit as st

DEFAULT_API_KEY = "ca794fa8d9705ac719ae1011e88393e788239889bbc8b193f32d3bca596ee378"
DEFAULT_BASE_URL = "https://api.together.xyz/v1"
DEFAULT_MODEL = "meta-llama/Llama-Vision-Free"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500
DEFAULT_TOKEN_BUDGET = 4096

class ConversationManager:
    def __init__(self, api_key=None, base_url=None, model=None, temperature=None, max_tokens=None, token_budget=None):
        if not api_key:
            api_key = DEFAULT_API_KEY
        if not base_url:
            base_url = DEFAULT_BASE_URL
            
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        self.model = model if model else DEFAULT_MODEL
        self.temperature = temperature if temperature else DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens if max_tokens else DEFAULT_MAX_TOKENS
        self.token_budget = token_budget if token_budget else DEFAULT_TOKEN_BUDGET
        
        self.non_plant_topics = {
            'navigasi_lokasi': [
                'arah', 'lokasi', 'alamat', 'peta', 'navigasi', 'tersesat', 'mencari', 'dimana',
                'gedung', 'jalan', 'blok', 'area', 'tempat', 'rute', 'mall', 'toko', 'pasar',
                'koordinat', 'gps', 'kompas', 'petunjuk', 'persimpangan', 'pertigaan', 'perempatan',
                'rambu', 'landmark', 'bundaran', 'stasiun', 'terminal', 'bandara', 'pelabuhan'
            ],
            'kesehatan_medis': [
                'dokter', 'rumah sakit', 'klinik', 'obat', 'penyakit', 'gejala', 'diagnosa',
                'terapi', 'pengobatan', 'vaksin', 'virus', 'bakteri', 'infeksi', 'operasi',
                'psikolog', 'psikiater', 'mental', 'depresi', 'anxiety', 'stress', 'alergi',
                'imunisasi', 'rehabilitasi', 'trauma', 'terapi', 'konseling', 'kesehatan mental',
                'farmasi', 'apotek', 'resep', 'dosis', 'efek samping', 'pengobatan alternatif'
            ],
            'kecantikan_perawatan': [
                'skincare', 'makeup', 'kosmetik', 'perawatan', 'kecantikan', 'salon',
                'spa', 'facial', 'cream', 'lotion', 'serum', 'masker', 'scrub', 'peeling',
                'waxing', 'manicure', 'pedicure', 'massage', 'treatment', 'hair spa',
                'botox', 'filler', 'laser', 'anti aging', 'whitening', 'bleaching',
                'hair color', 'hair style', 'nail art', 'extension', 'microblading'
            ],
            'teknologi_komputer': [
                'komputer', 'laptop', 'smartphone', 'aplikasi', 'software', 'hardware',
                'internet', 'wifi', 'jaringan', 'program', 'coding', 'website', 'server',
                'database', 'cybersecurity', 'artificial intelligence', 'robot', 'cloud',
                'encryption', 'blockchain', 'cryptocurrency', 'bitcoin', 'mining', 'hosting',
                'domain', 'backup', 'firewall', 'antivirus', 'malware', 'hacking', 'bug',
                'debugging', 'virtual reality', 'augmented reality', 'machine learning'
            ],
            'pendidikan_akademik': [
                'sekolah', 'universitas', 'kuliah', 'pelajaran', 'ujian', 'guru',
                'dosen', 'mahasiswa', 'siswa', 'kurikulum', 'akademik', 'riset',
                'penelitian', 'laboratorium', 'perpustakaan', 'beasiswa', 'skripsi',
                'tesis', 'disertasi', 'seminar', 'workshop', 'pelatihan', 'sertifikasi',
                'akreditasi', 'ijazah', 'gelar', 'pendidikan', 'pembelajaran'
            ],
            'sosial_budaya': [
                'agama', 'budaya', 'adat', 'tradisi', 'upacara', 'ritual', 'festival',
                'bahasa', 'suku', 'etnis', 'komunitas', 'masyarakat', 'kepercayaan',
                'mitologi', 'legenda', 'cerita rakyat', 'kesenian', 'tarian', 'musik tradisional',
                'pakaian adat', 'makanan tradisional', 'pernikahan adat', 'norma', 'nilai',
                'kebiasaan', 'gotong royong', 'kearifan lokal', 'warisan budaya'
            ],
            'ekonomi_bisnis': [
                'bisnis', 'ekonomi', 'keuangan', 'investasi', 'saham', 'bank',
                'kredit', 'pinjaman', 'asuransi', 'pajak', 'startup', 'marketing',
                'perdagangan', 'ekspor', 'impor', 'valuta asing', 'obligasi', 'reksadana',
                'inflasi', 'deflasi', 'resesi', 'bursa efek', 'pasar modal', 'pasar uang',
                'manajemen', 'sdm', 'outsourcing', 'franchise', 'tender', 'lelang'
            ],
            'hiburan_olahraga': [
                'film', 'musik', 'konser', 'artis', 'selebriti', 'game', 'olahraga',
                'pertandingan', 'turnamen', 'kompetisi', 'festival', 'bioskop', 'teater',
                'drama', 'komedi', 'horor', 'action', 'adventure', 'anime', 'manga',
                'cosplay', 'streaming', 'podcast', 'radio', 'televisi', 'siaran langsung',
                'esports', 'betting', 'gambling', 'kasino', 'lotre', 'undian'
            ],
            'hewan_non_botani': [
                'anjing', 'kucing', 'burung', 'ikan', 'reptil', 'mamalia', 'serangga',
                'hewan peliharaan', 'hewan ternak', 'hewan liar', 'kebun binatang',
                'akuarium', 'kandang', 'pakan', 'grooming', 'breeding', 'veteriner',
                'adopsi hewan', 'konservasi', 'habitat', 'migrasi', 'hibernasi',
                'domestikasi', 'perilaku hewan', 'anatomi hewan', 'evolusi'
            ],
            'transportasi': [
                'mobil', 'motor', 'kereta', 'pesawat', 'kapal', 'bus', 'taksi',
                'transportasi', 'tiket', 'perjalanan', 'travel', 'ekspedisi', 'kargo',
                'pengiriman', 'freight', 'container', 'gudang', 'inventory', 'supply chain',
                'distribusi', 'pengangkutan', 'kurir', 'pos', 'tracking', 'resi'
            ],
            'properti_konstruksi': [
                'rumah', 'apartemen', 'gedung', 'konstruksi', 'arsitektur', 'desain',
                'interior', 'eksterior', 'renovasi', 'properti', 'real estate', 'developer',
                'kontraktor', 'material', 'bahan bangunan', 'struktur', 'fondasi',
                'instalasi', 'pemipaan', 'kelistrikan', 'tata ruang', 'perizinan',
                'IMB', 'sertifikat', 'agraria', 'zonasi', 'tata kota'
            ],
            'pemerintahan_politik': [
                'politik', 'pemerintah', 'negara', 'presiden', 'menteri', 'gubernur',
                'walikota', 'undang-undang', 'hukum', 'parlemen', 'pemilu'
            ],
            'keamanan_militer': [
                'polisi', 'tentara', 'militer', 'keamanan', 'pertahanan', 'senjata',
                'perang', 'konflik', 'intel', 'strategi', 'teroris', 'kriminal',
                'forensik', 'investigasi', 'pengawasan', 'patroli', 'intelijen',
                'spionase', 'sabotase', 'kontraterorisme', 'satuan khusus', 'latihan militer',
                'persenjataan', 'amunisi', 'bom', 'peluru', 'rudal', 'tank'
            ],
            'sains_non_botani': [
                'fisika', 'kimia', 'astronomi', 'geologi', 'matematika', 'statistik',
                'bintang', 'planet', 'galaksi', 'atom', 'molekul', 'energi', 'listrik',
                'magnet', 'gelombang', 'quantum', 'relativitas', 'meteorologi',
                'klimatologi', 'oseanografi', 'paleontologi', 'antropologi',
                'arkeologi', 'genetika', 'biokimia', 'mikrobiologi', 'virologi'
            ],
            'laut_perairan': [
                'laut', 'samudra', 'pantai', 'pelabuhan', 'nelayan', 'ikan', 'kapal',
                'terumbu karang', 'gelombang', 'tsunami', 'air laut'
            ],
            'sejarah_tokoh': [
                'sejarah', 'pahlawan', 'tokoh', 'peristiwa', 'masa lalu', 'museum',
                'artefak', 'dinasti', 'kerajaan', 'revolusi', 'peradaban'
            ],
             'media_komunikasi': [
                'jurnalisme', 'berita', 'media massa', 'pers', 'broadcasting',
                'telekomunikasi', 'telepon', 'email', 'chat', 'messaging',
                'social media', 'blog', 'vlog', 'influencer', 'content creator',
                'digital marketing', 'public relations', 'advertising', 'propaganda',
                'hoax', 'fact checking', 'censorship', 'privacy', 'data protection'
            ],
            'spiritualitas_paranormal': [
                'meditasi', 'yoga', 'chakra', 'aura', 'karma', 'reinkarnasi',
                'feng shui', 'tarot', 'zodiak', 'astrologi', 'horoskop', 'numerologi',
                'paranormal', 'psychic', 'medium', 'supernatural', 'ghost', 'hantu',
                'mistis', 'klenik', 'ritual', 'mantra', 'jimat', 'ramalan'
            ],
            'kriminalitas_hukum': [
                'kejahatan', 'pidana', 'perdata', 'pengadilan', 'hakim', 'jaksa',
                'pengacara', 'advokat', 'notaris', 'mediasi', 'arbitrase', 'litigasi',
                'gugatan', 'tuntutan', 'sanksi', 'denda', 'penjara', 'tahanan',
                'napi', 'korupsi', 'penipuan', 'pemalsuan', 'pencucian uang'
            ],
            'umum_lainnya': [
                'cuaca', 'iklim', 'berita', 'gosip', 'tren', 'viral', 'sensasi',
                'skandal', 'kontroversi', 'rumor', 'hoax', 'ramalan', 'zodiak',
                'astrologi', 'supernatural', 'mistis'
            ]
        }
        
        self.plant_terms = [
            'plant', 'flower', 'tree', 'leaf', 'root', 'seed', 'fruit', 'garden',
            'soil', 'grow', 'water', 'sunlight', 'fertilizer', 'prune', 'harvest',
            'vegetable', 'herb', 'cultivation', 'botany', 'botanical', 'species',
            'propagation', 'germination', 'pollination', 'nursery', 'greenhouse',
            'compost', 'organic', 'pesticide', 'weed', 'mulch', 'hydroponics',
            'perennial', 'annual', 'biennial', 'deciduous', 'evergreen', 'tropical',
            'native', 'exotic', 'hybrid', 'grafting', 'cutting', 'transplant'
        ]

        self.system_message = """You are a knowledgeable botanical expert and guide focused exclusively on plants and vegetation.
                                Your knowledge covers:
                                - Plant species and families
                                - Plant care and cultivation
                                - Plant biology and lifecycle
                                - Gardening techniques
                                - Plant identification
                                - Plant ecology and habitat
                                - Traditional plant uses for food and agriculture
                                - Sustainable farming practices
                                - Plant conservation
                                - Native and invasive species
                                - Plant genetics and breeding
                                - Soil science and management
                                - Plant nutrition and fertilization
                                - Irrigation and water management
                                - Greenhouse and nursery operations
                                - Landscape design with plants
                                - Urban gardening and agriculture
                                - Organic farming techniques
                                - Composting and soil improvement
                                - Plant propagation methods


                                Strict restrictions:
                                1. Only discuss plants and vegetation-related topics
                                2. Do not provide information about:
                                - Medicinal uses of plants
                                - Plants for skincare or cosmetics
                                - Illegal plants or substances
                                - Drug-related topics
                                - Harmful or toxic uses of plants
                                - Psychoactive properties of plants
                                - Traditional medicine or herbal remedies
                                - Beauty products derived from plants
                                - Plant-based pharmaceuticals
                                - Therapeutic applications of plants
                                - Poisonous or toxic effects
                                - Alternative medicine using plants
                                - Ethnobotanical drug use
                                - Plant-based supplements

                                If asked about restricted topics, politely redirect the conversation to safe, botanical aspects of plants. Always maintain a professional, educational focus on legitimate plant science and cultivation."""

        self.conversation_history = [{"role": "system", "content": self.system_message}]

    def count_tokens(self, text):
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)

    def total_tokens_used(self):
        try:
            return sum(self.count_tokens(message['content']) for message in self.conversation_history)
        except Exception as e:
            print(f"Error calculating total tokens used: {e}")
            return None
    
    def enforce_token_budget(self):
        try:
            while self.total_tokens_used() > self.token_budget:
                if len(self.conversation_history) <= 1:
                    break
                self.conversation_history.pop(1)
        except Exception as e:
            print(f"Error enforcing token budget: {e}")

    def is_plant_related(self, prompt):
        """
        Check if the user's prompt is related to allowed plant topics.
        Returns tuple (is_allowed, message)
        """
        restricted_keywords = [
            'medicine', 'drug', 'cure', 'healing', 'treatment',
            'skincare', 'cosmetic', 'beauty', 'pharmaceutical',
            'illegal', 'narcotic', 'psychedelic', 'hallucino'
        ]
        
        prompt_lower = prompt.lower()
        for keyword in restricted_keywords:
            if keyword in prompt_lower:
                return (False, "I apologize, but I can only discuss plants from a botanical and agricultural perspective. I cannot provide information about medicinal, cosmetic, or restricted uses of plants. Would you like to learn about the plant's natural characteristics, cultivation, or ecological role instead?")
        
        return (True, None)

    def chat_completion(self, prompt, temperature=None, max_tokens=None, model=None):
        is_allowed, message = self.is_plant_related(prompt)
        if not is_allowed:
            return message

        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        model = model if model is not None else self.model

        self.conversation_history.append({"role": "user", "content": prompt})
        self.enforce_token_budget()

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        return ai_response
    
    def reset_conversation_history(self):
        self.conversation_history = [{"role": "system", "content": self.system_message}]

def get_instance_id():
    """Retrieve the EC2 instance ID from AWS metadata using IMDSv2."""
    try:
        token = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=1
        ).text

        instance_id = requests.get(
            "http://169.254.169.254/latest/meta-data/instance-id",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=1
        ).text
        return instance_id
    except requests.exceptions.RequestException:
        return "Instance ID not available (running locally or error in retrieval)"

### Streamlit code ###
st.title("PlantPal")
st.markdown("""
    Welcome to the Botanical Assistant! I'm here to help you learn about plants and gardening.
    I can discuss:
    - Plant species and characteristics
    - Plant care and cultivation
    - Gardening techniques
    - Plant biology and ecology
    """)

# Display EC2 Instance ID
instance_id = get_instance_id()
st.write(f"**EC2 Instance ID**: {instance_id}")

# Initialize the ConversationManager object
if 'chat_manager' not in st.session_state:
    st.session_state['chat_manager'] = ConversationManager()

chat_manager = st.session_state['chat_manager']

# Sidebar options
st.sidebar.title("Options")

# Max Tokens Per Message slider
chat_manager.max_tokens = st.sidebar.slider("Max Tokens Per Message", 10, 500, int(chat_manager.max_tokens), 10)

# Temperature slider
chat_manager.temperature = st.sidebar.slider("Temperature", 0.0, 1.0, float(chat_manager.temperature), 0.01)

# Dropdown for System Message selection
system_message_option = st.sidebar.selectbox("System message", ["Default", "Custom"])

# Custom System Message input
if system_message_option == "Custom":
    custom_system_message = st.sidebar.text_area("Custom system message", value=chat_manager.system_message)
    if st.sidebar.button("Set custom system message"):
        chat_manager.system_message = custom_system_message
        st.success("Custom system message set successfully!")
        chat_manager.reset_conversation_history()

# Button to reset conversation history
if st.sidebar.button("Reset conversation history"):
    chat_manager.reset_conversation_history()
    st.success("Conversation history reset!")

# Chat input from the user
user_input = st.chat_input("Ask me about plants...")

# Call the chat manager to get a response from the AI
if user_input:
    response = chat_manager.chat_completion(user_input)
    if response:
        st.session_state['conversation_history'] = chat_manager.conversation_history

# Display the conversation history
for message in chat_manager.conversation_history:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])