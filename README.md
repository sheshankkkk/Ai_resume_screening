AI-Powered Resume Screening System

An end-to-end AI tool for automating candidate shortlisting. This system uses Natural Language Processing (NLP) to parse resumes, extract skills and experience, and rank candidates against job descriptions — all through a clean web dashboard built with Streamlit.

⸻

Features
	•	Upload Resumes (TXT, PDF, DOCX) and Job Descriptions
	•	NLP-powered parsing of skills, entities, and experience (spaCy)
	•	Candidate Ranking using TF-IDF + cosine similarity (scikit-learn)
	•	Database support with SQLite to store resumes, job descriptions, and results
	•	Download ranked candidates as CSV
	•	Unit-tested NLP pipeline (Pytest)

⸻

Tech Stack
	•	Python 3.12+
	•	Streamlit → Web interface
	•	spaCy → NLP parsing
	•	scikit-learn → Vectorization + similarity scoring
	•	SQLite → Resume & JD storage
	•	PDFPlumber / docx2txt → Resume parsing
	•	Pytest → Testing
 
Usage Workflow
	1.	Upload a Job Description (paste text or upload file).
	2.	Upload resumes (multiple files supported).
	3.	Click ⚙️ Run Screening.
	4.	View ranked candidates with similarity scores.
	5.	Download results as CSV.
