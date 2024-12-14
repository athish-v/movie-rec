import string
import pickle
import pandas as pd
import ast
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def read_csv_to_df():
    # Read datasets
    credit_ = pd.read_csv('dataset/tmdb_5000_credits.csv')
    movies = pd.read_csv('dataset/tmdb_5000_movies.csv')

    # Merge datasets on the title
    movies = movies.merge(credit_, on='title')

    # Ensure genres and keywords are processed correctly
    def process_column(col):
        try:
            return " ".join([item['name'] for item in ast.literal_eval(col)])
        except (ValueError, SyntaxError, TypeError):
            return ""

    movies['genres'] = movies['genres'].apply(process_column)
    movies['keywords'] = movies['keywords'].apply(process_column)

    # Create a 'tags' column for similarity analysis
    movies['tags'] = (movies['overview'].fillna("") + " " +
                      movies['genres'].fillna("") + " " +
                      movies['keywords'].fillna(""))

    # Reduce to necessary columns
    new_df = movies[['movie_id', 'title', 'tags']]
    return movies, new_df, None


def recommend(new_df, movie, pickle_file_path):
    with open(pickle_file_path, 'rb') as file:
        similarity = pickle.load(file)
    idx = new_df[new_df['title'] == movie].index[0]
    similar_movies = sorted(list(enumerate(similarity[idx])), key=lambda x: x[1], reverse=True)[1:6]
    recommended = [new_df.iloc[i[0]].title for i in similar_movies]
    posters = [fetch_posters(new_df.iloc[i[0]].movie_id) for i in similar_movies]
    return recommended, posters

