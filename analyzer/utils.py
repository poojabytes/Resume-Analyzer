"""Resume analysis helpers with lightweight dependencies for Vercel."""
from __future__ import annotations

import math
import re
from collections import Counter

from docx import Document
from pypdf import PdfReader


class TextExtractor:
    @staticmethod
    def extract_from_pdf(file_path):
        try:
            reader = PdfReader(file_path)
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"

    @staticmethod
    def extract_from_docx(file_path):
        try:
            doc = Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}"


class TextPreprocessor:
    STOP_WORDS = {
        "the", "and", "for", "with", "that", "this", "from", "your", "have", "are",
        "was", "were", "will", "would", "could", "should", "about", "into", "over",
        "under", "their", "there", "them", "then", "than", "also", "such", "only",
    }

    def clean_text(self, text):
        text = (text or "").lower()
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        tokens = [t for t in text.split() if t not in self.STOP_WORDS and len(t) > 2]
        return " ".join(tokens)


class SkillExtractor:
    def __init__(self):
        self.skills_database = [
            "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go",
            "swift", "kotlin", "html", "css", "react", "angular", "vue", "nodejs", "express",
            "django", "flask", "spring", "laravel", "bootstrap", "jquery", "sql", "mysql",
            "postgresql", "mongodb", "redis", "aws", "azure", "gcp", "docker", "kubernetes",
            "git", "linux", "fastapi", "rest", "graphql", "machine learning", "deep learning",
            "nlp", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "tailwind",
            "nextjs", "nestjs", "prisma", "selenium", "jest", "cypress", "jira", "agile",
        ]

    def extract_skills(self, text):
        cleaned = (text or "").lower()
        found = []
        for skill in self.skills_database:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(pattern, cleaned):
                found.append(skill)
        return sorted(set(found))


class SimilarityCalculator:
    def __init__(self):
        self.preprocessor = TextPreprocessor()

    @staticmethod
    def _tfidf_vectors(docs):
        tokenized = [doc.split() for doc in docs]
        df = Counter()
        for tokens in tokenized:
            df.update(set(tokens))
        n_docs = len(docs)
        vectors = []
        for tokens in tokenized:
            tf = Counter(tokens)
            total = len(tokens) or 1
            vec = {}
            for term, count in tf.items():
                idf = math.log((1 + n_docs) / (1 + df[term])) + 1.0
                vec[term] = (count / total) * idf
            vectors.append(vec)
        return vectors

    @staticmethod
    def _cosine(a, b):
        keys = set(a) | set(b)
        if not keys:
            return 0.0
        dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
        na = math.sqrt(sum(v * v for v in a.values())) or 1.0
        nb = math.sqrt(sum(v * v for v in b.values())) or 1.0
        return float(dot / (na * nb))

    def calculate_similarity(self, resume_text, job_text):
        resume_clean = self.preprocessor.clean_text(resume_text)
        job_clean = self.preprocessor.clean_text(job_text)
        vectors = self._tfidf_vectors([resume_clean, job_clean])
        return self._cosine(vectors[0], vectors[1])


class AnalysisEngine:
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.similarity_calculator = SimilarityCalculator()

    def analyze_resume_job_match(self, resume_text, job_text, job_required_skills=None):
        resume_skills = self.skill_extractor.extract_skills(resume_text)
        job_skills = self.skill_extractor.extract_skills(job_text)
        if job_required_skills:
            job_skills = sorted(set(job_skills) | {s.lower() for s in job_required_skills})

        matched_skills = sorted(set(resume_skills) & set(job_skills))
        missing_skills = sorted(set(job_skills) - set(resume_skills))

        similarity_score = self.similarity_calculator.calculate_similarity(resume_text, job_text)
        similarity_pct = round(similarity_score * 100, 2)
        skill_score = (len(matched_skills) / len(job_skills) * 100) if job_skills else 50.0
        match_score = round((similarity_pct * 0.6) + (skill_score * 0.4), 2)

        recommendations = self.generate_recommendations(matched_skills, missing_skills, match_score)

        return {
            "match_score": match_score,
            "similarity_score": similarity_pct,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations,
            "resume_skills": resume_skills,
            "job_skills": job_skills,
        }

    def generate_recommendations(self, matched_skills, missing_skills, match_score):
        recommendations = []
        if missing_skills:
            recommendations.append(
                "Consider adding these skills if relevant: " + ", ".join(missing_skills[:8])
            )
        if match_score < 60:
            recommendations.append(
                "Rewrite your summary to mirror important keywords from the job description."
            )
        if matched_skills:
            recommendations.append(
                "Highlight impact for these matched skills: " + ", ".join(matched_skills[:6])
            )
        if not recommendations:
            recommendations.append("Strong overlap — keep quantifying outcomes for your top skills.")
        return recommendations


class ChatBot:
    def __init__(self, analysis_data=None):
        self.analysis_data = analysis_data or {}

    def process_message(self, message):
        msg = (message or "").lower()
        if any(w in msg for w in ["skill", "missing", "match"]):
            return self.handle_skills_query(msg)
        if any(w in msg for w in ["score", "similarity", "percent"]):
            return self.handle_score_query()
        if any(w in msg for w in ["improve", "recommend", "suggestion", "tip"]):
            return self.handle_improvement_query()
        return self.handle_general_query()

    def handle_skills_query(self, message):
        matched = self.analysis_data.get("matched_skills") or []
        missing = self.analysis_data.get("missing_skills") or []
        return (
            f"Matched skills: {', '.join(matched) if matched else 'none yet'}. "
            f"Missing skills: {', '.join(missing) if missing else 'none detected'}."
        )

    def handle_score_query(self):
        match_score = self.analysis_data.get("match_score", "N/A")
        similarity = self.analysis_data.get("similarity_score", "N/A")
        return f"Your match score is {match_score}% and content similarity is {similarity}%."

    def handle_improvement_query(self):
        recs = self.analysis_data.get("recommendations") or []
        if not recs:
            return "No recommendations available yet. Run an analysis first."
        return "Suggestions: " + " ".join(recs)

    def handle_general_query(self):
        return self.default_response()

    def default_response(self):
        return (
            "Ask me about your match score, missing skills, or improvement tips "
            "based on the latest resume analysis."
        )
