# Smart Recruitment Ranker

A lightweight AI-inspired recruitment ranking project that scores resumes against job requirements using feature extraction and weighted matching.

## Features

- Professional desktop GUI built with Tkinter
- Modernized UI styling with cleaner panels and typography
- Job requirement input for key hiring criteria
- Candidate resume text entry and instant ranking
- Top-candidate highlight with sorted scoring table
- Reusable ranking logic in `recruitment_ranker.py`

## Project Structure

- `Main.py` — GUI application entrypoint
- `recruitment_ranker.py` — ranking, feature extraction, and learning logic
- `weights.json` — current scoring weights
- `learner_weights.json` — learner-generated weights

## Requirements

- Python 3.10+
- `numpy`
- Tkinter support in Python (usually included in standard Python desktop installs)

Install dependencies:

```bash
pip install numpy
```

## Run the GUI

```bash
python Main.py
```

## How It Works

1. Enter job requirement levels (0.0 to 1.0) for selected features.
2. Add candidate names and resume text.
3. Click **Rank Candidates** to score and sort applicants.
4. Review the ranked table and top candidate.

## Example Output

See [`examples/example_run.md`](examples/example_run.md) for a neat end-to-end example of inputs and ranked results.

## Notes

- Scores are based on weighted feature matching between resume content and job requirements.
- You can tune the scoring behavior by updating `weights.json`.
