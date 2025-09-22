import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nlp import parse_resume, rank_resumes
def test_parse_resume_extracts_skills_and_experience():
    txt = "Experienced with Python, scikit-learn and SQL. 3 years experience."
    skills, exp = parse_resume(txt)
    assert "python" in [s.lower() for s in skills]
    assert any("3" in e for e in exp)

def test_rank_resumes_orders_by_similarity():
    jd = "We want Python, SQL, and scikit-learn for ML pipelines."
    r1 = "Python, SQL, scikit-learn, Pandas. Built ML pipelines."
    r2 = "Excel and Power BI dashboards."
    scores = rank_resumes(jd, [r1, r2])
    assert len(scores) == 2
    assert scores[0] > scores[1]