def fetch_posters(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=6177b4297dff132d300422e0343471fb'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}"
    return "https://via.placeholder.com/150"

def get_details(movie_name):
    # Load datasets
    movies = pd.read_csv('dataset/tmdb_5000_movies.csv')
    credits = pd.read_csv('dataset/tmdb_5000_credits.csv')

    # Merge datasets
    movies = movies.merge(credits, on='title')

    # Find the selected movie
    movie_data = movies[movies['title'] == movie_name]
    if movie_data.empty:
        return None  # Return None if the movie is not found

    # Extract necessary details
    movie_data = movie_data.iloc[0]
    poster_url = fetch_posters(movie_data['movie_id'])

    genres = ", ".join([g['name'] for g in ast.literal_eval(movie_data['genres'])]) if pd.notna(movie_data['genres']) else "N/A"
    overview = movie_data['overview'] if pd.notna(movie_data['overview']) else "N/A"
    release_date = movie_data['release_date'] if pd.notna(movie_data['release_date']) else "N/A"
    director = "N/A"
    cast = "N/A"

    # Extract director from crew
    if pd.notna(movie_data['crew']):
        crew = ast.literal_eval(movie_data['crew'])
        directors = [member['name'] for member in crew if member['job'] == 'Director']
        director = directors[0] if directors else "N/A"

    # Format cast
    if pd.notna(movie_data['cast']):
        cast_list = ast.literal_eval(movie_data['cast'])
        cast = ", ".join([member['name'] for member in cast_list[:5]])  # Top 5 cast members

    # Return the details
    return [poster_url, movie_name, genres, overview, release_date, director, cast]

def fetch_genres():
    api_key = 'YOUR_TMDB_API_KEY'
    url = 'https://api.themoviedb.org/3/genre/movie/list'
    params = {'api_key': '6177b4297dff132d300422e0343471fb', 'language': 'en-US'}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        genres_data = response.json()
        # Convert list of dictionaries to a dictionary with id as key and name as value
        genres = {genre['id']: genre['name'] for genre in genres_data['genres']}
        return genres
    else:
        print("Failed to fetch genres:", response.status_code)
        return {}

def recommend_by_genres(movie_title, similarity_matrix, movies_dict):
    """
    Recommend movies based on genre similarity.

    Args:
        movie_title (str): Title of the liked movie.
        similarity_matrix (numpy.ndarray): Precomputed similarity matrix for genres.
        movies_dict (dict): Dictionary of movies and their metadata.

    Returns:
        list: List of recommended movie titles.
    """
    try:
        # Get the index of the movie in the dictionary
        movie_index = list(movies_dict.keys()).index(movie_title)
        
        # Get similarity scores for the movie
        similarity_scores = list(enumerate(similarity_matrix[movie_index]))
        
        # Sort by similarity score in descending order
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top 10 similar movies (excluding the current movie)
        recommended_indices = [i[0] for i in similarity_scores[1:11]]
        recommended_movies = [list(movies_dict.keys())[i] for i in recommended_indices]
        
        return recommended_movies
    except ValueError as e:
        print(f"Error: Movie '{movie_title}' not found in movies_dict. {e}")
        return []

def recommend_by_keywords(movie_title, similarity_matrix, movies_dict):
    """
    Recommend movies based on keyword similarity.

    Args:
        movie_title (str): Title of the liked movie.
        similarity_matrix (numpy.ndarray): Precomputed similarity matrix for keywords.
        movies_dict (dict): Dictionary of movies and their metadata.

    Returns:
        list: List of recommended movie titles.
    """
    try:
        # Get the index of the movie in the dictionary
        movie_index = list(movies_dict.keys()).index(movie_title)
        
        # Get similarity scores for the movie
        similarity_scores = list(enumerate(similarity_matrix[movie_index]))
        
        # Sort by similarity score in descending order
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top 10 similar movies (excluding the current movie)
        recommended_indices = [i[0] for i in similarity_scores[1:11]]
        recommended_movies = [list(movies_dict.keys())[i] for i in recommended_indices]
        
        return recommended_movies
    except ValueError as e:
        print(f"Error: Movie '{movie_title}' not found in movies_dict. {e}")
        return []

def recommend_by_cast(movie_title, similarity_matrix, movies_dict):
    """
    Recommend movies based on cast similarity.

    Args:
        movie_title (str): Title of the liked movie.
        similarity_matrix (numpy.ndarray): Precomputed similarity matrix for cast.
        movies_dict (dict): Dictionary of movies and their metadata.

    Returns:
        list: List of recommended movie titles.
    """
    try:
        # Get the index of the movie in the dictionary
        movie_index = list(movies_dict.keys()).index(movie_title)
        
        # Get similarity scores for the movie
        similarity_scores = list(enumerate(similarity_matrix[movie_index]))
        
        # Sort by similarity score in descending order
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top 10 similar movies (excluding the current movie)
        recommended_indices = [i[0] for i in similarity_scores[1:11]]
        recommended_movies = [list(movies_dict.keys())[i] for i in recommended_indices]
        
        return recommended_movies
    except ValueError as e:
        print(f"Error: Movie '{movie_title}' not found in movies_dict. {e}")
        return []


# Load the similarity matrices and movie dictionary
def load_pkl(file_path):
    with open(file_path, 'rb') as file:
        return pickle.load(file)

# Function to load and inspect a .pkl file
def inspect_pkl(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)

    # Check if it's a DataFrame or dict-like structure
    if isinstance(data, dict):
        data_df = pd.DataFrame.from_dict(data)
        print(f"Loaded {file_path} as DataFrame:")
        print(data_df.head())
    elif isinstance(data, pd.DataFrame):
        print(f"Loaded {file_path} as DataFrame:")
        print(data.head())
    else:
        print(f"Data in {file_path} is of type {type(data)}:")
        print(data)

# # List of .pkl files
# pkl_files = [
#     'Files/movies_dict.pkl',
#     'Files/movies2_dict.pkl',
#     'Files/new_df_dict.pkl',
#     'Files/similarity_tags_genres.pkl',
#     'Files/similarity_tags_keywords.pkl',
#     'Files/similarity_tags_tcast.pkl',
# ]

# # Inspect each file
# for file in pkl_files:
#     print(f"Inspecting: {file}")
#     inspect_pkl(file)
#     print("\n")
