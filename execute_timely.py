import os
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, date
from pymongo import MongoClient
from urllib.parse import quote_plus
from collections import Counter
import zipfile
username = os.environ.get('MONGODB_USERNAME')
password = os.environ.get('MONGODB_PASSWORD')
def get_updated_data_from_kaggle_each_day(destination_dir='./'):
    #Kaggle
    os.system(f'kaggle datasets download -d alanvourch/tmdb-movies-daily-updates -p {destination_dir}')

    extracted_files = os.listdir(destination_dir)
    print("Contents of the destination directory:")
    print(extracted_files)

    zip_files = [file for file in extracted_files if file.endswith('.zip')]

    if not zip_files:
        print("No zip file found in the destination directory.")
        return None

    # Contents of zip
    zip_file_path = os.path.join(destination_dir, zip_files[0])
    extracted_dir_path = os.path.join(destination_dir, 'tmdb-movies-daily-updates')
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_dir_path)

    extracted_files = os.listdir(extracted_dir_path)
    print("Contents of the extracted directory:")
    print(extracted_files)

    csv_files = [file for file in extracted_files if file.endswith('.csv')]

    if not csv_files:
        print("No CSV file found in the extracted directory.")
        return None
    csv_file_path = os.path.join(extracted_dir_path, csv_files[0])
    df = pd.read_csv(csv_file_path)

    return df


#get_upcoming_movies
def get_upcoming_movies(df):
  escaped_username = quote_plus(username)
  escaped_password = quote_plus(password)

  uri = f"mongodb+srv://{escaped_username}:{escaped_password}@dishacluster.q3eiurk.mongodb.net/"

# Connect to MongoDB
  client = MongoClient(uri)
  mydb = client["4cinephile"]
  mycol = mydb["tempdata"]
  current_date = date.today().isoformat()
  sorted_movies = df.sort_values(by='release_date', ascending=False)
  sorted_movies = sorted_movies.dropna()
  sorted_movies['release_date'] = sorted_movies['release_date'].astype(str)
  upcoming_movies = sorted_movies[sorted_movies['release_date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").year)  > datetime.now().year]
  upcoming_movies = upcoming_movies["title"].to_list()
  mydict = {
        "date" : current_date,
        "func_name": "get_upcoming_movies",
        "data": upcoming_movies
  }
  mycol.insert_one(mydict)
  return upcoming_movies;


#get_count_by_genres
def get_movies_count_by_genre(df):


  escaped_username = quote_plus(username)
  escaped_password = quote_plus(password)

  uri = f"mongodb+srv://{escaped_username}:{escaped_password}@dishacluster.q3eiurk.mongodb.net/"

# Connect to MongoDB
  client = MongoClient(uri)
  mydb = client["4cinephile"]
  mycol = mydb["tempdata"]
  current_date = date.today().isoformat()
  genre_df = df['genres']
  genre_df.dropna(inplace=True)
  genre_df = pd.DataFrame(genre_df, columns = ['genres'])
  #print(genre_df)
  genre_df['genres'] = genre_df['genres'].apply(lambda x : x.split(', '))
  genre_frequency = Counter(g for genres in genre_df['genres'] for g in genres)
  # print(genre_frequency.most_common(5))
  df_genre = pd.DataFrame([genre_frequency]).T.reset_index()
  df_genre.columns = ['genre', 'count']
  genre_names = df_genre["genre"].to_list()
  count = df_genre["count"].to_list()
  mydict = {
      "date" : current_date,
      "func_name" : "get_movies_count_by_genre",
      "names" : genre_names,
      "count" : count
  }
  mycol.insert_one(mydict)
  return df_genre


df = get_updated_data_from_kaggle_each_day()
get_upcoming_movies(df)
get_movies_count_by_genre(df)