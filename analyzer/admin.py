from django.contrib import admin
from .models import Resume, JobDescription, Analysis, ChatSession, ChatMessage

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'user', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['original_filename', 'user__username']

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'created_at']
    list_filter = ['created_at', 'company']
    search_fields = ['title', 'company']

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['resume', 'job_description', 'match_score', 'similarity_score', 'created_at']
    list_filter = ['created_at', 'match_score']
    
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'analysis', 'created_at']
    list_filter = ['created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message', 'timestamp']
    list_filter = ['timestamp']