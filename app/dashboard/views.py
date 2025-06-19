from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import pandas as pd
import io
import csv
from datetime import datetime, timedelta
import os
from .models import DataUploadLog, EnvironmentalData, GenomicSample, BiodiversityRecord

# Get logger for this module
logger = logging.getLogger('dashboard')


def login_view(request):
    """Handle user login with secure authentication"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Input validation
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'dashboard/login.html')
        
        # Attempt authentication
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                logger.info(f'User {username} logged in successfully')
                
                # Redirect to next page if specified, otherwise dashboard
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                logger.warning(f'Inactive user {username} attempted login')
                messages.error(request, 'Your account has been disabled. Please contact support.')
        else:
            logger.warning(f'Failed login attempt for username: {username}')
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'dashboard/login.html')


def signup_view(request):
    """Handle user registration with comprehensive validation"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Comprehensive validation
        errors = []
        
        # Required fields validation
        if not all([username, email, password, confirm_password]):
            errors.append('All fields are required.')
        
        # Username validation
        if username:
            if len(username) < 3:
                errors.append('Username must be at least 3 characters long.')
            elif len(username) > 150:
                errors.append('Username must be less than 150 characters.')
            elif not username.replace('_', '').replace('-', '').replace('.', '').isalnum():
                errors.append('Username can only contain letters, numbers, and .-_ characters.')
            elif User.objects.filter(username=username).exists():
                errors.append('Username already exists. Please choose a different one.')
        
        # Email validation
        if email:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors.append('Email already registered. Please use a different email.')
            except ValidationError:
                errors.append('Please enter a valid email address.')
        
        # Password validation
        if password:
            if len(password) < 8:
                errors.append('Password must be at least 8 characters long.')
            elif password.isdigit():
                errors.append('Password cannot be entirely numeric.')
            elif password.lower() in ['password', '12345678', 'qwerty', 'abc123']:
                errors.append('Password is too common. Please choose a stronger password.')
            elif username and password.lower() == username.lower():
                errors.append('Password cannot be the same as your username.')
        
        # Password confirmation validation
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Display errors if any
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'dashboard/signup.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            logger.info(f'New user account created: {username}')
            
            # Automatically log in the user
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                logger.info(f'New user {username} automatically logged in')
                messages.success(request, f'Account created successfully! Welcome to EcoGenomics Suite, {user.username}!')
                return redirect('dashboard')
            else:
                logger.error(f'Account created for {username} but automatic login failed')
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('login')
                
        except IntegrityError as e:
            logger.error(f'Database integrity error during user creation: {str(e)}')
            messages.error(request, 'An error occurred while creating your account. Please try again.')
        except Exception as e:
            logger.error(f'Unexpected error during user creation: {str(e)}')
            messages.error(request, 'An unexpected error occurred. Please try again.')
    
    return render(request, 'dashboard/signup.html')


@login_required
def dashboard_view(request):
    """Display the main dashboard with environmental and genomic data"""
    logger.info(f'User {request.user.username} accessed dashboard')
    
    context = {
        'user': request.user,
        'environmental_data': get_environmental_data(),
        'genomic_data': get_genomic_data(),
        'heatmap_data': json.dumps(get_heatmap_data()),
        'chart_data': json.dumps(get_chart_data()),
    }
    return render(request, 'dashboard/dashboard.html', context)


