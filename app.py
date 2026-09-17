import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Reel Insights: TMDB Movie Dashboard", page_icon="🎬", layout="wide")

st.title("🎬 Reel Insights: Global Movie Industry Analysis")
st.write("Welcome to the End-to-End TMDB Movie Analytics Dashboard!")

# Database connection check
try:
    conn = sqlite3.connect('data/tmdb_movies.db')
    movies_df = pd.read_sql("SELECT * FROM movies", conn)
    genres_df = pd.read_sql("SELECT * FROM genres", conn)
    conn.close()
    st.success("Database connected successfully inside Streamlit app!")
    st.metric("Total Movies Loaded", f"{len(movies_df):,}")
except Exception as e:
    st.error(f"Database connection error: {e}")
    # Add a simple chart to make the dashboard look awesome
if 'movies_df' in locals() and not movies_df.empty:
    st.subheader("📊 Top 10 Movies by Revenue")
    
    # Check if revenue and title columns exist
    if 'title' in movies_df.columns and 'revenue' in movies_df.columns:
        top_movies = movies_df.nlargest(10, 'revenue')
        fig = px.bar(
            top_movies, 
            x='title', 
            y='revenue', 
            color='revenue',
            title="Top 10 Highest Revenue Movies",
            labels={'title': 'Movie Title', 'revenue': 'Revenue ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
