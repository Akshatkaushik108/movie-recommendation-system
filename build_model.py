"""Reproduce the File2(TMDB) metadata and cosine-similarity model."""
from pathlib import Path
import ast
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent

def build_model():
    data = ROOT / 'TMDB movie Dataset'
    credits = pd.read_csv(data / 'tmdb_5000_credits.csv')
    movies = pd.read_csv(data / 'tmdb_5000_movies.csv')
    # Preserve the original notebook's title-based merge for reproducibility.
    movies = movies.merge(credits, on='title')
    movies = movies[['movie_id','title','overview','genres','keywords','cast','crew']].copy()
    for column in ['genres','keywords']:
        movies[column] = movies[column].apply(lambda value:[x['name'] for x in ast.literal_eval(value)])
    movies['cast'] = movies['cast'].apply(lambda value:[x['name'] for x in ast.literal_eval(value)[:3]])
    movies['crew'] = movies['crew'].apply(lambda value:[x['name'] for x in ast.literal_eval(value) if x['job']=='Director'])
    movies['tags'] = (movies['genres']+movies['keywords']+movies['cast']+movies['crew']).apply(lambda value:' '.join(value).lower())
    movies = movies[['movie_id','title','overview','tags']].reset_index(drop=True)
    vectors = TfidfVectorizer(stop_words='english').fit_transform(movies['tags'])
    similarities = cosine_similarity(vectors,vectors)
    target = ROOT / 'movie_data.pkl'
    with target.open('wb') as handle:
        pickle.dump((movies,similarities),handle,protocol=pickle.HIGHEST_PROTOCOL)
    print(f'Built {len(movies):,} rows for {movies.movie_id.nunique():,} distinct movie IDs: {target.name}')
    return movies,similarities

if __name__ == '__main__':
    build_model()
