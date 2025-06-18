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

## Installation & Setup

### 1. Create Virtual Environment

```bash
# Navigate to the app directory
cd app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
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