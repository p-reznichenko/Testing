# Suno Full Generator (Offline)

Suno Full Generator is an offline toolkit for crafting rich music prompts, style descriptions, and lyrics without network access. It bundles a small Flask application that exposes a web interface for exploring combinations of emotions, instruments, and regional vocal techniques.

## Installation

1. Ensure Python 3.8+ is installed.
2. Install the required dependency:
   ```bash
   pip install flask
   ```

## Running

Launch the development server and open the interface in your browser:
```bash
python module1_patched.py
```
Then visit [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Major Features

- **Hybrid Prompt Generator** – Mixes emotions, instruments, regions, and sound‑effects to build Suno prompts with minimal typing.
- **World Vocal Atlas** – Maps regions to characteristic vocal techniques, allowing quick exploration of global singing styles.
- **Style Builder** – Normalizes style tags and augments them with co‑occurrence weights to produce a four‑sentence description and an "Exclude Styles" list.
- **Lyricist** – `/lyrics` endpoint and web panel transform raw ideas into polished, timeless lyrics while automatically filtering banned terms.

## Offline Datasets

The application ships with JSON datasets so it can operate completely offline:

- `suno-weights.json` – Base vocabulary of popular styles and their weights.
- `unified-suno-weights-expanded.json` – Extended style vocabulary and co‑occurrence weights used by the Style Builder and Flask client.

These files are loaded at runtime to populate suggestions and guide the Style Builder, allowing the entire workflow to function without internet access.


## Testing

Install the test dependencies and run the suite from the project root:

```bash
pip install pytest
pytest
```
