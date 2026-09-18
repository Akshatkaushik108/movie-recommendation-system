import streamlit as st
import os
from html import escape
from movie_utils import load_model, recommend_movies, fetch_movie_poster
# --- Page Configuration ---
st.set_page_config(
    page_title="AI-Powered Movie Recommendation",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🎬"
)

# --- Custom CSS for Beautiful Modern Design ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&display=swap');

    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main App Styling */
    .stApp {
        background: #0d0d0d;
        font-family: 'Poppins', sans-serif;
        color: #ffffff;
    }

    /* Ensure all text is visible */
    p, div, span, label {
        color: #ffffff;
    }

    /* Stunning Hero Section */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 80px 40px;
        border-radius: 30px;
        margin: 20px 0 40px 0;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .hero-content {
        position: relative;
        z-index: 2;
        text-align: center;
    }

    .hero-logo {
        font-size: 80px;
        font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        text-shadow: 0 10px 30px rgba(0,0,0,0.3);
        letter-spacing: 3px;
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .hero-tagline {
        font-size: 24px;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 300;
        letter-spacing: 2px;
        margin-top: 10px;
    }

    .hero-description {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 15px;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Section Headers */
    .section-header {
        font-size: 42px;
        font-weight: 700;
        color: #fff;
        margin: 50px 0 30px 0;
        padding-left: 20px;
        border-left: 6px solid #667eea;
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
        padding: 20px;
        border-radius: 10px;
    }

    /* Movie Cards */
    .movie-card-container {
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        margin-bottom: 20px;
    }

    .movie-card-container:hover {
        transform: translateY(-15px) scale(1.05);
    }

    .movie-poster {
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        transition: all 0.4s ease;
        border: 3px solid transparent;
    }

    .movie-card-container:hover .movie-poster {
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.6);
        border-color: #667eea;
    }

    .movie-title {
        color: #fff;
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        margin-top: 15px;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 10px;
        transition: all 0.3s ease;
    }

    .movie-card-container:hover .movie-title {
        color: #667eea;
        transform: scale(1.05);
    }

    /* Search Section */
    .search-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 30px;
        border-radius: 25px;
        margin: 20px 0;
        border: 2px solid rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
    }

    /* Enhanced Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50px;
        padding: 18px 45px;
        font-weight: 700;
        border: none;
        font-size: 18px;
        transition: all 0.4s ease;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        transform: translateY(-5px);
    }

    /* Selectbox Styling */
    .stSelectbox label {
        color: #fff !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-bottom: 10px !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }

    /* Selectbox dropdown text */
    .stSelectbox div[data-baseweb="select"] > div {
        color: #ffffff !important;
        background-color: rgba(13, 13, 13, 0.9) !important;
    }

    /* Selectbox selected value */
    .stSelectbox [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* Selectbox dropdown menu - WHITE BACKGROUND */
    .stSelectbox [role="listbox"] {
        background-color: #ffffff !important;
        border: 2px solid rgba(102, 126, 234, 0.5) !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    }

    /* Selectbox dropdown options - BLACK TEXT */
    .stSelectbox [role="option"] {
        color: #000000 !important;
        background-color: #ffffff !important;
        padding: 10px 15px !important;
        font-weight: 500 !important;
    }

    .stSelectbox [role="option"]:hover {
        background-color: rgba(102, 126, 234, 0.15) !important;
        color: #000000 !important;
    }

    /* Selectbox search input in dropdown - BLACK TEXT */
    .stSelectbox [role="listbox"] input {
        color: #000000 !important;
        background-color: #f5f5f5 !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
        padding: 8px !important;
    }

    .stSelectbox [role="listbox"] input::placeholder {
        color: #666 !important;
    }

    /* Chat Styling */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    .chat-title {
        font-size: 36px;
        font-weight: 900;
        color: white !important;
        margin: 0;
    }

    .chat-subtitle {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.95) !important;
        margin-top: 10px;
    }

    /* Override for chat header text to stay white */
    .chat-header .chat-title,
    .chat-header .chat-subtitle {
        color: white !important;
    }

    /* Chat Messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span,
    .stChatMessage [data-testid="stMarkdownContainer"],
    .stChatMessage .st-emotion-cache-1v0mbdj {
        color: #1a1a1a !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        font-weight: 500 !important;
    }

    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #e3e8ff 0%, #f0f2ff 100%) !important;
        border-left: 4px solid #667eea;
    }

    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #f3e8ff 0%, #f8f0ff 100%) !important;
        border-left: 4px solid #764ba2;
    }

    /* Force all chat message text to be dark */
    [data-testid="stChatMessageContent"] * {
        color: #1a1a1a !important;
    }

    /* Additional overrides for chat text visibility */
    .stChatMessage .st-emotion-cache-1v0mbdj,
    .stChatMessage .st-emotion-cache-1v0mbdj p,
    .stChatMessage [class*="emotion-cache"] p,
    .stChatMessage [class*="emotion-cache"] div,
    .stChatMessage [class*="emotion-cache"] span {
        color: #000000 !important;
    }

    /* Target Streamlit's markdown container specifically */
    .element-container p,
    .stMarkdown p {
        color: inherit;
    }

    /* Inside chat messages specifically */
    .stChatMessage .element-container p,
    .stChatMessage .stMarkdown p {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* Chat Input */
    .stChatInput input {
        background: #ffffff !important;
        border: 2px solid rgba(102, 126, 234, 0.4) !important;
        border-radius: 30px !important;
        color: #000000 !important;
        padding: 18px 25px !important;
        font-size: 16px !important;
    }

    .stChatInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.4) !important;
    }

    .stChatInput input::placeholder {
        color: #888888 !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    .streamlit-expanderHeader p, .streamlit-expanderHeader svg {
        color: white !important;
        fill: white !important;
    }

    details[open] .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.3) !important;
        color: white !important;
    }

    details[open] .streamlit-expanderHeader p {
        color: white !important;
    }

    .streamlit-expanderContent {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
        border-radius: 15px;
        padding: 20px;
        border: 2px solid rgba(102, 126, 234, 0.2);
    }

    /* Expander text override */
    [data-testid="stExpander"] p {
        color: white !important;
    }

    [data-testid="stExpander"] summary {
        color: white !important;
    }

    /* Chat content inside expander - BLACK TEXT */
    .streamlit-expanderContent p,
    .streamlit-expanderContent div,
    .streamlit-expanderContent span,
    .streamlit-expanderContent label,
    .streamlit-expanderContent [data-testid="stMarkdownContainer"] {
        color: #1a1a1a !important;
    }

    /* Ensure markdown content is dark */
    .streamlit-expanderContent [data-testid="stMarkdownContainer"] p {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }

    /* Chat message markdown */
    .stMarkdown {
        color: #ffffff !important;
    }

    /* Rank Badges */
    .rank-badge {
        position: absolute;
        top: 15px;
        left: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 16px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
        z-index: 10;
    }

    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 50px 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        padding: 40px 20px;
        margin-top: 60px;
        border-top: 1px solid rgba(102, 126, 234, 0.2);
    }

    .footer-title {
        font-size: 20px;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
    }

    /* Spinner/Loading */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }

    /* Success/Warning Messages */
    .stSuccess, .stWarning, .stError {
        border-radius: 15px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_resource
def load_movie_data():
    try:
        return load_model()
    except FileNotFoundError:
        st.error("Movie data is missing. Run python build_model.py, then restart the app.")
        st.stop()

movies, cosine_sim = load_movie_data()

@st.cache_resource
def init_llm():
    key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    if not key or not base_url:
        return None
    try:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.7,
            openai_api_key=key,
            openai_api_base=base_url,
            timeout=30,
            max_retries=1,
        )
    except (ImportError, ValueError):
        return None

