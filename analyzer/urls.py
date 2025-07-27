from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_files, name='upload'),
    path('results/<int:analysis_id>/', views.results, name='results'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/chat-history/<str:session_id>/', views.chat_history, name='chat_history'),
]