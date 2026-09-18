import os
from pathlib import Path
import pickle
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

import numpy as np
import pandas as pd

from movie_utils import ROOT, fetch_movie_poster, load_model, recommend_movies


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.movies = pd.DataFrame({
            'movie_id': [1, 2, 2, 3, 4],
            'title': ['Selected', 'Second', 'Second duplicate', 'Third', 'Fourth']})
        self.similarities = np.array([
            [1., 1., 1., .8, .2],
            [1., 1., 1., .8, .2],
            [1., 1., 1., .8, .2],
            [.8, .8, .8, 1., .5],
            [.2, .2, .2, .5, 1.]])

    def test_excludes_self_and_duplicate_ids_on_ties(self):
        result = recommend_movies(self.movies, self.similarities, 'Second')
        self.assertEqual(result.movie_id.tolist(), [1, 3, 4])

    def test_ranking_and_limit(self):
        result = recommend_movies(self.movies, self.similarities, 'Fourth', 2)
        self.assertEqual(result.movie_id.tolist(), [3, 1])

    def test_unknown_title_and_zero_limit(self):
        self.assertTrue(recommend_movies(self.movies, self.similarities, 'Missing').empty)
        self.assertTrue(recommend_movies(self.movies, self.similarities, 'Selected', 0).empty)

    def test_model_dimension_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / 'model.pkl'
            model.write_bytes(pickle.dumps((self.movies, np.eye(2))))
            with self.assertRaisesRegex(ValueError, 'dimensions'):
                load_model(model)

    def test_missing_model_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / 'model.pkl'
            model.write_bytes(pickle.dumps((pd.DataFrame({'name': ['A']}), np.eye(1))))
            with self.assertRaisesRegex(ValueError, 'columns'):
                load_model(model)


class PosterTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    @patch('movie_utils.urlopen')
    def test_no_key_never_requests_network(self, request):
        self.assertTrue(Path(fetch_movie_poster(1)).is_file())
        request.assert_not_called()

    @patch.dict(os.environ, {'TMDB_API_KEY': 'test-placeholder'}, clear=True)
    @patch('movie_utils.urlopen', side_effect=URLError('offline'))
    def test_network_failure_returns_local_image(self, request):
        self.assertEqual(fetch_movie_poster(1), str(ROOT / 'assets/no-poster.png'))


@unittest.skipUnless((ROOT / 'movie_data.pkl').exists(), 'Build local model to run integration checks')
class SavedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.movies, cls.similarities = load_model()

    def test_real_movie_recommendations(self):
        for title in ['Avatar', 'The Dark Knight Rises', 'Toy Story']:
            with self.subTest(title=title):
                result = recommend_movies(self.movies, self.similarities, title)
                self.assertEqual(len(result), 10)
                self.assertEqual(result.movie_id.nunique(), 10)
                selected_id = self.movies.loc[self.movies.title == title, 'movie_id'].iloc[0]
                self.assertNotIn(selected_id, result.movie_id.tolist())


if __name__ == '__main__':
    unittest.main()