llm = init_llm()

def get_recommendations(title, cosine_sim=cosine_sim):
    return recommend_movies(movies, cosine_sim, title)

def get_top_movies(n=10):
    """Get a repeatable sample of movies"""
    return movies.drop_duplicates("movie_id").sample(n=min(n, movies.movie_id.nunique()), random_state=42)

@st.cache_data
def fetch_poster(movie_id):
    return fetch_movie_poster(movie_id)

def chat_with_movie_agent(user_message, chat_history):
    """AI chat function with improved error handling"""
    if llm is None:
        return "Sorry, the AI chat service is currently unavailable. Please try the movie search feature instead!"

    try:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        system_prompt = """You are an AI Movie Assistant, an enthusiastic and knowledgeable movie expert.
        Help users discover amazing movies based on their preferences. Be friendly, engaging, and provide
        thoughtful recommendations with brief explanations. Keep responses concise but informative."""

        # Check for movie mentions
        movie_matches = movies[movies['title'].str.contains(user_message, case=False, na=False, regex=False)]
        context = ""

        if len(movie_matches) > 0:
            movie_title = movie_matches.iloc[0]['title']
            try:
                recs = get_recommendations(movie_title)
                if not recs.empty:
                    rec_list = recs['title'].tolist()[:5]
                    context = f"\n\n[Movies similar to '{movie_title}']: " + ", ".join(rec_list)
            except:
                pass

        messages = [SystemMessage(content=system_prompt)]

        # Keep last 10 messages for context
        for msg in chat_history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=user_message + context))

        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        return "The chat service could not complete this request. Please try again or use the movie selector."

# --- Initialize Session State ---
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hey there! I'm your AI Movie Assistant, your personal movie expert! Ask me anything about movies, or tell me what you like and I'll recommend something awesome! 🎬✨"}
    ]
