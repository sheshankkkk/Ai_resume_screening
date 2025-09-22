import os
import io
from pathlib import Path
import streamlit as st
import pdfplumber
import docx2txt
import pandas as pd

from db import init_db, insert_job, insert_resume, insert_result
from nlp import parse_resume, rank_resumes

# -------- Setup --------
init_db()
st.set_page_config(page_title="AI Resume Screening", page_icon="📄", layout="wide")
st.title("📄 AI Resume Screening System")

@st.cache_data(show_spinner=False)
def read_file_to_text(uploaded) -> str:
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        with pdfplumber.open(uploaded) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)
    if name.endswith(".docx"):
        return docx2txt.process(uploaded)
    return uploaded.read().decode("utf-8", errors="ignore")

# -------- JD Input --------
st.header("1) Job Description")
jd_col1, jd_col2 = st.columns([2,1])
with jd_col1:
    jd_text = st.text_area("Paste JD text", height=180, placeholder="Paste job description here...")
with jd_col2:
    jd_file = st.file_uploader("Or upload JD (PDF/DOCX/TXT)", type=["pdf","docx","txt"], key="jd_up")
    if jd_file:
        try:
            jd_text = read_file_to_text(jd_file)
            st.success(f"Loaded JD from {jd_file.name}")
        except Exception as e:
            st.error(f"Failed to read JD: {e}")

# -------- Resume Input --------
st.header("2) Resumes")
resume_files = st.file_uploader("Upload resumes (PDF/DOCX/TXT)", type=["pdf","docx","txt"], accept_multiple_files=True)

resumes = []
if resume_files:
    for f in resume_files:
        try:
            txt = read_file_to_text(f)
            resumes.append({"name": f.name, "text": txt})
        except Exception as e:
            st.warning(f"Skipping {f.name}: {e}")

st.info(f"Selected {len(resumes)} resume(s).")

# -------- Screening --------
st.header("3) Screening")
if st.button("⚙️ Run Screening", type="primary"):
    if not jd_text.strip():
        st.warning("Please provide a job description.")
    elif not resumes:
        st.warning("Please upload at least one resume.")
    else:
        # Save JD
        jd_id = insert_job("Job", jd_text)

        # Parse + store resumes
        for r in resumes:
            skills, exp = parse_resume(r["text"])
            insert_resume(r["name"], r["text"], skills, exp, jd_id)

        # Rank
        scores = rank_resumes(jd_text, [r["text"] for r in resumes])

        # Build results DataFrame
        rows = []
        for r, s in zip(resumes, scores):
            rows.append({"candidate": r["name"], "score": float(s)})

        # Sort by score desc and add rank
        df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", range(1, len(df)+1))

        # Save to DB results table
        for _, row in df.iterrows():
            insert_result(jd_id, str(row["candidate"]), float(row["score"]))

        st.success("Screening complete!")
        st.subheader("Results")
        st.dataframe(df, use_container_width=True)

        # ---------- Export to CSV ----------
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Ranked Results (CSV)",
            data=csv_bytes,
            file_name="ranked_candidates.csv",
            mime="text/csv"
        )

        # Preview top candidates
        with st.expander("Preview top candidates (first 300 chars each)"):
            for _, row in df.head(5).iterrows():
                name = row["candidate"]
                text = next((x["text"] for x in resumes if x["name"] == name), "")
                st.markdown(f"**{name}** — Score: {row['score']:.3f}")
                st.text((text or "")[:300] + ("..." if len(text) > 300 else ""))