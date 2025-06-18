# EcoGenomics Suite - Django Application

A comprehensive environmental monitoring and genomic analytics platform built with Django.

## Features

- **Environmental Monitoring Dashboard**: Real-time environmental data visualization
- **Genomic Analytics**: Species diversity and genetic analysis tools
- **Interactive Visualizations**: Charts, heatmaps, and data representations
- **User Authentication**: Login and signup functionality
- **Responsive Design**: Mobile-friendly interface

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- **Windows Users**: Microsoft Visual C++ 14.0 or greater (for Pillow compilation)

## Installation & Setup

### 1. Create Virtual Environment

```bash
# Navigate to the app directory
cd app

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (Command Prompt):
.venv\Scripts\activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Git Bash):
source .venv/Scripts/activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip first (recommended)
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Windows Troubleshooting:**
If you encounter issues with Pillow installation on Windows:

```bash
# Option 1: Install pre-compiled wheel
pip install --upgrade pip setuptools wheel
pip install Pillow

# Option 2: Install without Pillow first, then add it
pip install Django==4.2.7
pip install Pillow

# Option 3: Use conda instead of pip (if you have Anaconda/Miniconda)
conda install pillow
pip install Django==4.2.7
```

### 3. Database Setup

```bash
# Run migrations to set up the database
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Quick Start (Windows)

If you're having dependency issues, here's a simplified approach:

```bash
# 1. Navigate to app directory
cd app

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install Django first
pip install Django==4.2.7

# 4. Try to install Pillow (optional for this demo)
pip install Pillow

# 5. Run migrations
python manage.py migrate

# 6. Start server
python manage.py runserver
```

**Note:** Pillow is only needed for image handling. The current demo doesn't require it, so you can skip it if installation fails.

## Usage

### Demo Mode
The application runs in demo mode where any username and password combination will allow login access. This is perfect for demonstration purposes.

### Navigation
- **Login Page**: Enter any username/password to access the dashboard
- **Dashboard**: Navigate through different tabs:
  - Overview: Key metrics and summary charts
  - Environmental Data: Real-time environmental monitoring
  - Genomic Analysis: Species and genetic diversity data
  - Biodiversity Map: Interactive heatmap visualization

## Project Structure

```
app/
├── ecogenomics/          # Main Django project
│   ├── settings.py       # Django settings
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI configuration
├── dashboard/           # Main application
│   ├── views.py         # View functions
│   ├── urls.py          # App URL patterns
│   └── models.py        # Data models
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   └── dashboard/       # Dashboard templates
├── static/             # Static files
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Images and icons
├── requirements.txt    # Python dependencies
└── manage.py          # Django management script
```

## Common Windows Issues & Solutions

### Issue 1: ModuleNotFoundError: No module named 'django'
**Solution:** Make sure your virtual environment is activated:
```bash
.venv\Scripts\activate
pip install Django==4.2.7
```

### Issue 2: Pillow installation fails
**Solution:** Skip Pillow for now (not required for demo):
```bash
pip install Django==4.2.7
# Skip Pillow installation
```

### Issue 3: Virtual environment activation issues
**Solution:** Try different activation methods:
```bash
# Method 1 (Command Prompt)
.venv\Scripts\activate.bat

# Method 2 (PowerShell)
.venv\Scripts\Activate.ps1

# Method 3 (Git Bash)
source .venv/Scripts/activate
```

## Development

### Adding New Features
1. Create new views in `dashboard/views.py`
2. Add URL patterns in `dashboard/urls.py`
3. Create templates in `templates/dashboard/`
4. Add static files in `static/`

### Customizing Data
All data is currently hardcoded in the view functions for demo purposes. To modify:
- Edit the data functions in `dashboard/views.py`
- Update chart data in the template context

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure proper database settings
3. Set up static file serving
4. Configure allowed hosts
5. Use a production WSGI server like Gunicorn

## Support

For issues or questions, please refer to the Django documentation or contact the development team.