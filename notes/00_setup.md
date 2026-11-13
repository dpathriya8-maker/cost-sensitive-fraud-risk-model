# Step 0: Project setup (11 Nov 2026)

## What we made and why
| File / folder | Plain meaning | Why it exists |
|---|---|---|
| `README.md` | the project's front page (Markdown text) | an interviewer or GitHub visitor understands the project in 1 minute |
| `requirements.txt` | list of libraries, one per line | anyone (or Docker) can install everything with `pip install -r requirements.txt` |
| `.gitignore` | list of files Git must skip | 1.3 GB data and model files must never go to GitHub |
| `.gitkeep` | an empty placeholder file | Git ignores empty folders, so this keeps the folder in the repo |
| `src/__init__.py` | an empty file that marks `src` as a Python *package* | lets the API write `from src.features import ...` |
| `data/raw` vs `data/processed` | original data vs data we changed | never overwrite raw data, so you can always rebuild from scratch |
| `reports/metrics.json` (later) | numbers saved by code | your interview numbers come from a file, not from memory |

## Names & syntax
- **Markdown (`.md`)**: plain text with simple formatting: `#` = heading, `|` = table, `- [ ]` = checkbox.
- **package**: a folder of `.py` files you can import from, like `import pandas`, but your own.
- **`pip install -r file`**: `-r` means "read the library names from this file".

## Interview line
"I structured it like a production ML repo: notebooks for exploration, a `src/` package for the
reusable feature and prediction code that the FastAPI service imports, data and models kept out of
Git, and every reported metric written by code to `reports/`."

## Kaggle vs laptop
Kaggle runs the heavy steps (590K rows, about 30 GB RAM, free). The laptop runs samples, the API and Docker.
Notebooks auto-detect where they run (Step 1 explains the setup cell line by line).