if "show_recommendations" not in st.session_state:
    st.session_state.show_recommendations = False

# --- Hero Section ---
st.markdown("""
    <div class="hero-container">
        <div class="hero-content">
            <div class="hero-logo">🎬 AI-Powered Movie Recommendation</div>
            <div class="hero-tagline">Intelligent Movie Discovery</div>
            <div class="hero-description">
                Discover your next favorite film with recommendations based on movie genres, keywords, cast and directors
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Top Movies Carousel ---
st.markdown('<div class="section-header">🎬 Explore Movies</div>', unsafe_allow_html=True)

top_movies = get_top_movies(10)

# Display in two rows
for row_idx in range(2):
    cols = st.columns(5)
    start_idx = row_idx * 5

    for col_idx, col in enumerate(cols):
        movie_idx = start_idx + col_idx
        if movie_idx < len(top_movies):
            movie = top_movies.iloc[movie_idx]
            with col:
                st.markdown('<div class="movie-card-container">', unsafe_allow_html=True)
                poster_url = fetch_poster(movie['movie_id'])
                st.image(poster_url, use_container_width=True)
                st.markdown(f'<div class="movie-title">#{movie_idx+1} {escape(str(movie["title"]))}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    if row_idx == 0:
        st.markdown("<br>", unsafe_allow_html=True)

# --- Search Section ---
st.markdown("---")
st.markdown('<div class="section-header">🔍 Find Your Perfect Match</div>', unsafe_allow_html=True)

st.markdown('<div class="search-container">', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

with col1:
    selected_movie = st.selectbox(
        "🎥 Select a movie to discover similar ones:",
        movies['title'].values,
        key="movie_select"
    )

with col2:
    st.write("")
    st.write("")
    if st.button('✨ Discover'):
        st.session_state.show_recommendations = True
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- Recommendations Display ---
if st.session_state.show_recommendations and selected_movie:
    st.markdown("---")
    st.markdown(f'<div class="section-header">🎯 Perfect Matches for "{escape(str(selected_movie))}"</div>', unsafe_allow_html=True)

    with st.spinner("🎬 Finding perfect matches for you..."):
        recommendations = get_recommendations(selected_movie)

    if recommendations.empty:
        st.warning(f"⚠️ No recommendations found for **{selected_movie}**. Try another!")
    else:
        # Display recommendations
        for row_idx in range(2):
            rec_cols = st.columns(5)
            start_idx = row_idx * 5

            for col_idx, col in enumerate(rec_cols):
                rec_idx = start_idx + col_idx
                if rec_idx < len(recommendations):
                    movie = recommendations.iloc[rec_idx]
                    with col:
                        st.markdown('<div class="movie-card-container">', unsafe_allow_html=True)
                        poster_url = fetch_poster(movie['movie_id'])
                        st.image(poster_url, use_container_width=True)
                        st.markdown(f'<div class="movie-title">{escape(str(movie["title"]))}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

            if row_idx == 0:
                st.markdown("<br>", unsafe_allow_html=True)

# --- AI Chat Section ---
st.markdown("---")
st.markdown('<div class="section-header">💬 Chat with AI Movie Assistant</div>', unsafe_allow_html=True)

with st.expander("🤖 Click to open AI Chat Assistant", expanded=False):
    st.markdown("""
        <div class="chat-header">
            <div class="chat-title">🎬 AI Movie Assistant</div>
            <div class="chat-subtitle">Get personalized movie recommendations through conversation</div>
        </div>
    """, unsafe_allow_html=True)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(f'<div style="color: #000000; font-weight: 500; font-size: 16px;">{escape(str(message["content"]))}</div>', unsafe_allow_html=True)

    # Chat input
    if llm is None:
        st.caption("Optional chat is not configured. Movie recommendations work without it.")
    if prompt := st.chat_input("💭 Ask me about movies, genres, actors, or get recommendations...", disabled=llm is None):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="👤"):
            st.markdown(f'<div style="color: #000000; font-weight: 500; font-size: 16px;">{escape(str(prompt))}</div>', unsafe_allow_html=True)

        # Get AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🎬 Thinking..."):
                response = chat_with_movie_agent(prompt, st.session_state.messages[:-1])
                st.markdown(f'<div style="color: #000000; font-weight: 500; font-size: 16px;">{escape(str(response))}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})

        st.rerun()

    # Clear chat button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Chat cleared! Ready for a fresh conversation. What movies are you interested in?"}
            ]
            st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("""
    <div class="footer">
        <div class="footer-title">🎬 AI-Powered Movie Recommendation</div>
        <p style="font-size: 16px; color: #aaa; margin-top: 10px;">
            Your Intelligent Movie Discovery Platform
        </p>
    </div>
""", unsafe_allow_html=True)
