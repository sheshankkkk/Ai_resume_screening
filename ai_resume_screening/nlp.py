import re
import math
from typing import Iterable, List, Tuple

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy small English model (run download once: python -m spacy download en_core_web_sm)
_nlp = spacy.load("en_core_web_sm")

# Simple skill lexicon (extend as needed)
_SKILL_TERMS = {
    "python","sql","scikit-learn","sklearn","pandas","numpy","tensorflow","pytorch",
    "nlp","spaCy","spacy","regex","tf-idf","tfidf","machine learning","data science",
    "flask","fastapi","streamlit","dash","airflow","tableau","power bi",
}

def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def parse_resume(text: str) -> Tuple[List[str], List[str]]:
    """
    Extract skills (lexicon-based + spaCy tokens) and experience mentions like '3 years'.
    Returns (skills, experience_mentions)
    """
    t = text.lower()
    skills = sorted({k for k in _SKILL_TERMS if k.lower() in t})

    # Heuristic: pick capitalized tech tokens from spaCy as potential skills
    doc = _nlp(text)
    caps = {tok.text for tok in doc if tok.is_title and len(tok.text) > 2}
    for c in caps:
        if c.lower() not in {"and","or","the","with","For","From","Team","Company"}:
            # Add capitalized tech names like 'Snowflake', 'React'
            if any(ch.isalpha() for ch in c):
                skills.add if isinstance(skills, set) else None

    # Rebuild skills as sorted set (ensure idempotence even if set op above no-op)
    skills = sorted(set(skills))

    # Experience mentions: '2 years', '3+ years'
    experience = re.findall(r"(\d+)\+?\s*years?", t)
    return skills, experience

def rank_resumes(jd_text: str, resumes: Iterable[str]) -> List[float]:
    """
    Returns list of similarity scores aligned with order of input resumes.
    """
    docs = [_normalize_ws(jd_text)] + [_normalize_ws(r) for r in resumes]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(docs)
    jd_vec = tfidf[0]
    resume_vecs = tfidf[1:]
    sims = cosine_similarity(jd_vec, resume_vecs)[0]
    # Guard: normalize to 0..1 if negative values (rare with cosine on tf-idf)
    mn, mx = float(min(sims)), float(max(sims)) if len(sims) else (0.0, 1.0)
    if mx - mn > 1e-9:
        sims = (sims - mn) / (mx - mn)
    return sims.tolist()