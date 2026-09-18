# Movie Recommendation System

A final-year project that recommends similar movies using TMDB metadata, TF-IDF and cosine similarity. Two Streamlit interfaces offer movie selection and poster cards; the main interface also supports an optional conversational assistant.

## Features

- Select a movie and discover up to 10 similar, distinct films.
- Rank movies using genres, keywords, the first three cast members and directors.
- Display TMDB posters when an API key is configured, with a local placeholder otherwise.
- Use the recommender without an external AI service; enable chat separately if desired.

## Which notebook is connected?

**`File2(TMDB).ipynb` is the notebook used by this project.** It reads the two TMDB CSV files and writes `movie_data.pkl`, containing the processed movie table and similarity matrix. Both `agent_final.py` and `app_enhanced_ui.py` read that generated file. The apps do not execute a notebook at runtime.

The older `file1.ipynb` reads a different dataset into `df`, later refers to the undefined variable `movies_data`, and does not export the model consumed by the apps. It is omitted from this repository.

The original File2 preprocessing was run and compared with the supplied model: the table contents match, with **4,809 rows representing 4,803 distinct movie IDs** and a **4,809 × 4,809** similarity matrix. File2 merges the CSVs on title, so duplicate titles produce additional rows. This behavior is retained for reproducibility; recommendation results exclude the selected movie and repeated movie IDs.

## Run locally

Use Python 3.11 or 3.12. In a terminal opened at the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python build_model.py
python -m streamlit run agent_final.py
```

On macOS/Linux, activate with `source .venv/bin/activate`.

For the simpler interface:

```powershell
python -m streamlit run app_enhanced_ui.py
```

`build_model.py` reproduces the notebook's preprocessing and similarity calculation. Alternatively, install JupyterLab (`python -m pip install jupyterlab`), launch it from the repository root and run every cell in `File2(TMDB).ipynb` in order.

The original generated model is approximately **187 MB**, above GitHub's 100 MB per-file limit. It is intentionally excluded and rebuilt locally. Building the dense similarity matrix requires several hundred MB of available memory.

## Optional posters and chat

Copy `.env.example` to `.env`. Set `TMDB_API_KEY` to your own TMDB API key for posters. Without it, recommendations still work with placeholder images.

For chat, install the optional dependencies:

```powershell
python -m pip install -r requirements-chat.txt
```

Set `OPENAI_API_KEY`, `OPENAI_BASE_URL` and `OPENAI_MODEL` for your chosen compatible provider, then restart Streamlit. The endpoint and key must belong to the same provider. Chat sends the conversation and any matched recommendations to that configured service and may incur provider charges. Chat remains disabled when it is not configured; no key is needed for the local recommender.

Keep `.env` private. No working credentials are included in this repository.

## Project structure

```text
agent_final.py             Main Streamlit interface with optional chat
app_enhanced_ui.py         Simpler recommendation interface
File2(TMDB).ipynb          Original connected preprocessing notebook, cleaned
build_model.py            Command-line model builder
movie_utils.py            Shared loading, ranking and poster helpers
TMDB movie Dataset/       The two source CSV files
assets/no-poster.png       Offline poster fallback
tests/                    Recommendation and fallback checks
```

## How recommendations work

```text
TMDB movies + credits → title merge → metadata tags
    → TF-IDF vectors → cosine similarity → movie_data.pkl
    → Streamlit movie selection → ranked recommendations
```

The overview is retained in the processed table but is not part of the vectorized tags. Recommendations are content-based, with no user ratings or viewing history. Optional chat is a separate language-model feature. The project does not claim a measured recommendation accuracy or live popularity ranking.

The included CSVs are the TMDB 5000 movies/credits files supplied with the original project. Movie metadata and images remain subject to their source terms; this project is not endorsed or certified by TMDB. Dataset provenance and redistribution terms should be checked before broader redistribution.

## Validation

```powershell
python -m unittest discover -s tests -v
```

Tests cover ranking order, similarity ties, duplicate IDs, unknown titles, model shape validation and poster fallback behavior without external calls. If `movie_data.pkl` exists, additional checks exercise recommendations against that local model.

Repository preparation verified the original File2 table against the supplied model, checked matrix dimensions, symmetry and finite values, and reproduced File1's undefined-variable failure. Python files and notebook code cells were syntax-checked. Full Streamlit execution and a fresh scikit-learn model build could not be tested in the preparation environment because dependency downloads were blocked; these remain runtime verification steps.

Reports, presentation files, videos, `agent.py`, `app.py`, the obsolete notebook and the generated model are excluded. Original project files are preserved separately.
