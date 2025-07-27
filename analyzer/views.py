# analyzer/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth.models import User
from .models import Resume, JobDescription, Analysis, ChatSession, ChatMessage
from .forms import ResumeUploadForm, JobDescriptionForm, ChatForm
from .utils import TextExtractor, AnalysisEngine, ChatBot
import json
import uuid
import os

def home(request):
    """Home page view"""
    recent_analyses = []
    if request.user.is_authenticated:
        # Get recent analyses for authenticated users
        recent_analyses = Analysis.objects.filter(
            resume__user=request.user
        ).order_by('-created_at')[:5]
    
    context = {
        'recent_analyses': recent_analyses,
    }
    return render(request, 'home.html', context)

def upload_files(request):
    """Upload resume and job description"""
    if request.method == 'POST':
        resume_form = ResumeUploadForm(request.POST, request.FILES)
        job_form = JobDescriptionForm(request.POST)
        
        if resume_form.is_valid() and job_form.is_valid():
            try:
                # Save resume (commit=False to set user and filename)
                resume = resume_form.save(commit=False)
                if request.user.is_authenticated:
                    resume.user = request.user
                resume.original_filename = resume.file.name
                resume.save()  # <-- Save to ensure file is written and path is available

                # Extract text from resume
                if hasattr(resume.file, 'path'):
                    file_path = resume.file.path
                elif hasattr(resume.file, 'temporary_file_path'):
                    file_path = resume.file.temporary_file_path()
                else:
                    # For in-memory files, save to a temp location
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        tmp.write(resume.file.read())
                        file_path = tmp.name

                if resume.file.name.lower().endswith('.pdf'):
                    extracted_text = TextExtractor.extract_from_pdf(file_path)
                elif resume.file.name.lower().endswith(('.docx', '.doc')):
                    extracted_text = TextExtractor.extract_from_docx(file_path)
                else:
                    messages.error(request, 'Unsupported file format.')
                    return render(request, 'upload.html', {
                        'resume_form': resume_form,
                        'job_form': job_form
                    })
                
                if extracted_text.startswith('Error'):
                    messages.error(request, f'File processing error: {extracted_text}')
                    return render(request, 'upload.html', {
                        'resume_form': resume_form,
                        'job_form': job_form
                    })
                
                resume.extracted_text = extracted_text
                resume.save()
                
                # Save job description
                job_desc = job_form.save()
                
                # Perform analysis
                engine = AnalysisEngine()
                analysis_result = engine.analyze_resume_job_match(
                    resume.extracted_text, 
                    job_desc.description
                )
                
                # Save analysis
                analysis = Analysis.objects.create(
                    resume=resume,
                    job_description=job_desc,
                    match_score=analysis_result['match_score'],
                    similarity_score=analysis_result['similarity_score'],
                    matched_skills=analysis_result['matched_skills'],
                    missing_skills=analysis_result['missing_skills'],
                    recommendations=analysis_result['recommendations']
                )
                
                # Clear any old chat sessions for this user to prevent mixing
                if request.user.is_authenticated:
                    # Clear old sessions for authenticated users
                    old_sessions = ChatSession.objects.filter(user=request.user)
                    for session in old_sessions:
                        if session.analysis:
                            request.session.pop(f"chat_session_{session.analysis.id}", None)
                
                messages.success(request, 'Resume analyzed successfully!')
                return redirect('results', analysis_id=analysis.id)
                
            except Exception as e:
                messages.error(request, f'An error occurred during analysis: {str(e)}')
                return render(request, 'upload.html', {
                    'resume_form': resume_form,
                    'job_form': job_form
                })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        resume_form = ResumeUploadForm()
        job_form = JobDescriptionForm()
    
    return render(request, 'upload.html', {
        'resume_form': resume_form,
        'job_form': job_form
    })

def results(request, analysis_id):
    """Display analysis results"""
    analysis = get_object_or_404(Analysis, id=analysis_id)
    
    # Create unique chat session for each analysis
    session_key = f"chat_session_{analysis_id}"
    session_id = request.session.get(session_key)
    
    if not session_id:
        # Create unique session ID for this specific analysis
        session_id = f"{analysis_id}_{str(uuid.uuid4())}"
        request.session[session_key] = session_id
    
    # Create or get chat session
    chat_session, created = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            'analysis': analysis,
            'user': request.user if request.user.is_authenticated else None
        }
    )
    
    # Update analysis if session already exists but analysis is different
    if not created and chat_session.analysis != analysis:
        chat_session.analysis = analysis
        if request.user.is_authenticated:
            chat_session.user = request.user
        chat_session.save()
    
    # Calculate additional metrics
    total_resume_skills = len(analysis.matched_skills) + len([
        skill for skill in analysis.resume.skills_extracted 
        if skill not in analysis.matched_skills
    ]) if hasattr(analysis.resume, 'skills_extracted') and analysis.resume.skills_extracted else len(analysis.matched_skills)
    
    context = {
        'analysis': analysis,
        'match_score': analysis.match_score,
        'similarity_score': analysis.similarity_score,
        'matched_skills': analysis.matched_skills,
        'missing_skills': analysis.missing_skills,
        'recommendations': analysis.recommendations,
        'chat_session_id': session_id,
        'total_matched_skills': len(analysis.matched_skills),
        'total_missing_skills': len(analysis.missing_skills),
        'total_resume_skills': total_resume_skills,
        'resume_filename': analysis.resume.original_filename,
        'job_title': analysis.job_description.title,
        'company_name': analysis.job_description.company,
    }
    
    return render(request, 'results.html', context)

