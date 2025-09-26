# recruitment_ranker.py

import json
import math
import random
import os
from typing import Dict, List, Tuple
import numpy as np

WEIGHTS_FILE = "weights.json"


# -----------------------
# Feature utilities
# -----------------------
DEFAULT_FEATURES = [
    "Python",
    "Machine Learning",
    "Data Structures",
    "Algorithms",
    "Cloud Computing",
    "AWS",
    "GCP",
    "Azure",
    "SQL",
    "NoSQL",
    "Communication",
    "Leadership",
    "Years of Experience",
    "Certifications",
    "Frontend",
    "Backend",
    "DevOps",
    "Testing",
    "Docker",
    "Kubernetes",
]

def init_weights(features: List[str], seed: int = 0) -> Dict[str, float]:
    """Initialize weights (positive and normalized)."""
    random.seed(seed)
    raw = {f: random.random() + 0.1 for f in features}  # avoid zeros
    total = sum(raw.values())
    return {f: raw[f]/total for f in features}

def save_weights(weights: Dict[str, float], filename: str = WEIGHTS_FILE):
    with open(filename, "w") as fh:
        json.dump(weights, fh, indent=2)

def load_weights(filename: str = WEIGHTS_FILE, fallback: List[str] = None) -> Dict[str, float]:
    if os.path.exists(filename):
        with open(filename, "r") as fh:
            return json.load(fh)
    if fallback is None:
        fallback = DEFAULT_FEATURES
    w = init_weights(fallback)
    save_weights(w, filename)
    return w

# -----------------------
# Feature extraction (simple)
# -----------------------
def extract_features_from_resume_text(text: str, feature_list: List[str]) -> Dict[str, float]:
    """
    Very simple extractor:
      - looks for skill token presence (case-insensitive)
      - Years of Experience: looks for "X years" pattern
    Returns feature-levels in range [0, 1].
    """
    t = text.lower()
    feats = {}
    for f in feature_list:
        key = f.lower()
        if key == "years of experience":
            # simple heuristics: find "X year" or "X years"
            years = 0.0
            tokens = t.replace(",", " ").split()
            for i, tok in enumerate(tokens):
                if tok.isdigit():
                    # check if next token is 'year' or 'years'
                    if i+1 < len(tokens) and tokens[i+1].startswith("year"):
                        years = float(tok)
                        break
            # map years to 0-1 (cap at 10 years)
            feats[f] = min(years/10.0, 1.0)
        else:
            # presence and simple strength by counting occurrences
            cnt = t.count(key)
            # also check for common abbreviations: ML -> machine learning
            if key == "machine learning":
                cnt += t.count("ml")
            # map count to 0-1 (cap threshold 3)
            feats[f] = min(cnt / 3.0, 1.0)
    return feats

def normalize_feature_map(m: Dict[str, float]) -> Dict[str, float]:
    """Optional: ensure all values in [0,1] and present for all keys."""
    return {k: max(0.0, min(1.0, float(v))) for k, v in m.items()}


# -----------------------
# Scoring
# -----------------------
def calculate_score(resume_feats: Dict[str, float],
                    job_req_feats: Dict[str, float],
                    weights: Dict[str, float]) -> float:
    """
    Score = sum_over_features( weight[f] * match_level[f] )
    match_level = min(candidate_level, job_required_level)  (so exceeding req doesn't always add)
    """
    s = 0.0
    for f, w in weights.items():
        r_lvl = resume_feats.get(f, 0.0)
        j_req = job_req_feats.get(f, 0.0)
        match = min(r_lvl, j_req)
        s += w * match
    return float(s)


# -----------------------
# Simple reinforcement-style weight updater
# -----------------------
def update_weights_reinforcement(weights: Dict[str, float],
                                 resume_feats: Dict[str, float],
                                 hired: bool,
                                 learning_rate: float = 0.03) -> Dict[str, float]:
    """
    For each feature present in resume, increase (if hired) or decrease (if not).
    Then renormalize to sum=1.
    """
    w = dict(weights)  # copy
    for f in w.keys():
        presence = resume_feats.get(f, 0.0)
        if presence <= 0:
            continue
        if hired:
            w[f] += learning_rate * presence
        else:
            w[f] = max(1e-8, w[f] - learning_rate * presence)
    # renormalize
    total = sum(w.values()) or 1.0
    for f in w:
        w[f] = w[f] / total
    return w


