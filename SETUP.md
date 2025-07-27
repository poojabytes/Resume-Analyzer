# Resume Analyzer - Setup Guide

## Quick Start

### Prerequisites
- Python 3.11+ installed
- Git installed
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Pooja021011/Resume-Analyzer.git
   cd Resume-Analyzer
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## Features

- ✅ Resume upload and analysis
- ✅ Job description matching
- ✅ AI-powered skill extraction
- ✅ Interactive chat system
- ✅ Quick text-based analysis
- ✅ User authentication
- ✅ Analysis history

## Technology Stack

- **Backend:** Django 5.2.4
- **Database:** SQLite (development)
- **ML Libraries:** scikit-learn, NLTK
- **Document Processing:** PyMuPDF, python-docx
- **Frontend:** Bootstrap 5, JavaScript
- **Forms:** Django Crispy Forms

## Project Structure

```
resume_analyzer/
├── analyzer/                 # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Form classes
│   ├── utils.py             # Analysis engine
│   ├── admin.py             # Admin configuration
│   ├── urls.py              # URL patterns
│   └── templates/           # HTML templates
├── media/                   # Uploaded files
├── static/                  # Static files (CSS, JS)
├── templates/               # Global templates
├── resume_analyzer/         # Project settings
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
└── README.md               # Project documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.