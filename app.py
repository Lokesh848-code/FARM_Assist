import streamlit as st
import requests
import json
import os
import urllib.parse
from dotenv import load_dotenv
from retriever import FarmingRetriever

# Load environment variables at startup
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Farmer Assist - Smart RAG Farming Advisor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Rich Aesthetics: Forest Green, Amber Gold, & Creamy Soft Earthy Background)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Overall Font & Background */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background-color: #F4F6F3; /* Ultra premium light grayish-green */
    }

    /* Main Container Title */
    .header-card {
        background: linear-gradient(135deg, #1E4D2B, #0F2F19);
        padding: 25px 20px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(30, 77, 43, 0.15);
        text-align: center;
        border-bottom: 4px solid #FFC107;
    }
    
    .header-card h1 {
        margin: 0;
        font-size: 2.6rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .header-card p {
        margin: 5px 0 0 0;
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.9;
    }

    /* Crop Selector Section */
    .section-title {
        color: #1E4D2B;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-left: 4px solid #FFC107;
        padding-left: 10px;
    }

    /* Dashboard Info Cards */
    .dash-card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border-top: 4px solid #1E4D2B;
        height: 100%;
        transition: all 0.2s ease;
    }
    
    .dash-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(30, 77, 43, 0.08);
    }
    
    .dash-card h4 {
        color: #1E4D2B;
        margin: 0 0 10px 0;
        font-weight: 600;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .dash-card p {
        margin: 0;
        font-size: 0.88rem;
        color: #4A5568;
        line-height: 1.45;
        white-space: pre-wrap;
    }

    /* Override Streamlit Buttons to look like Visual Crop Cards */
    button[kind="secondary"] {
        background-color: white !important;
        color: #1E4D2B !important;
        border: 1px solid #D1FAE5 !important;
        padding: 12px 10px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: #ECFDF5 !important;
        border-color: #34D399 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(16, 185, 129, 0.1) !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #10B981, #059669) !important;
        color: white !important;
        border: none !important;
        padding: 12px 10px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        box-shadow: 0 6px 12px rgba(16, 185, 129, 0.25) !important;
    }

    /* Native Chat Message Enhancements */
    [data-testid="stChatMessage"] {
        border-radius: 14px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
        border: 1px solid #EAEAEA !important;
    }
    
    [data-testid="stChatMessageUser"] {
        background-color: #E8F5E9 !important; /* Soft light green */
        border-left: 5px solid #2E7D32 !important;
    }
    
    [data-testid="stChatMessageAssistant"] {
        background-color: #FFFDE7 !important; /* Soft warm yellow */
        border-left: 5px solid #FBC02D !important;
    }

    /* Clean Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #142118 !important; /* Premium dark forest */
        color: #F4FBF7 !important;
    }
    
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
    }

    .footer {
        text-align: center;
        padding: 20px;
        font-size: 0.85rem;
        color: #718096;
        margin-top: 30px;
        border-top: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Localization helper
LANGUAGES = {
    "English": {
        "title": "🌾 Farmer Assist",
        "subtitle": "Smart Agricultural RAG Dashboard & Advisor",
        "credentials_missing": "⚠️ Missing environment variables. Please copy `.env.example` to `.env` and fill in your WATSONX_API_KEY and WATSONX_PROJECT_ID, or configure them under Developer Settings.",
        "input_placeholder": "Ask anything else (e.g., 'Suggest weather actions', 'Mandi advice')...",
        "btn_clear": "🧹 Clear Chat",
        "sidebar_header": "Developer & API Config",
        "api_key_lbl": "IBM Cloud API Key",
        "project_id_lbl": "watsonx.ai Project ID",
        "region_lbl": "watsonx.ai Region URL",
        "model_lbl": "LLM Model ID",
        "temp_lbl": "Temperature",
        "tokens_lbl": "Max Tokens",
        "retrieved_sources": "🔍 RAG Context Sources",
        "source_score": "Confidence Score",
        "quick_questions": "💡 Suggested Questions",
        "thinking": "Consulting watsonx.ai...",
        "select_crop": "🌱 Select standing crop to view dashboard:",
        "soil_title": "🧪 Soil & Climate Suitability",
        "pest_title": "🐛 Pest & Disease Control",
        "mandi_title": "💰 Mandi Market Price",
        "irrigation_title": "💧 Irrigation Guidance",
        "chat_header": "💬 Ask Farmer Assist Advisor",
        "context_label": "Query context linked to crop: "
    },
    "Hindi": {
        "title": "🌾 किसान सहायता",
        "subtitle": "स्मार्ट कृषि डैशबोर्ड और सलाहकार (RAG)",
        "credentials_missing": "⚠️ क्रेडेंशियल गायब हैं। कृपया `.env.example` को `.env` में कॉपी करें और WATSONX_API_KEY और WATSONX_PROJECT_ID भरें, या डेवलपर सेटिंग्स में कॉन्फ़िगर करें।",
        "input_placeholder": "कुछ भी और पूछें (जैसे: 'मौसम सलाह', 'मंडी सुझाव')...",
        "btn_clear": "🧹 चैट साफ करें",
        "sidebar_header": "डेवलपर और API सेटिंग्स",
        "api_key_lbl": "IBM क्लाउड API कुंजी",
        "project_id_lbl": "watsonx.ai प्रोजेक्ट ID",
        "region_lbl": "watsonx.ai क्षेत्र URL",
        "model_lbl": "LLM मॉडल ID",
        "temp_lbl": "तापमान",
        "tokens_lbl": "अधिकतम टोकन",
        "retrieved_sources": "🔍 पुनर्प्राप्त ज्ञान संदर्भ",
        "source_score": "विश्वास स्कोर",
        "quick_questions": "💡 सुझाए गए प्रश्न",
        "thinking": "watsonx.ai से परामर्श लिया जा रहा है...",
        "select_crop": "🌱 डैशबोर्ड देखने के लिए फसल चुनें:",
        "soil_title": "🧪 मिट्टी और जलवायु उपयुक्तता",
        "pest_title": "🐛 कीट और रोग नियंत्रण",
        "mandi_title": "💰 मंडी बाजार भाव",
        "irrigation_title": "💧 सिंचाई मार्गदर्शन",
        "chat_header": "💬 किसान सहायता सलाहकार से पूछें",
        "context_label": "संबद्ध फसल संदर्भ: "
    }
}

# Clean Sidebar: Basic user options at the top
st.sidebar.markdown("## ⚙️ Main Options")
lang_choice = st.sidebar.selectbox("Language / भाषा", ["English", "Hindi"])
text_map = LANGUAGES[lang_choice]

# Load default config from environment variables
env_api_key = os.getenv("WATSONX_API_KEY", "")
env_project_id = os.getenv("WATSONX_PROJECT_ID", "")
env_region_url = os.getenv("WATSONX_REGION_URL", "https://us-south.ml.cloud.ibm.com")
env_model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-4-h-small")

# Clean technical credentials inside a single expander
st.sidebar.markdown("---")
with st.sidebar.expander(f"🛠  {text_map['sidebar_header']}", expanded=False):
    api_key_input = st.text_input(
        text_map['api_key_lbl'], 
        value=st.session_state.get("ibm_api_key", env_api_key), 
        type="password"
    )
    project_id_input = st.text_input(
        text_map['project_id_lbl'], 
        value=st.session_state.get("watsonx_project_id", env_project_id)
    )
    region_url_input = st.text_input(
        text_map['region_lbl'],
        value=st.session_state.get("watsonx_region_url", env_region_url)
    )
    model_id_input = st.text_input(
        text_map['model_lbl'],
        value=st.session_state.get("watsonx_model_id", env_model_id)
    )
    temperature = st.slider(text_map['temp_lbl'], min_value=0.0, max_value=1.0, value=0.3, step=0.05)
    max_tokens = st.slider(text_map['tokens_lbl'], min_value=50, max_value=2000, value=600, step=50)

# Save active configurations in session state
st.session_state["ibm_api_key"] = api_key_input
st.session_state["watsonx_project_id"] = project_id_input
st.session_state["watsonx_region_url"] = region_url_input
st.session_state["watsonx_model_id"] = model_id_input

# Extract active values
active_api_key = st.session_state["ibm_api_key"]
active_project_id = st.session_state["watsonx_project_id"]
active_region_url = st.session_state["watsonx_region_url"]
active_model_id = st.session_state["watsonx_model_id"]

# Extract region subdomain (e.g. "us-south") from URL
region_subdomain = "us-south"
if active_region_url:
    clean_url = active_region_url.replace("https://", "").replace("http://", "")
    parts = clean_url.split(".")
    if parts:
        region_subdomain = parts[0]

# Initialize retriever
@st.cache_resource
def get_retriever():
    return FarmingRetriever("master_farming_dataset.txt")

retriever = get_retriever()

# Helper function to get watsonx IAM token
def get_watsonx_token(api_key_str):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key_str
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# Helper function to call watsonx text generation REST API
def call_watsonx_generation(prompt, token, proj_id, model, temp, max_tok, reg_sub):
    url = f"https://{reg_sub}.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    decoding_method = "sample" if temp > 0.0 else "greedy"
    parameters = {
        "decoding_method": decoding_method,
        "max_new_tokens": max_tok,
        "min_new_tokens": 1,
        "repetition_penalty": 1.15
    }
    if decoding_method == "sample":
        parameters["temperature"] = temp
        
    body = {
        "input": prompt,
        "parameters": parameters,
        "model_id": model,
        "project_id": proj_id
    }
    
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()["results"][0]["generated_text"]

# Main Header
st.markdown(f"""
<div class="header-card">
    <h1>{text_map['title']}</h1>
    <p>{text_map['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# Select crop logic
if "selected_crop" not in st.session_state:
    st.session_state.selected_crop = "Rice"

active_crop = st.session_state.selected_crop

# Crop selector horizontal tabs
st.markdown(f"<div class='section-title'>{text_map['select_crop']}</div>", unsafe_allow_html=True)

crop_list = [
    {"name": "Rice", "emoji": "🌾", "hindi": "धान"},
    {"name": "Maize", "emoji": "🌽", "hindi": "मक्का"},
    {"name": "Cotton", "emoji": "🧶", "hindi": "कपास"},
    {"name": "Mango", "emoji": "🥭", "hindi": "आम"},
    {"name": "Apple", "emoji": "🍎", "hindi": "सेब"},
    {"name": "Coconut", "emoji": "🥥", "hindi": "नारियल"}
]

col_c1, col_c2, col_c3, col_c4, col_c5, col_c6 = st.columns(6)
cols = [col_c1, col_c2, col_c3, col_c4, col_c5, col_c6]

for idx, crop in enumerate(crop_list):
    with cols[idx]:
        is_active = active_crop == crop["name"]
        btn_type = "primary" if is_active else "secondary"
        btn_label = f"{crop['emoji']} {crop['name']} ({crop['hindi']})"
        if st.button(btn_label, key=f"btn_crop_{crop['name']}", type=btn_type, use_container_width=True):
            st.session_state.selected_crop = crop["name"]
            st.rerun()

# ----------------- DYNAMIC CROP DASHBOARD -----------------
st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>📊 {active_crop} Dashboard Summary</div>", unsafe_allow_html=True)

# Fetch Crop parameters from local dataset to populate dashboard cards
@st.cache_data
def get_crop_dashboard_data(crop_name):
    soil_res = retriever.retrieve(f"{crop_name} soil and climate suitability", top_k=1)
    pest_res = retriever.retrieve(f"{crop_name} pests diseases control", top_k=1)
    mandi_res = retriever.retrieve(f"{crop_name} mandi market prices", top_k=1)
    irr_res = retriever.retrieve(f"{crop_name} irrigation guidance", top_k=1)
    
    def clean_text(res_list):
        if not res_list:
            return "No data found."
        text = res_list[0]["chunk"]
        lines = text.split("\n")
        clean_lines = []
        for l in lines:
            l_strip = l.strip()
            if l_strip.startswith("Section:") or l_strip.startswith("Crop:") or l_strip.startswith("Crop/Subject:") or l_strip.startswith("Soil & Climate Samples:"):
                continue
            clean_lines.append(l_strip)
        return "\n".join([c for c in clean_lines if c]).strip()
        
    return {
        "soil": clean_text(soil_res),
        "pest": clean_text(pest_res),
        "mandi": clean_text(mandi_res),
        "irrigation": clean_text(irr_res)
    }

dash_data = get_crop_dashboard_data(active_crop)

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.markdown(f"""
    <div class="dash-card">
        <h4>🧪 {text_map['soil_title']}</h4>
        <p>{dash_data['soil']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dash-card">
        <h4>💰 {text_map['mandi_title']}</h4>
        <p>{dash_data['mandi']}</p>
    </div>
    """, unsafe_allow_html=True)

with col_d2:
    st.markdown(f"""
    <div class="dash-card">
        <h4>🐛 {text_map['pest_title']}</h4>
        <p>{dash_data['pest']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dash-card">
        <h4>💧 {text_map['irrigation_title']}</h4>
        <p>{dash_data['irrigation']}</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------- ADVISORY CHATBOT SECTION -----------------
st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{text_map['chat_header']}</div>", unsafe_allow_html=True)

# Initialize messages
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_retrieved_sources" not in st.session_state:
    st.session_state.last_retrieved_sources = []

# Show validation warnings if credentials are missing
credentials_valid = True
if not active_api_key:
    st.error("⚠️ Missing WATSONX_API_KEY. Copy `.env.example` to `.env` and fill in your credentials, or set it under the 'Developer & API Config' sidebar expander.")
    credentials_valid = False
if not active_project_id:
    st.error("⚠️ Missing WATSONX_PROJECT_ID. Copy `.env.example` to `.env` and fill in your credentials, or set it under the 'Developer & API Config' sidebar expander.")
    credentials_valid = False

# Clear conversation action row
col_c_left, col_c_right = st.columns([4, 1])
with col_c_right:
    if st.button(text_map["btn_clear"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_retrieved_sources = []
        st.rerun()

with col_c_left:
    st.info(f"{text_map['context_label']} **{active_crop}**")

# Display current chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Suggested chips for current crop
st.markdown(f"<span style='font-size: 0.9rem; color: #4A5568;'>{text_map['quick_questions']}: </span>", unsafe_allow_html=True)
suggestion_queries = {
    "Rice": ["How do I control Stem Borer in Rice?", "What fertilizer split doses do I apply for Rice?", "What is the market price of Rice in Punjab?"],
    "Maize": ["What are the main insect pests for Maize?", "Describe critical irrigation stages for Maize", "What is the typical pH range for Maize?"],
    "Cotton": ["What is the Pink Bollworm warning for Cotton?", "Tell me average mandi rates for Cotton", "How much rainfall does Cotton require?"],
    "Mango": ["How do I control Mango Hopper?", "What soil conditions are needed for Mango?", "Tell me mango prices in Guntur mandi"],
    "Apple": ["How do I control Woolly Apple Aphid?", "What is the fertilizer dosage for Apple?", "What is the cool ripening temperature range for Apple?"],
    "Coconut": ["How do I treat Rhinoceros Beetle in Coconut?", "Tell me typical soil requirements for Coconut", "Which mandi has highest Coconut price?"]
}

chips = suggestion_queries.get(active_crop, [])
col_chip1, col_chip2, col_chip3 = st.columns(3)
chip_cols = [col_chip1, col_chip2, col_chip3]

selected_chip = None
for i, chip_q in enumerate(chips):
    with chip_cols[i]:
        # Only enable chip questions if credentials are valid
        if st.button(chip_q, key=f"chip_{i}", use_container_width=True, disabled=not credentials_valid):
            selected_chip = chip_q

# User Chat Input
chat_input = st.chat_input(text_map["input_placeholder"], disabled=not credentials_valid)

query_to_run = selected_chip if selected_chip else chat_input

if query_to_run and credentials_valid:
    # Append user question
    st.session_state.messages.append({"role": "user", "content": query_to_run})
    st.rerun()

# Execute model response if user has just typed or clicked a chip
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    latest_user_msg = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        status_text = st.empty()
        status_text.info(text_map["thinking"])
        
        try:
            # 1. Retrieve RAG chunks
            retrieval_query = f"{active_crop} {latest_user_msg}"
            retrieved = retriever.retrieve(retrieval_query, top_k=3)
            st.session_state.last_retrieved_sources = retrieved
            
            context_str = "\n\n".join([r["chunk"] for r in retrieved])
            
            # 2. Build RAG Prompt
            rag_prompt = f"""You are Farmer Assist, an expert agricultural advisory chatbot for small-scale Indian farmers.
Use the following retrieved context from our farming knowledge base to answer the farmer's question about {active_crop}.
If the retrieved context does not contain the answer, use your pre-trained agricultural knowledge to provide a helpful answer, but clearly state that it is general advice.
Always be polite, supportive, and write the answer in the language requested (English or Hindi). Provide actionable, practical farming steps.

Retrieved Context:
{context_str}

Farmer's Question:
{latest_user_msg}

Answer:"""
            
            # 3. Get token
            token = get_watsonx_token(active_api_key)
            
            # 4. Generate response
            response_text = call_watsonx_generation(
                prompt=rag_prompt,
                token=token,
                proj_id=active_project_id,
                model=active_model_id,
                temp=temperature,
                max_tok=max_tokens,
                reg_sub=region_subdomain
            )
            
            status_text.empty()
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()
            
        except Exception as e:
            status_text.empty()
            st.error(f"Error calling watsonx.ai: {e}")

# Sidebar source display (updated after queries are executed)
if st.session_state.last_retrieved_sources:
    st.sidebar.divider()
    st.sidebar.markdown(f"### {text_map['retrieved_sources']}")
    for idx, item in enumerate(st.session_state.last_retrieved_sources):
        lines = item["chunk"].split("\n")
        crop_name = "General Agriculture"
        section_name = "Knowledge Reference"
        for line in lines:
            if line.startswith("Crop:") or line.startswith("Crop/Subject:"):
                crop_name = line.split(":", 1)[1].strip()
            elif line.startswith("Section:"):
                section_name = line.split(":", 1)[1].strip()
        
        with st.sidebar.expander(f"📖 {crop_name} - {section_name}"):
            st.markdown(f"<span class='source-badge'>{text_map['source_score']}: {item['score']:.4f}</span>", unsafe_allow_html=True)
            st.text_area("Chunk Content", value=item["chunk"], height=150, disabled=True, label_visibility="collapsed", key=f"sidebar_txt_{idx}")

# Simple footer
st.markdown("""
<div class="footer">
    Farmer Assist smart chatbot | Built for IBM watsonx.ai submission | 🌾 Helping small-scale Indian farmers grow sustainably.
</div>
""", unsafe_allow_html=True)