# -----------------------
# Online logistic regression (SGD) for weight learning
# -----------------------
class OnlineLogisticLearner:
    """
    Learns weights w for predicting P(hired=1 | x) = sigmoid(w · x)
    - Uses L2 regularization (lambda_reg)
    - Updates with SGD per example
    """

    def __init__(self, feature_list: List[str], lr: float = 0.5, lambda_reg: float = 1e-3):
        self.features = list(feature_list)
        self.lr = lr
        self.lambda_reg = lambda_reg
        self.w = np.array([0.0] * len(self.features), dtype=float)  # raw weights
        # small random init to break symmetry
        self.w += 0.01 * np.random.randn(len(self.w))

    def _to_vector(self, feature_map: Dict[str, float]) -> np.ndarray:
        v = np.array([feature_map.get(f, 0.0) for f in self.features], dtype=float)
        return v

    @staticmethod
    def _sigmoid(x):
        # numerically stable sigmoid
        return 1.0 / (1.0 + np.exp(-x))

    def predict_proba(self, feature_map: Dict[str, float]) -> float:
        x = self._to_vector(feature_map)
        return float(self._sigmoid(np.dot(self.w, x)))

    def predict_label(self, feature_map: Dict[str, float], thresh: float = 0.5) -> int:
        return 1 if self.predict_proba(feature_map) >= thresh else 0

    def update(self, feature_map: Dict[str, float], label: int):
        """
        One step of SGD on negative log-likelihood:
        grad = (label - p) * x - lambda_reg * w
        w += lr * grad
        """
        x = self._to_vector(feature_map)
        p = self._sigmoid(np.dot(self.w, x))
        grad = (label - p) * x - self.lambda_reg * self.w
        self.w += self.lr * grad

    def get_weights_dict(self) -> Dict[str, float]:
        # convert raw weights to positive normalized importance scores
        raw = np.maximum(0.0, self.w)  # clip negatives to 0 (we want nonnegative importances)
        s = raw.sum() + 1e-12
        normalized = raw / s
        return {f: float(normalized[i]) for i, f in enumerate(self.features)}

    def load_weights_from_dict(self, d: Dict[str, float]):
        """Optional: set internal w proportional to given importance dict"""
        arr = np.array([d.get(f, 0.0) for f in self.features], dtype=float)
        # map back to constructor scale: invert normalization (set w = logit of arr)
        # avoid zero entries
        arr = np.clip(arr, 1e-6, 1.0 - 1e-6)
        # approximate logit mapping; for small arr => negative; use log(arr/(1-arr))
        self.w = np.log(arr / (1.0 - arr))

# -----------------------
# Simple persistence wrapper for online learner & reinforcement weights
# -----------------------
def persist_json(obj, filename):
    with open(filename, "w") as fh:
        json.dump(obj, fh, indent=2)

def load_json(filename):
    with open(filename, "r") as fh:
        return json.load(fh)


