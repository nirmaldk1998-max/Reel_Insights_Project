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