@csrf_exempt
def chat_api(request):
    """Chat API endpoint with session security"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
            
            if not message or not session_id:
                return JsonResponse({
                    'error': 'Message and session_id are required'
                }, status=400)
            
            # Get chat session and verify ownership
            try:
                chat_session = get_object_or_404(ChatSession, session_id=session_id)
            except:
                return JsonResponse({
                    'error': 'Invalid session ID'
                }, status=404)
            
            # Security check: verify session belongs to current user/analysis
            if chat_session.analysis:
                session_key = f"chat_session_{chat_session.analysis.id}"
                stored_session_id = request.session.get(session_key)
                
                if stored_session_id != session_id:
                    return JsonResponse({
                        'error': 'Unauthorized access to this chat session'
                    }, status=403)
            
            analysis = chat_session.analysis
            
            # Prepare analysis data for chatbot
            analysis_data = {}
            if analysis:
                analysis_data = {
                    'match_score': analysis.match_score,
                    'similarity_score': analysis.similarity_score,
                    'matched_skills': analysis.matched_skills,
                    'missing_skills': analysis.missing_skills,
                    'recommendations': analysis.recommendations,
                    'resume_filename': analysis.resume.original_filename,
                    'job_title': analysis.job_description.title,
                    'company_name': analysis.job_description.company,
                }
            
            # Process message with chatbot
            chatbot = ChatBot(analysis_data)
            response = chatbot.process_message(message)
            
            # Save chat message
            ChatMessage.objects.create(
                session=chat_session,
                message=message,
                response=response
            )
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'error': 'Method not allowed. Use POST.'
    }, status=405)

def chat_history(request, session_id):
    """Get chat history for a session with security check"""
    try:
        chat_session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Security check: verify session belongs to current user/analysis
        if chat_session.analysis:
            session_key = f"chat_session_{chat_session.analysis.id}"
            stored_session_id = request.session.get(session_key)
            
            if stored_session_id != session_id:
                return JsonResponse({
                    'error': 'Unauthorized access to chat history'
                }, status=403)
        
        messages = ChatMessage.objects.filter(
            session=chat_session
        ).order_by('timestamp')
        
        history = []
        for msg in messages:
            history.append({
                'message': msg.message,
                'response': msg.response,
                'timestamp': msg.timestamp.strftime('%H:%M')
            })
        
        return JsonResponse({
            'history': history,
            'total_messages': len(history)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error retrieving chat history: {str(e)}'
        }, status=500)

def analysis_list(request):
    """List all analyses for authenticated users"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to view your analysis history.')
        return redirect('home')
    
    analyses = Analysis.objects.filter(
        resume__user=request.user
    ).order_by('-created_at')
    
    context = {
        'analyses': analyses,
        'total_analyses': analyses.count(),
    }
    
    return render(request, 'analysis_list.html', context)

def delete_analysis(request, analysis_id):
    """Delete an analysis (only owner can delete)"""
    analysis = get_object_or_404(Analysis, id=analysis_id)
    
    # Check if user is the owner
    if request.user.is_authenticated and analysis.resume.user == request.user:
        # Delete associated chat sessions and messages
        chat_sessions = ChatSession.objects.filter(analysis=analysis)
        for session in chat_sessions:
            ChatMessage.objects.filter(session=session).delete()
            # Clear from session
            session_key = f"chat_session_{analysis.id}"
            request.session.pop(session_key, None)
        chat_sessions.delete()
        
        # Delete analysis (cascade will delete resume and job description)
        analysis.delete()
        messages.success(request, 'Analysis deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this analysis.')
    
    return redirect('analysis_list')

def quick_analysis(request):
    """Quick text-based analysis without file upload"""
    if request.method == 'POST':
        resume_text = request.POST.get('resume_text', '').strip()
        job_text = request.POST.get('job_text', '').strip()
        
        if not resume_text or not job_text:
            messages.error(request, 'Both resume text and job description are required.')
            return render(request, 'quick_analysis.html')
        
        if len(resume_text) < 100:
            messages.error(request, 'Resume text is too short. Please provide more details.')
            return render(request, 'quick_analysis.html')
        
        if len(job_text) < 50:
            messages.error(request, 'Job description is too short. Please provide more details.')
            return render(request, 'quick_analysis.html')
        
        try:
            # Create temporary objects (not saved to database)
            engine = AnalysisEngine()
            analysis_result = engine.analyze_resume_job_match(resume_text, job_text)
            
            context = {
                'analysis_result': analysis_result,
                'resume_text': resume_text[:200] + '...',  # Show truncated text
                'job_text': job_text[:200] + '...',
            }
            
            return render(request, 'quick_results.html', context)
            
        except Exception as e:
            messages.error(request, f'Analysis failed: {str(e)}')
            return render(request, 'quick_analysis.html')
    
    return render(request, 'quick_analysis.html')

# Error handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'errors/500.html', status=500)