# -----------------------
# Demo / Simulation
# -----------------------
def demo_simulation():
    print("=== Demo: Recruitment ranking + online updates ===")
    features = DEFAULT_FEATURES.copy()
    # initialize weights (or load)
    if os.path.exists(WEIGHTS_FILE):
        print(f"Loading weights from {WEIGHTS_FILE}")
        weights = load_weights(WEIGHTS_FILE, fallback=features)
    else:
        weights = init_weights(features)
        save_weights(weights, WEIGHTS_FILE)
        print(f"Initialized and saved weights to {WEIGHTS_FILE}")

    print("Initial weights (top 8):")
    for k, v in sorted(weights.items(), key=lambda kv: -kv[1])[:8]:
        print(f"  {k}: {v:.3f}")
    print()

    # define a job
    job = {
        "Python": 1.0,
        "Machine Learning": 0.9,
        "Data Structures": 0.6,
        "Algorithms": 0.6,
        "Cloud Computing": 0.5,
        "Years of Experience": 0.6,
        "SQL": 0.6,
    }
    job = normalize_feature_map(job)

    # some example resumes (text)
    resumes_text = [
        # strong ML candidate
        ("Resume A", "5 years experience in Python, Machine Learning (ML), deep learning, python python. SQL. "
                     "Worked with AWS, Docker, Kubernetes. Has certifications."),
        # strong backend/data structures
        ("Resume B", "3 years experience in backend, algorithms, data structures, python, sql, testing."),
        # frontend/devops
        ("Resume C", "4 years experience in frontend, javascript, communication, leadership, docker, devops."),
        # junior ML but strong communication
        ("Resume D", "1 year experience. ML projects, communication, python. Certification in ML."),
    ]

    # create online learner
    learner = OnlineLogisticLearner(features, lr=0.8, lambda_reg=1e-3)
    # optionally seed learner weights from current importance
    learner.load_weights_from_dict(weights)

    # convert resumes into feature maps and score them, then simulate hiring decisions
    # We'll simulate hiring label based on a hidden "ground truth" scoring that favors ML & Python.
    def hidden_hiring_decision(resume_map: Dict[str, float]) -> int:
        # hidden weights (unknown to learner) - prefer Python & ML & experience
        hidden = {
            "Python": 1.5,
            "Machine Learning": 2.0,
            "Years of Experience": 1.0,
            "SQL": 0.5
        }
        score = 0.0
        for f, v in resume_map.items():
            score += hidden.get(f, 0.0) * v
        # threshold
        return 1 if score >= 1.5 else 0

    # simulate streaming decisions and updates
    print("Simulating 30 candidate arrivals with online updates...\n")
    for i in range(30):
        name, text = random.choice(resumes_text)
        resume_map = extract_features_from_resume_text(text, features)
        resume_map = normalize_feature_map(resume_map)
        # score with current weights (reinforcement weights)
        score = calculate_score(resume_map, job, weights)
        # learner predicted proba
        pred_p = learner.predict_proba(resume_map)

        # hidden real hiring decision (simulated HR)
        true_lbl = hidden_hiring_decision(resume_map)

        # Print every few iterations
        if i % 6 == 0:
            print(f"Iter {i:02d}: {name} | score={score:.3f} | modelP={pred_p:.3f} | true={true_lbl}")

        # Update both systems:
        # 1) Reinforcement style (imitates quick business rule)
        weights = update_weights_reinforcement(weights, resume_map, hired=bool(true_lbl), learning_rate=0.02)

        # 2) Online logistic learner (SGD)
        learner.update(resume_map, true_lbl)

    # show final learned importances from the online learner
    learned_importance = learner.get_weights_dict()
    print("\nFinal learned importances (top 8):")
    for k, v in sorted(learned_importance.items(), key=lambda kv: -kv[1])[:8]:
        print(f"  {k}: {v:.3f}")

    # show final reinforcement weights top values
    print("\nFinal reinforcement weights (top 8):")
    for k, v in sorted(weights.items(), key=lambda kv: -kv[1])[:8]:
        print(f"  {k}: {v:.3f}")

    # save both
    print("\nSaving reinforcement weights ->", WEIGHTS_FILE)
    save_weights(weights, WEIGHTS_FILE)
    print("Saving learner weights -> learner_weights.json")
    persist_json(learned_importance, "learner_weights.json")

    print("\nDemo complete. You can now use calculate_score() with updated weights, or load learner_weights.json for ML-driven importances.")


# -----------------------
# Small API for external usage (example)
# -----------------------
def rank_candidates(resume_texts: List[Tuple[str,str]],
                    job_req: Dict[str, float],
                    weights: Dict[str, float],
                    top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Resume_texts: list of (candidate_name, resume_text)
    job_req: feature->required-level (0-1)
    weights: current importance mapping
    Returns list of (candidate_name, score) sorted desc
    """
    result = []
    for name, text in resume_texts:
        feats = extract_features_from_resume_text(text, list(weights.keys()))
        feats = normalize_feature_map(feats)
        score = calculate_score(feats, job_req, weights)
        result.append((name, score))
    result.sort(key=lambda x: -x[1])
    return result[:top_k]


# -----------------------
# If run as script -> demo
# -----------------------
if __name__ == "__main__":
    demo_simulation()
