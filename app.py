import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Reel Insights: TMDB Movie Dashboard", page_icon="🎬", layout="wide")

# Load Data from SQLite Database
@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect('data/tmdb_movies.db')
        movies_df = pd.read_sql("SELECT * FROM movies", conn)
        genres_df = pd.read_sql("SELECT * FROM genres", conn)
        movie_genres_df = pd.read_sql("SELECT * FROM movie_genres", conn)
        cast_df = pd.read_sql("SELECT * FROM cast", conn)
        conn.close()
        return movies_df, genres_df, movie_genres_df, cast_df
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

movies_df, genres_df, movie_genres_df, cast_df = load_data()

if movies_df.empty:
    st.error("⚠️ Database or movies table not found inside the 'data/' folder! Please check your file paths.")
else:
    # Sidebar Navigation for Multi-page setup
    st.sidebar.title("🎬 Reel Insights Menu")
    page = st.sidebar.radio("Navigation", ["1. Filters & Overview", "2. Dashboard & Visualizations", "3. Query Explorer"])

    # -----------------------------------------
    # PAGE 1: FILTERS & OVERVIEW
    # -----------------------------------------
    if page == "1. Filters & Overview":
        st.title("🎛️ Movie Filters & Dataset Overview")
        st.write("Use the controls below to filter movies dynamically across the app.")

        # Extract year safely
        if 'release_date' in movies_df.columns:
            movies_df['year'] = pd.to_datetime(movies_df['release_date'], errors='coerce').dt.year
            min_y = int(movies_df['year'].min()) if not movies_df['year'].isnull().all() else 2000
            max_y = int(movies_df['year'].max()) if not movies_df['year'].isnull().all() else 2026
        else:
            min_y, max_y = 2000, 2026

        col1, col2 = st.columns(2)
        with col1:
            year_range = st.slider("Select Release Year Range", min_y, max_y, (min_y, max_y))
        with col2:
            min_rating = st.slider("Minimum Vote Average", 0.0, 10.0, 0.0)

        # Filtering logic
        filtered_df = movies_df[
            (movies_df['year'] >= year_range[0]) & 
            (movies_df['year'] <= year_range[1]) & 
            (movies_df['vote_average'] >= min_rating)
        ]

        st.markdown("---")
        st.metric("🎬 Live Matching Movies Count", f"{len(filtered_df):,}")
        
        st.subheader("Sample Filtered Data Preview")
        st.dataframe(filtered_df[['title', 'release_date', 'vote_average', 'revenue', 'budget']].head(15), use_container_width=True)

    # -----------------------------------------
    # PAGE 2: DASHBOARD & VISUALIZATIONS
    # -----------------------------------------
    elif page == "2. Dashboard & Visualizations":
        st.title("📊 Business Analytics Dashboard")
        st.write("High-level key performance metrics and industry trends.")

        # KPI Metrics Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Movies", f"{len(movies_df):,}")
        kpi2.metric("Total Genres", f"{len(genres_df):,}" if not genres_df.empty else "N/A")
        kpi3.metric("Total Cast Records", f"{len(cast_df):,}" if not cast_df.empty else "N/A")
        avg_rtg = movies_df['vote_average'].mean() if 'vote_average' in movies_df.columns else 0
        kpi4.metric("Average Rating", f"{avg_rtg:.2f}")

        st.markdown("---")

        # Top 10 Movies by Revenue
        st.subheader("🏆 Top 10 Highest-Grossing Movies")
        if 'title' in movies_df.columns and 'revenue' in movies_df.columns:
            top_rev = movies_df.nlargest(10, 'revenue')
            fig_rev = px.bar(top_rev, x='title', y='revenue', color='revenue', 
                             title="Top 10 Movies by Box-Office Revenue",
                             labels={'title': 'Movie Title', 'revenue': 'Revenue ($)'})
            st.plotly_chart(fig_rev, use_container_width=True)

        # Budget vs Revenue Scatter Plot
        st.subheader("💰 Budget vs Revenue Relationship")
        if 'budget' in movies_df.columns and 'revenue' in movies_df.columns:
            fig_scat = px.scatter(movies_df, x='budget', y='revenue', color='vote_average',
                                  hover_data=['title'], title="Production Budget vs Box-Office Revenue",
                                  labels={'budget': 'Budget ($)', 'revenue': 'Revenue ($)'})
            st.plotly_chart(fig_scat, use_container_width=True)
            
        st.info("💡 **Key Business Insight:** High production budgets strongly correlate with higher box-office returns, though several mid-budget movies achieve exceptional proportional ROI.")

    # -----------------------------------------
    # PAGE 3: QUERY EXPLORER
    # -----------------------------------------
    elif page == "3. Query Explorer":
        st.title("🔍 SQL Query Explorer")
        st.write("Explore pre-defined analytical SQL queries and their live database execution results.")

        query_choice = st.selectbox("Select SQL Analysis Query:", [
            "1. Top 10 Highest-Grossing Movies",
            "2. Movies with Highest Budgets",
            "3. Top Rated Movies (Min 500 Votes)"
        ])

        conn = sqlite3.connect('data/tmdb_movies.db')
        if "Top 10 Highest-Grossing" in query_choice:
            query = "SELECT title, release_date, budget, revenue FROM movies ORDER BY revenue DESC LIMIT 10"
        elif "Highest Budgets" in query_choice:
            query = "SELECT title, release_date, budget FROM movies ORDER BY budget DESC LIMIT 10"
        else:
            query = "SELECT title, vote_average, vote_count FROM movies WHERE vote_count > 500 ORDER BY vote_average DESC LIMIT 10"

        result_df = pd.read_sql(query, conn)
        conn.close()

        st.subheader("Query Results Execution Table")
        st.dataframe(result_df, use_container_width=True)
        
        st.success("✅ Query executed successfully directly from the SQLite database schema!")
