"""Shared model loading, ranking and optional TMDB posters."""
from pathlib import Path
import json
import os
import pickle
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np

ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv(ROOT / '.env', override=False)

def load_model(path=None):
    """Load the local cache created by the notebook or build_model.py."""
    with Path(path or ROOT / 'movie_data.pkl').open('rb') as handle:
        movies, similarities = pickle.load(handle)
    if not {'title', 'movie_id'}.issubset(movies.columns):
        raise ValueError('The model must contain title and movie_id columns.')
    if similarities.shape != (len(movies), len(movies)):
        raise ValueError('Movie rows and similarity matrix dimensions do not match.')
    return movies.reset_index(drop=True), similarities

def recommend_movies(movies, similarities, title, limit=10):
    """Rank distinct movies while excluding the selected film, even on ties."""
    matches = np.flatnonzero(movies['title'].to_numpy() == title)
    if not len(matches) or limit <= 0:
        return movies.iloc[0:0][['title', 'movie_id']].copy()
    selected = int(matches[0])
    selected_id = movies.iloc[selected]['movie_id']
    seen = {selected_id}
    indices = []
    for candidate in np.argsort(-np.asarray(similarities[selected]), kind='stable'):
        movie_id = movies.iloc[int(candidate)]['movie_id']
        if movie_id in seen:
            continue
        seen.add(movie_id)
        indices.append(int(candidate))
        if len(indices) >= limit:
            break
    return movies.iloc[indices][['title', 'movie_id']].copy()

def fetch_movie_poster(movie_id, size='w500'):
    """Return a TMDB poster URL, or a local placeholder when unavailable."""
    placeholder = str(ROOT / 'assets/no-poster.png')
    key = os.getenv('TMDB_API_KEY')
    if not key:
        return placeholder
    try:
        movie_id = int(movie_id)
        if size not in {'w185', 'w500'}:
            return placeholder
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?' + urlencode({'api_key':key})
        request = Request(url, headers={'Accept':'application/json'})
        with urlopen(request, timeout=5) as response:
            poster = json.load(response).get('poster_path')
        if isinstance(poster,str) and poster.startswith('/') and not poster.startswith('//'):
            return f'https://image.tmdb.org/t/p/{size}{poster}'
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError):
        pass
    return placeholder
