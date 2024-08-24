import streamlit as st
import pickle
import pandas as pd
import movieposters as mp
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fetch posters for a list of movies using multithreading
def fetch_posters(movie_names):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(mp.get_poster, movie_name): movie_name for movie_name in movie_names}
        results = {}
        for future in as_completed(futures):
            movie_name = futures[future]
            try:
                results[movie_name] = future.result()
            except Exception as e:
                results[movie_name] = None  # Handle error or return None if poster fetch fails
    return results

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
    
    # Fetch posters with a spinner
    with st.spinner('Fetching movie posters...'):
        posters = fetch_posters(recommended_movies)
    
    return recommended_movies, [posters.get(movie, None) for movie in recommended_movies]

# Load movie data and similarity matrix
movies_list = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.header("Movie Recommender System")
selected_movie_name = st.selectbox('Type or select a movie from dropdown', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    
    cols = st.columns(5)
    for i, col in enumerate(cols):
        if i < len(names):
            with col:
                st.text(names[i])
                if posters[i] is not None:
                    st.image(posters[i])
                else:
                    st.text("Poster not available")
