"""Vercel entrypoint for Django WSGI."""
from resume_analyzer.wsgi import application

app = application
