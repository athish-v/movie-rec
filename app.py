import pickle
from flask import Flask, render_template, request, jsonify
from preprocess import read_csv_to_df, recommend, get_details, fetch_genres, recommend_by_cast, recommend_by_keywords, recommend_by_genres, load_pkl

app = Flask(__name__)
app = Flask(__name__, static_folder='static')


# Load data on startup
try:
    movies, new_df, _ = read_csv_to_df()
    # Fetch genres when the app starts
    genres = fetch_genres()
    mood_mapping = {
    "happy": ["Comedy", "Family", "Animation"],
    "sad": ["Drama", "Romance"],
    "adventurous": ["Action", "Adventure"],
    "excited": ["Thriller", "Horror", "Science Fiction"],
    "calm": ["Documentary", "Biography"]
    }

    # Load similarity matrices
    movies_dict = load_pkl('dataset/movies_dict.pkl')
    similarity_tags = pickle.load(open('dataset/similarity_tags_tags.pkl', 'rb'))
    similarity_tags_genres = pickle.load(open('dataset/similarity_tags_genres.pkl', 'rb'))
    similarity_tags_keywords = pickle.load(open('dataset/similarity_tags_keywords.pkl', 'rb'))
    similarity_tags_tcast = pickle.load(open('dataset/similarity_tags_tcast.pkl', 'rb'))
    similarity_tags_production_companies = pickle.load(open('dataset/similarity_tags_tprduction_comp.pkl', 'rb'))

    similarity_files = {
        "tags": similarity_tags,
        "genres": similarity_tags_genres,
        "keywords": similarity_tags_keywords,
        "tcast": similarity_tags_tcast,
        "tprduction_comp": similarity_tags_production_companies,
    }



    # Movie list (you can fetch this dynamically from your dataset)
    movie_list = new_df['title'].values.tolist()
    # Get recommendations
    # movie = "Inception"
    # rec = standard_rec(movie, new_df, similarity_files)

    # Print recommendations
    # for category, movies in rec.items():
    #     print(f"\nRecommendations based on {category.capitalize()}:")
    #     for m in movies:
    #         print(f"- {m}")

except Exception as e:
    print("Error loading data:", e)

@app.route('/')
def home():
    return render_template('index.html', movie_name=None, combined_recommendations=[], movies=movie_list)


# @app.route('/details/<movie_name>')
# def movie_details(movie_name):
#     details = get_details(movie_name)
#     if details is None:
#         return render_template('error.html', error="Movie details not found.")
#     return render_template('details.html', details=details)

@app.route('/details/<movie_name>')
def movie_details(movie_name):
    details = get_details(movie_name)
    if details is None:
        return render_template('error.html', error="Movie details not found.")
    return {
        "title": details[1],
        "overview": details[3],
        "release_date": details[4],
        "genres": details[2],
        "director": details[5],
        "cast": details[6],
        "poster": details[0],
    }


# 404 Error Handling
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error="Page not found"), 404

# @app.route('/recommend', methods=['GET', 'POST'])
# def recommendation():

#     if request.method == 'POST':
#         # Get the selected movie from the form
#         movie_name = request.form['movie']

#         try:
#             # Create a list to store all recommendations with their type
#             combined_recommendations = []

#             # Main recommendation based on tags
#             recommendations, posters = recommend(new_df, movie_name, 'dataset/similarity_tags_tags.pkl')

#             # Add recommendations for tags
#             combined_recommendations.extend(
#                 [{"movie_name": rec, "poster": poster, "type": "tags"} for rec, poster in zip(recommendations, posters)]
#             )

#             # Recommendations by Genres
#             genre_recommendations, genre_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_genres.pkl')   
#             combined_recommendations.extend(
#                 [{"movie_name": rec, "poster": poster, "type": "genres"} for rec, poster in zip(genre_recommendations, genre_posters)]
#             )

#             # Recommendations by Keywords
#             keyword_recommendations, keyword_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_keywords.pkl')
#             combined_recommendations.extend(
#                 [{"movie_name": rec, "poster": poster, "type": "keywords"} for rec, poster in zip(keyword_recommendations, keyword_posters)]
#             )

#             # Recommendations by Cast
#             cast_recommendations, cast_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_tcast.pkl')
#             combined_recommendations.extend(
#                 [{"movie_name": rec, "poster": poster, "type": "cast"} for rec, poster in zip(cast_recommendations, cast_posters)]
#             )

#             # Recommendations by Production Companies
#             production_recommendations, production_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_tprduction_comp.pkl')
#             combined_recommendations.extend(
#                 [{"movie_name": rec, "poster": poster, "type": "production_companies"} for rec, poster in zip(production_recommendations, production_posters)]
#             )


#             # Render the recommendations template
#             return render_template(
#                 'index.html',
#                 movie_name=movie_name,
#                 combined_recommendations=combined_recommendations,
#                 movies=movie_list
#             )

#         except Exception as e:
#             # Handle errors
#             print("Error Occurred:", str(e))
#             return render_template('error.html', error=str(e))


@app.route('/recommend', methods=['POST'])
def recommendation():
    if request.method == 'POST':
        # Get the selected movie from the form
        movie_name = request.form.get('movie', '')

        if not movie_name:
            return jsonify({"error": "No movie selected."}), 400

        try:
            # Create a list to store all recommendations with their type
            combined_recommendations = []

            # Main recommendation based on tags
            recommendations, posters = recommend(new_df, movie_name, 'dataset/similarity_tags_tags.pkl')
            combined_recommendations.append({
                "title": "Best Recommendations",
                "movies": [{"name": rec, "poster": poster} for rec, poster in zip(recommendations, posters)]
            })

            # Recommendations by Genres
            genre_recommendations, genre_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_genres.pkl')
            combined_recommendations.append({
                "title": "Recommendations Based on Same Genres",
                "movies": [{"name": rec, "poster": poster} for rec, poster in zip(genre_recommendations, genre_posters)]
            })

            # Recommendations by Keywords
            keyword_recommendations, keyword_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_keywords.pkl')
            combined_recommendations.append({
                "title": "Recommendations Based on Similar Keywords",
                "movies": [{"name": rec, "poster": poster} for rec, poster in zip(keyword_recommendations, keyword_posters)]
            })

            # Recommendations by Cast
            cast_recommendations, cast_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_tcast.pkl')
            combined_recommendations.append({
                "title": "Recommendations Based on the Cast",
                "movies": [{"name": rec, "poster": poster} for rec, poster in zip(cast_recommendations, cast_posters)]
            })

            # Recommendations by Production Companies
            production_recommendations, production_posters = recommend(new_df, movie_name, 'dataset/similarity_tags_tprduction_comp.pkl')
            combined_recommendations.append({
                "title": "Recommendations Based on the Same Production Companies",
                "movies": [{"name": rec, "poster": poster} for rec, poster in zip(production_recommendations, production_posters)]
            })

            # Return the recommendations as JSON
            return jsonify({
                "movie_name": movie_name,
                "recommendations": combined_recommendations
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    # Default page with no recommendations
    return render_template('index.html', movie_name=None, combined_recommendations=[], movies=movie_list)




if __name__ == "__main__":
    app.run(debug=True)