def logout_view(request):
    """Handle user logout"""
    username = request.user.username if request.user.is_authenticated else "User"
    logout(request)
    logger.info(f'User {username} logged out')
    messages.success(request, f'You have been successfully logged out. Goodbye, {username}!')
    return redirect('login')


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_data(request):
    """Handle file upload and processing"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        file_type = request.POST.get('file_type', 'environmental')
        
        # Validate file type
        if not uploaded_file.name.endswith(('.csv', '.xlsx', '.xls')):
            return JsonResponse({'error': 'Invalid file type. Please upload CSV or Excel files.'}, status=400)
        
        # Create upload log
        upload_log = DataUploadLog.objects.create(
            user=request.user,
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,
            processing_status='processing'
        )
        
        # Process the file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Process based on file type
            records_processed = process_uploaded_data(df, file_type, request.user)
            
            # Update upload log
            upload_log.processing_status = 'completed'
            upload_log.records_processed = records_processed
            upload_log.processing_completed = datetime.now()
            upload_log.save()
            
            return JsonResponse({
                'success': True,
                'message': f'File processed successfully. {records_processed} records imported.',
                'records_processed': records_processed
            })
            
        except Exception as e:
            upload_log.processing_status = 'failed'
            upload_log.error_message = str(e)
            upload_log.save()
            
            return JsonResponse({'error': f'Error processing file: {str(e)}'}, status=500)
            
    except Exception as e:
        logger.error(f'Upload error: {str(e)}')
        return JsonResponse({'error': 'Upload failed'}, status=500)


def process_uploaded_data(df, file_type, user):
    """Process uploaded data based on file type"""
    records_processed = 0
    
    if file_type == 'environmental':
        for _, row in df.iterrows():
            try:
                EnvironmentalData.objects.create(
                    temperature=row.get('temperature', 0),
                    humidity=row.get('humidity', 0),
                    ph_level=row.get('ph_level', 7),
                    oxygen_level=row.get('oxygen_level', 0),
                    turbidity=row.get('turbidity', 0),
                    conductivity=row.get('conductivity', 0),
                    location=row.get('location', ''),
                    notes=row.get('notes', '')
                )
                records_processed += 1
            except Exception as e:
                logger.warning(f'Error processing environmental record: {e}')
                
    elif file_type == 'genomic':
        for _, row in df.iterrows():
            try:
                GenomicSample.objects.create(
                    sample_id=row.get('sample_id', ''),
                    sample_type=row.get('sample_type', 'other'),
                    location=row.get('location', ''),
                    species_identified=row.get('species_identified', 0),
                    genetic_variants=row.get('genetic_variants', 0),
                    notes=row.get('notes', '')
                )
                records_processed += 1
            except Exception as e:
                logger.warning(f'Error processing genomic record: {e}')
                
    elif file_type == 'biodiversity':
        for _, row in df.iterrows():
            try:
                BiodiversityRecord.objects.create(
                    species_name=row.get('species_name', ''),
                    common_name=row.get('common_name', ''),
                    location=row.get('location', ''),
                    population_count=row.get('population_count', None),
                    conservation_status=row.get('conservation_status', 'NE'),
                    habitat_description=row.get('habitat_description', ''),
                    threat_assessment=row.get('threat_assessment', ''),
                    observer=user
                )
                records_processed += 1
            except Exception as e:
                logger.warning(f'Error processing biodiversity record: {e}')
    
    return records_processed


@login_required
def download_template(request, template_type):
    """Download CSV template for data upload"""
    templates = {
        'environmental': {
            'filename': 'environmental_template.csv',
            'headers': ['timestamp', 'temperature', 'humidity', 'ph_level', 'oxygen_level', 'turbidity', 'conductivity', 'location', 'notes'],
            'sample_data': [
                ['2024-01-01 10:00:00', '23.5', '65', '7.2', '8.5', '2.1', '450', 'Lake Station A', 'Morning sample'],
                ['2024-01-01 14:00:00', '25.1', '62', '7.1', '8.3', '2.3', '465', 'Lake Station A', 'Afternoon sample']
            ]
        },
        'genomic': {
            'filename': 'genomic_template.csv',
            'headers': ['sample_id', 'sample_type', 'collection_date', 'location', 'species_identified', 'genetic_variants', 'notes'],
            'sample_data': [
                ['GS001', 'water', '2024-01-01', 'Lake Station A', '15', '234', 'High diversity sample'],
                ['GS002', 'soil', '2024-01-01', 'Forest Plot B', '23', '456', 'Rich soil microbiome']
            ]
        },
        'biodiversity': {
            'filename': 'biodiversity_template.csv',
            'headers': ['species_name', 'common_name', 'location', 'observation_date', 'population_count', 'conservation_status', 'habitat_description', 'threat_assessment'],
            'sample_data': [
                ['Quercus alba', 'White Oak', 'Forest Plot A', '2024-01-01', '45', 'LC', 'Mature forest canopy', 'Low threat level'],
                ['Rana pipiens', 'Northern Leopard Frog', 'Wetland Area C', '2024-01-01', '12', 'NT', 'Shallow pond edge', 'Habitat degradation concern']
            ]
        }
    }
    
    if template_type not in templates:
        return JsonResponse({'error': 'Invalid template type'}, status=400)
    
    template = templates[template_type]
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{template["filename"]}"'
    
    writer = csv.writer(response)
    writer.writerow(template['headers'])
    for row in template['sample_data']:
        writer.writerow(row)
    
    return response


@login_required
@csrf_exempt
def run_analysis(request):
    """Run statistical analysis on data"""
    try:
        data = json.loads(request.body)
        dataset = data.get('dataset', 'environmental')
        analysis_type = data.get('analysis_type', 'descriptive')
        
        # Mock analysis results (replace with actual analysis)
        results = perform_statistical_analysis(dataset, analysis_type)
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def generate_visualization(request):
    """Generate data visualization"""
    try:
        data = json.loads(request.body)
        chart_type = data.get('chart_type', 'scatter')
        variables = data.get('variables', [])
        
        # Mock visualization data (replace with actual chart generation)
        chart_data = create_visualization_data(chart_type, variables)
        
        return JsonResponse({
            'success': True,
            'chart_data': chart_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def generate_report(request):
    """Generate and download report"""
    try:
        data = json.loads(request.body)
        report_type = data.get('report_type', 'comprehensive')
        output_format = data.get('output_format', 'pdf')
        
        # Mock report generation (replace with actual report creation)
        report_data = create_report(report_type, output_format)
        
        return JsonResponse({
            'success': True,
            'download_url': f'/reports/{report_data["filename"]}',
            'message': 'Report generated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Helper functions for mock data and analysis
def perform_statistical_analysis(dataset, analysis_type):
    """Perform statistical analysis (mock implementation)"""
    results = {
        'descriptive': {
            'mean': 23.45,
            'median': 22.80,
            'std': 4.12,
            'min': 18.20,
            'max': 31.70,
            'count': 1234
        },
        'correlation': {
            'correlations': [
                {'variables': 'Temperature vs Humidity', 'r': -0.65, 'p_value': 0.001},
                {'variables': 'pH vs Oxygen', 'r': 0.42, 'p_value': 0.01}
            ]
        },
        'ttest': {
            'statistic': 3.45,
            'p_value': 0.0012,
            'effect_size': 0.82
        }
    }
    
    return results.get(analysis_type, {'message': 'Analysis completed'})


def create_visualization_data(chart_type, variables):
    """Create visualization data (mock implementation)"""
    return {
        'type': chart_type,
        'data': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [{
                'label': 'Sample Data',
                'data': [12, 19, 3, 5, 2]
            }]
        }
    }


def create_report(report_type, output_format):
    """Create report (mock implementation)"""
    filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
    
    return {
        'filename': filename,
        'size': '2.3 MB',
        'pages': 15
    }


# Data functions (hardcoded for demo purposes)
def get_environmental_data():
    """Return hardcoded environmental monitoring data"""
    return {
        'temperature': {
            'value': 23.5, 
            'unit': '°C', 
            'status': 'normal',
            'description': 'Water temperature within optimal range'
        },
        'humidity': {
            'value': 65, 
            'unit': '%', 
            'status': 'normal',
            'description': 'Atmospheric humidity levels stable'
        },
        'ph_level': {
            'value': 7.2, 
            'unit': 'pH', 
            'status': 'optimal',
            'description': 'pH levels ideal for aquatic life'
        },
        'oxygen': {
            'value': 8.5, 
            'unit': 'mg/L', 
            'status': 'good',
            'description': 'Dissolved oxygen levels healthy'
        },
        'turbidity': {
            'value': 2.1, 
            'unit': 'NTU', 
            'status': 'clear',
            'description': 'Water clarity excellent'
        },
        'conductivity': {
            'value': 450, 
            'unit': 'μS/cm', 
            'status': 'normal',
            'description': 'Electrical conductivity within range'
        },
    }


def get_genomic_data():
    """Return hardcoded genomic analysis data"""
    return {
        'species_diversity': 127,
        'genetic_variants': 1543,
        'conservation_status': 'Stable',
        'population_trend': 'Increasing',
        'threat_level': 'Low',
        'last_updated': '2024-01-15',
        'total_samples': 2847,
        'analysis_completion': 94.2,
        'rare_species_count': 23,
        'endemic_species': 45,
    }


def get_heatmap_data():
    """Return hardcoded heatmap data for biodiversity visualization"""
    return [
        [0.2, 0.4, 0.6, 0.8, 0.5, 0.3, 0.7],
        [0.3, 0.6, 0.8, 0.4, 0.7, 0.5, 0.2],
        [0.5, 0.3, 0.7, 0.9, 0.2, 0.6, 0.4],
        [0.7, 0.5, 0.3, 0.6, 0.8, 0.4, 0.9],
        [0.4, 0.8, 0.5, 0.2, 0.6, 0.7, 0.3],
        [0.6, 0.2, 0.9, 0.5, 0.3, 0.8, 0.6],
        [0.8, 0.7, 0.4, 0.3, 0.9, 0.2, 0.5],
    ]


def get_chart_data():
    """Return hardcoded chart data for visualizations"""
    return {
        'temperature_trend': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'data': [22.1, 23.5, 24.2, 23.8, 22.9, 23.5]
        },
        'species_count': {
            'labels': ['Mammals', 'Birds', 'Fish', 'Reptiles', 'Amphibians'],
            'data': [45, 78, 123, 34, 56]
        },
        'genetic_diversity': {
            'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
            'data': [0.75, 0.82, 0.78, 0.85]
        },
        'monthly_samples': {
            'labels': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'data': [234, 267, 298, 312, 289, 345]
        }
    }


# API endpoints for AJAX requests
@login_required
def api_environmental_data(request):
    """API endpoint for environmental data"""
    return JsonResponse(get_environmental_data())


@login_required
def api_genomic_data(request):
    """API endpoint for genomic data"""
    return JsonResponse(get_genomic_data())


@login_required
def api_chart_data(request):
    """API endpoint for chart data"""
    return JsonResponse(get_chart_data())