# Example Ranking Session

This example uses the default GUI seed data and the current `weights.json` file.

## Job Requirements

| Feature | Requirement |
| --- | --- |
| Python | 1.0 |
| Machine Learning | 0.9 |
| Cloud Computing | 0.6 |
| SQL | 0.5 |
| Years of Experience | 0.7 |

## Candidates

1. **Alice** — "5 years experience in Python, ML projects, SQL, AWS cloud."
2. **Bob** — "3 years experience in frontend, JavaScript, React, some DevOps."
3. **Charlie** — "2 years Python developer, good communication, certifications in ML."

## Ranked Results

| Rank | Candidate | Score |
| --- | --- | --- |
| 1 | Alice | 0.169 |
| 2 | Charlie | 0.146 |
| 3 | Bob | 0.009 |

## How to Reproduce

1. Run `python Main.py`.
2. Keep the default job requirement values and candidate resumes.
3. Click **Rank Candidates**.

> Note: Scores will change if you update `weights.json`.
