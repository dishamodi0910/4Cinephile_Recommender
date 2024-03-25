from flask import Flask, jsonify
import joblib
import pandas as pd
from scipy.sparse import load_npz
from flask_cors import CORS
from urllib.parse import quote_plus
from flask import request
import movieposters as mp

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello World'
 
movie_dataset = pd.read_parquet('./movie_database.parquet')
mat = load_npz('./utility_matrix.npz')
user_index = joblib.load('./user_index.pkl')
index_user = joblib.load('./index_user.pkl')
movie_index = joblib.load('./movie_index.pkl')
index_movie = joblib.load('./index_movie.pkl')
model = joblib.load('./Recommendation_System.sav')
movie_title = 'Sabrina (1995)'

@app.route('/recommendations/')
def get_recommendations(k=11):
    movie_title = request.args.get('search', '')
    print("Movie title is : ",movie_title);
    titleofmovie = dict(zip(movie_dataset['title'], movie_dataset['movieId']))
    titleofmovie_new = dict(zip(movie_dataset['movieId'], movie_dataset['title']))
    movie_id = titleofmovie[movie_title]
    mat_transpose = mat.T
    nearest_k_ids = []
    nearest_movie_name = []
    movieIdx = movie_index[movie_id]
    movie_vec = mat_transpose[movieIdx]
    neighbour = model.kneighbors(movie_vec, return_distance=False)
    for i in range(0,k):
        n = neighbour.item(i)
        nearest_k_ids.append(index_movie[n])
        nearest_movie_name.append(titleofmovie_new[index_movie[n]])
        #link = mp.get_poster(title=titleofmovie_new[index_movie[n]])
        #print(link);
    nearest_k_ids.pop(0)
    nearest_movie_name.pop(0)
    return jsonify({'recommendations': nearest_movie_name})

if __name__ == '__main__':
    app.run(debug=True)