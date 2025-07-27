import fitz  # PyMuPDF
from docx import Document
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextExtractor:
    @staticmethod
    def extract_from_pdf(file_path):
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    @staticmethod
    def extract_from_docx(file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}"

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)

class SkillExtractor:
    def __init__(self):
        # Common technical skills - you can expand this list
        self.skills_database = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'swift',
            'kotlin', 'scala', 'r programming', 'r language', 'matlab', 'perl', 'shell', 'bash',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask',
            'spring', 'laravel', 'bootstrap', 'jquery', 'ajax',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra',
            'elasticsearch', 'firebase',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'gitlab', 'github',
            'terraform', 'ansible', 'chef', 'puppet',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'artificial intelligence', 'data science',
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
            'tableau', 'power bi', 'excel',
            
            # Other Technologies
            'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'jira', 'confluence',
            'linux', 'unix', 'windows server', 'networking', 'cybersecurity'
        ]
    
    def extract_skills(self, text):
        """Extract skills from text with improved context-aware matching"""
        text_lower = text.lower()
        found_skills = []
        
        import re
        
        # Special handling for programming languages that are single letters
        special_patterns = {
            'r programming': r'\br\s*(programming|language|lang)\b',
            'r language': r'\br\s*(programming|language|lang)\b',
            'c programming': r'\bc\s*(programming|language|lang)\b',
            'c language': r'\bc\s*(programming|language|lang)\b'
        }
        
        for skill in self.skills_database:
            # Check special patterns first
            if skill in special_patterns:
                if re.search(special_patterns[skill], text_lower):
                    found_skills.append(skill.split()[0])  # Add just 'r' or 'c'
                continue
            
            # For very short skills (1-2 characters), use word boundary
            if len(skill) <= 2:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            else:
                # For longer skills, use simple substring match
                if skill in text_lower:
                    found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates

class SimilarityCalculator:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def calculate_similarity(self, resume_text, job_text):
        """Calculate similarity between resume and job description"""
        try:
            documents = [resume_text, job_text]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0]) * 100  # Convert to percentage
        except:
            return 0.0

class AnalysisEngine:
    def __init__(self):
        self.text_processor = TextPreprocessor()
        self.skill_extractor = SkillExtractor()
        self.similarity_calculator = SimilarityCalculator()
    
    def analyze_resume_job_match(self, resume_text, job_text, job_required_skills=None):
        """Complete analysis of resume vs job description"""
        
        # Extract skills
        resume_skills = self.skill_extractor.extract_skills(resume_text)
        job_skills = self.skill_extractor.extract_skills(job_text)
        
        if job_required_skills:
            job_skills.extend(job_required_skills)
            job_skills = list(set(job_skills))  # Remove duplicates
        
        # Calculate matches
        matched_skills = list(set(resume_skills) & set(job_skills))
        missing_skills = list(set(job_skills) - set(resume_skills))
        
        # Calculate match score
        if job_skills:
            match_score = (len(matched_skills) / len(job_skills)) * 100
        else:
            match_score = 0
        
        # Calculate text similarity
        similarity_score = self.similarity_calculator.calculate_similarity(resume_text, job_text)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(matched_skills, missing_skills, match_score)
        
        return {
            'match_score': round(match_score, 2),
            'similarity_score': round(similarity_score, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'resume_skills': resume_skills,
            'job_skills': job_skills,
            'recommendations': recommendations
        }
    
    def generate_recommendations(self, matched_skills, missing_skills, match_score):
        """Generate improvement recommendations"""
        recommendations = []
        
        if match_score < 30:
            recommendations.append("Your resume has low compatibility with this job. Consider gaining more relevant skills.")
        elif match_score < 60:
            recommendations.append("Your resume shows moderate compatibility. Focus on highlighting relevant experience.")
        else:
            recommendations.append("Great match! Your skills align well with the job requirements.")
        
        if missing_skills:
            if len(missing_skills) <= 3:
                recommendations.append(f"Consider learning: {', '.join(missing_skills[:3])}")
            else:
                recommendations.append(f"Top missing skills to focus on: {', '.join(missing_skills[:5])}")
        
        if matched_skills:
            recommendations.append(f"Highlight these matching skills in your resume: {', '.join(matched_skills[:5])}")
        
        return '\n'.join(recommendations)

class ChatBot:
    def __init__(self, analysis_data=None):
        self.analysis_data = analysis_data or {}
    
    def process_message(self, message):
        """Process user message and return response"""
        message_lower = message.lower()
        
        # Skill-related questions
        if any(word in message_lower for word in ['skill', 'skills', 'missing', 'lack']):
            return self.handle_skills_query(message_lower)
        
        # Score-related questions
        elif any(word in message_lower for word in ['score', 'match', 'percentage', '%']):
            return self.handle_score_query()
        
        # Improvement suggestions
        elif any(word in message_lower for word in ['improve', 'recommendation', 'suggest', 'advice']):
            return self.handle_improvement_query()
        
        # General questions
        elif any(word in message_lower for word in ['resume', 'cv', 'job', 'position']):
            return self.handle_general_query()
        
        else:
            return self.default_response()
    
    def handle_skills_query(self, message):
        if not self.analysis_data:
            return "Please upload a resume and job description first to get skill analysis."
        
        missing_skills = self.analysis_data.get('missing_skills', [])
        matched_skills = self.analysis_data.get('matched_skills', [])
        
        if 'missing' in message or 'lack' in message:
            if missing_skills:
                return f"Missing skills from your resume: {', '.join(missing_skills[:10])}"
            else:
                return "Great! You have all the required skills for this position."
        else:
            if matched_skills:
                return f"Skills you have that match the job: {', '.join(matched_skills[:10])}"
            else:
                return "No matching skills found. Consider updating your resume with more relevant skills."
    
    def handle_score_query(self):
        if not self.analysis_data:
            return "Please upload a resume and job description first to get match scores."
        
        match_score = self.analysis_data.get('match_score', 0)
        similarity_score = self.analysis_data.get('similarity_score', 0)
        
        return f"Your resume match score is {match_score}% and similarity score is {similarity_score}%. " + \
               f"{'Excellent match!' if match_score > 70 else 'Good potential!' if match_score > 40 else 'Consider improving your resume.'}"
    
    def handle_improvement_query(self):
        if not self.analysis_data:
            return "Upload your resume and job description first, then I can provide personalized recommendations."
        
        recommendations = self.analysis_data.get('recommendations', '')
        if recommendations:
            return f"Here are my recommendations:\n\n{recommendations}"
        else:
            return "Based on your analysis, focus on highlighting your matching skills and consider learning the missing ones."
    
    def handle_general_query(self):
        return "I can help you analyze your resume against job descriptions. Upload both files and I'll provide detailed insights about skill matches, scores, and improvement suggestions."
    
    def default_response(self):
        return "I can help you with:\n• Skill analysis (matched/missing skills)\n• Match scores and similarity\n• Improvement recommendations\n• General resume advice\n\nWhat would you like to know?"