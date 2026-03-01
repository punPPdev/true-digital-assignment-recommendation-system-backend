import streamlit as st
import requests
import os
import pandas as pd
import requests

# CRUCIAL: Read the API URL from environment variables.
# This allows it to work both locally and inside Docker without changing code.
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(layout="wide")

st.set_page_config(page_title="Movie Recommender", layout="centered")

st.title("🎬 Netflix Movie/TV shows Recommendation System")

@st.cache_data
def fetch_options():
    
    try:
        response = requests.get("http://127.0.0.1:8000/get-movie-tv-show-data")
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []
    
    
res_json = fetch_options()
select_oprtion = res_json['dashboard_data']
    
# User Input
genres = st.selectbox(
    "What genres do you like?",
    select_oprtion['genres'],
    index = None,
    placeholder="Choose genres"
)
# User Input
title = st.selectbox(
    "What movies or tv serires do you like?",
    select_oprtion['title'],
    index = None,
    placeholder="Choose title"
)
cast = st.selectbox(
    "What cast do you like?",
    select_oprtion['cast'],
    index = None,
    placeholder="Choose cast"
)
director = st.selectbox(
    "What director do you like?",
    select_oprtion['director'],
    index = None,
    placeholder="Choose director"
)
# top_k = st.slider("How many recommendations?", min_value=1, max_value=5, value=3)

if st.button("Get Recommendations"):

    if not( genres or title or cast or director):
        st.warning("Please select at least one genre!")
    else:
        if not genres:
            genres = ''
        if not title:
            title = ''
        if not cast:
            cast= ''
        if not director:
            director =''  
        
        with st.spinner("Getting recommend mvoie/tv series"):
            # Prepare the JSON payload
            payload = {
                "liked_content": [genres, title, cast, director],
                "top_k": 10
            }
            print(payload)
            
            try:
                # Call the FastAPI endpoint
                response = requests.post(f"{API_URL}/recommend", json=payload)
                response.raise_for_status()
                data = response.json()
                
                st.success(f"Status: {data['status']}")
                
                # Display results nicely in a table
                if data["recommendations"]:
                    st.header("🍿Here list of TV shows and movies you should watch!!!", divider=True)
                    df_recs = pd.DataFrame(data["recommendations"])
                    st.table(df_recs[['title', 'director', 'cast', 'genres', 'description', 'rating']])
                else:
                    st.info("No recommendations found.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"API Connection Error: {e}")