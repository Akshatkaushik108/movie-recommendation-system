import streamlit as st
import os
from html import escape
from movie_utils import load_model, recommend_movies, fetch_movie_poster
# --- Configuration for Wide Layout and Custom Styling ---
st.set_page_config(
    page_title="Cinematch: Movie Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner, modern look
st.markdown("""
    <style>
    /* General App Styling */
    .css-1d391kg { /* Main Content Block */
        padding-top: 2rem;
    }
    .stButton>button { /* Styling the Recommend Button */
        background-color: #E50914; /* Netflix Red */
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #f40a17;
    }
    /* Header/Title Styling */
    .st-emotion-cache-10trblm { /* Header H1 element */
        color: #E50914; /* Red color for title */
        font-family: 'Arial Black', sans-serif;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    /* Movie Title in Recommendation Cards */
    .movie-title-card {
        text-align: center;
        font-size: 14px;
        font-weight: 600;
        min-height: 40px; /* Ensure titles have uniform height */
        display: flex;
        align-items: center;
        justify-content: center;
        color: #f0f2f6; /* Light color for better contrast on dark background */
        margin-top: -10px;
    }
    /* Recommendation Header */
    .recommendation-header {
        color: #ffffff; /* White text for contrast */
        font-size: 24px;
        margin-top: 15px;
        margin-bottom: 20px;
        border-bottom: 2px solid #333333;
        padding-bottom: 5px;
    }
    /* Make the whole app look dark-themed */
    body {
        color: #f0f2f6;
        background-color: #0e1117;
    }
    .stApp {
        background-color: #1a1a1a;
    }
    /* Ensure the selectbox is visible */
    .st-emotion-cache-nahz7x {
        color: #0e1117; /* Text color for the selectbox dropdown background */
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data loading and recommendations ---
@st.cache_resource
def load_movie_data():
    try:
        return load_model()
    except FileNotFoundError:
        st.error("Movie data is missing. Run python build_model.py, then restart the app.")
        st.stop()

movies, cosine_sim = load_movie_data()

def get_recommendations(title, cosine_sim=cosine_sim):
    return recommend_movies(movies, cosine_sim, title)

@st.cache_data
def fetch_poster(movie_id):
    return fetch_movie_poster(movie_id, size="w185")

# --- Streamlit UI Layout ---
st.title("🎬 Cinematch: Movie Recommendation System")

# Create a container for input elements for better visual grouping
input_container = st.container()

with input_container:
    # Use st.columns to place the selectbox and button side-by-side
    col1, col2 = st.columns([4, 1])
    
    with col1:
        selected_movie = st.selectbox(
            "Select a movie to get similar recommendations:", 
            movies['title'].values, 
            key="movie_select"
        )
    
    with col2:
        # Add some vertical space before the button to align it better
        st.write("") 
        st.write("")
        if st.button('Recommend', key='recommend_button'):
            # This flag is used to trigger the display logic outside the button block
            st.session_state['run_recommendation'] = True
        else:
            # Initialize or reset the flag
            if 'run_recommendation' not in st.session_state:
                 st.session_state['run_recommendation'] = False


# --- Recommendation Display Logic ---

# Only run and display results if the button was pressed
if st.session_state.get('run_recommendation'):
    
    # Add a visual separator
    st.markdown("---")
    
    st.markdown('<p class="recommendation-header">🔥 Top 10 Recommended Movies Just For You:</p>', unsafe_allow_html=True)
    
    # Get the recommendations
    recommendations = get_recommendations(selected_movie)
    
    if recommendations.empty:
        st.info(f"Could not find recommendations for **{selected_movie}**. Please select another movie.")
    else:
        # Use two rows of 5 columns each for better poster presentation
        
        # Row 1: Movies 1-5
        cols1 = st.columns(5)
        for idx, (col, row) in enumerate(zip(cols1, recommendations.iloc[0:5].iterrows())):
            movie_data = row[1]
            movie_title = movie_data['title']
            movie_id = movie_data['movie_id']
            
            # Fetch poster and display
            with col:
                poster_url = fetch_poster(movie_id)
                st.image(poster_url, caption=f"#{idx+1}", use_container_width=True)
                st.markdown(f'<p class="movie-title-card">{escape(str(movie_title))}</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True) # Add space between rows

        # Row 2: Movies 6-10
        cols2 = st.columns(5)
        for idx, (col, row) in enumerate(zip(cols2, recommendations.iloc[5:10].iterrows())):
            movie_data = row[1]
            movie_title = movie_data['title']
            movie_id = movie_data['movie_id']
            
            # Fetch poster and display
            with col:
                poster_url = fetch_poster(movie_id)
                st.image(poster_url, caption=f"#{idx+6}", use_container_width=True)
                st.markdown(f'<p class="movie-title-card">{escape(str(movie_title))}</p>', unsafe_allow_html=True)

    