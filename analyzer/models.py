from django.db import models
from django.contrib.auth.models import User
import json

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255)
    extracted_text = models.TextField()
    skills_extracted = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resume - {self.original_filename}"

class JobDescription(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    required_skills = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.company}"

class Analysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE)
    match_score = models.FloatField()
    similarity_score = models.FloatField()
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis - {self.match_score}% match"

# ChatSession model में changes करें:
class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # यह line add करें
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session_id', 'analysis']  # यह भी add करें
    
    def __str__(self):
        return f"Chat Session - {self.session_id} - Analysis {self.analysis.id if self.analysis else 'None'}"
    
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True) 