from recruitment_ranker import rank_candidates, load_weights, normalize_feature_map

# Load current weights (from weights.json)
weights = load_weights()

# Define a job requirement (feature levels 0–1)
job_req = {
    "Python": 1.0,
    "Machine Learning": 0.9,
    "Cloud Computing": 0.6,
    "SQL": 0.5,
    "Years of Experience": 0.7
}
job_req = normalize_feature_map(job_req)

# Define resumes (name, text)
resumes = [
    ("Alice", "5 years experience in Python, ML projects, SQL, AWS cloud."),
    ("Bob", "3 years experience in frontend, JavaScript, React, some DevOps."),
    ("Charlie", "2 years Python developer, good communication, certifications in ML."),
]

# Get top candidates
ranked = rank_candidates(resumes, job_req, weights, top_k=3)

# Print results
print("Ranking:")
for name, score in ranked:
    print(f"{name}: {score:.3f}")


max = 0
index = None
for i in range(len(ranked)):
    if ranked[i][1] > max:
        max = ranked[i][1]
        index = i

print(ranked[i])