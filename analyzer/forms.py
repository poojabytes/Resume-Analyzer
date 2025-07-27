# analyzer/forms.py

from django import forms
from .models import Resume, JobDescription

class ResumeUploadForm(forms.ModelForm):
    """Form for uploading resume files"""
    
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.doc',
                'id': 'resume-file'
            })
        }
        labels = {
            'file': 'Upload Resume'
        }
        help_texts = {
            'file': 'Supported formats: PDF, DOCX, DOC (Max size: 5MB)'
        }
    
    def clean_file(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file')
        
        if file:
            # Check file extension
            allowed_extensions = ['.pdf', '.docx', '.doc']
            file_extension = file.name.lower()[-5:]  # Get last 5 characters
            
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    'Invalid file format. Only PDF, DOCX, and DOC files are allowed.'
                )
            
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    'File size too large. Please upload a file smaller than 5MB.'
                )
            
            # Check if file is empty
            if file.size == 0:
                raise forms.ValidationError('The uploaded file is empty.')
        
        return file


class JobDescriptionForm(forms.ModelForm):
    """Form for job description input"""
    
    class Meta:
        model = JobDescription
        fields = ['title', 'company', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Developer',
                'maxlength': 200
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Google Inc. (Optional)',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Paste the complete job description here...\n\nInclude:\n- Job responsibilities\n- Required skills\n- Qualifications\n- Experience requirements',
                'style': 'min-height: 300px;'
            })
        }
        labels = {
            'title': 'Job Title',
            'company': 'Company Name',
            'description': 'Job Description'
        }
        help_texts = {
            'title': 'Enter the position title you\'re applying for',
            'company': 'Company name (optional)',
            'description': 'Paste the full job posting or description'
        }
    
    def clean_title(self):
        """Validate job title"""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise forms.ValidationError('Job title must be at least 3 characters long.')
        return title.strip() if title else title
    
    def clean_description(self):
        """Validate job description"""
        description = self.cleaned_data.get('description')
        
        if description:
            description = description.strip()
            
            if len(description) < 50:
                raise forms.ValidationError(
                    'Job description is too short. Please provide a more detailed description (at least 50 characters).'
                )
            
            if len(description) > 10000:
                raise forms.ValidationError(
                    'Job description is too long. Please limit to 10,000 characters.'
                )
        
        return description


class ChatForm(forms.Form):
    """Form for chat messages"""
    
    message = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ask me about your resume analysis...',
            'autocomplete': 'off',
            'maxlength': 500
        }),
        label='',
        help_text='Ask questions about your analysis, skills, or get recommendations'
    )
    
    def clean_message(self):
        """Validate chat message"""
        message = self.cleaned_data.get('message')
        
        if message:
            message = message.strip()
            
            if len(message) < 3:
                raise forms.ValidationError('Message is too short.')
            
            if not message.replace(' ', '').replace('?', '').replace('!', '').replace('.', ''):
                raise forms.ValidationError('Please enter a valid message.')
        
        return message


class QuickAnalysisForm(forms.Form):
    """Form for quick text-based analysis"""
    
    resume_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Paste your resume content here...',
            'maxlength': 5000
        }),
        label='Resume Text',
        max_length=5000,
        help_text='Copy and paste your resume content (up to 5000 characters)'
    )
    
    job_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Paste the job description here...',
            'maxlength': 5000
        }),
        label='Job Description',
        max_length=5000,
        help_text='Copy and paste the job description (up to 5000 characters)'
    )
    
    def clean_resume_text(self):
        """Validate resume text"""
        text = self.cleaned_data.get('resume_text')
        if text and len(text.strip()) < 100:
            raise forms.ValidationError('Resume text is too short. Please provide more details.')
        return text.strip() if text else text
    
    def clean_job_text(self):
        """Validate job description text"""
        text = self.cleaned_data.get('job_text')
        if text and len(text.strip()) < 50:
            raise forms.ValidationError('Job description is too short. Please provide more details.')
        return text.strip() if text else text


# Custom validation functions
def validate_file_extension(file):
    """Custom validator for file extensions"""
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_extension = file.name.lower()
    
    if not any(file_extension.endswith(ext) for ext in allowed_extensions):
        raise forms.ValidationError(
            f'File extension "{file_extension.split(".")[-1]}" is not allowed. '
            f'Allowed extensions are: {", ".join(allowed_extensions)}'
        )


def validate_file_size(file):
    """Custom validator for file size"""
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise forms.ValidationError(
            f'File size ({file.size} bytes) exceeds maximum allowed size ({max_size} bytes).'
        )