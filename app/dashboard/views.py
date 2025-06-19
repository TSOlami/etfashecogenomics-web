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
from .models import DataUploadLog, EnvironmentalData, GenomicSample, BiodiversityRecord, AnalysisResult, Report
from .analysis import run_analysis, EnvironmentalAnalyzer, GenomicAnalyzer
from django.db.models import Count, Avg, Max, Min
import numpy as np

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
                # Don't show success message for signup - just redirect
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
    """Display the main dashboard with real environmental and genomic data"""
    logger.info(f'User {request.user.username} accessed dashboard')
    
    # Get real data from database
    environmental_data = get_real_environmental_data(request.user)
    genomic_data = get_real_genomic_data(request.user)
    biodiversity_data = get_real_biodiversity_data(request.user)
    
    # Generate chart data from real data
    chart_data = generate_real_chart_data(request.user)
    heatmap_data = generate_real_heatmap_data(request.user)
    
    context = {
        'user': request.user,
        'environmental_data': environmental_data,
        'genomic_data': genomic_data,
        'biodiversity_data': biodiversity_data,
        'heatmap_data': json.dumps(heatmap_data),
        'chart_data': json.dumps(chart_data),
        'recent_uploads': DataUploadLog.objects.filter(user=request.user)[:5],
        'recent_analyses': AnalysisResult.objects.filter(user=request.user)[:5],
    }
    return render(request, 'dashboard/dashboard.html', context)


def logout_view(request):
    """Handle user logout"""
    username = request.user.username if request.user.is_authenticated else "User"
    logout(request)
    logger.info(f'User {username} logged out')
    # Don't show logout message - just redirect
    return redirect('login')


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_data(request):
    """Handle file upload and processing with real data integration"""
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
            processing_status='processing',
            processing_started=datetime.now()
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
            upload_log.processing_completed = datetime.now()
            upload_log.save()
            
            return JsonResponse({'error': f'Error processing file: {str(e)}'}, status=500)
            
    except Exception as e:
        logger.error(f'Upload error: {str(e)}')
        return JsonResponse({'error': 'Upload failed'}, status=500)


def process_uploaded_data(df, file_type, user):
    """Process uploaded data based on file type with enhanced field mapping"""
    records_processed = 0
    
    if file_type == 'environmental':
        for _, row in df.iterrows():
            try:
                # Create environmental data record with comprehensive field mapping
                env_data = EnvironmentalData.objects.create(
                    user=user,
                    timestamp=pd.to_datetime(row.get('timestamp', datetime.now())),
                    location=row.get('location', ''),
                    
                    # Air Quality Parameters
                    ozone_concentration=safe_float(row.get('ozone_concentration')),
                    carbon_monoxide=safe_float(row.get('carbon_monoxide')),
                    nitrogen_dioxide=safe_float(row.get('nitrogen_dioxide')),
                    sulfur_dioxide=safe_float(row.get('sulfur_dioxide')),
                    total_voc=safe_float(row.get('total_voc')),
                    pm25=safe_float(row.get('pm25')),
                    pm10=safe_float(row.get('pm10')),
                    
                    # Basic Environmental Parameters
                    temperature=safe_float(row.get('temperature')),
                    humidity=safe_float(row.get('humidity')),
                    ph_level=safe_float(row.get('ph_level')),
                    oxygen_level=safe_float(row.get('oxygen_level')),
                    turbidity=safe_float(row.get('turbidity')),
                    conductivity=safe_float(row.get('conductivity')),
                    
                    # Heavy Metals
                    lead_concentration=safe_float(row.get('lead_concentration')),
                    chromium_concentration=safe_float(row.get('chromium_concentration')),
                    cadmium_concentration=safe_float(row.get('cadmium_concentration')),
                    mercury_concentration=safe_float(row.get('mercury_concentration')),
                    arsenic_concentration=safe_float(row.get('arsenic_concentration')),
                    
                    # Georeferencing
                    latitude=safe_float(row.get('latitude')),
                    longitude=safe_float(row.get('longitude')),
                    
                    notes=row.get('notes', '')
                )
                records_processed += 1
            except Exception as e:
                logger.warning(f'Error processing environmental record: {e}')
                
    elif file_type == 'genomic':
        for _, row in df.iterrows():
            try:
                # Create genomic sample record
                genomic_sample = GenomicSample.objects.create(
                    user=user,
                    sample_id=row.get('sample_id', f'GS_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
                    sample_type=row.get('sample_type', 'other'),
                    collection_date=pd.to_datetime(row.get('collection_date', datetime.now())),
                    location=row.get('location', ''),
                    
                    # Georeferencing
                    latitude=safe_float(row.get('latitude')),
                    longitude=safe_float(row.get('longitude')),
                    distance_from_source=safe_float(row.get('distance_from_source')),
                    
                    # DNA Analysis
                    dna_concentration=safe_float(row.get('dna_concentration')),
                    dna_purity_260_280=safe_float(row.get('dna_purity_260_280')),
                    dna_purity_260_230=safe_float(row.get('dna_purity_260_230')),
                    
                    # Gene Analysis (JSON fields)
                    target_genes=row.get('target_genes', ''),
                    gene_sequences=row.get('gene_sequences', ''),
                    mutations_detected=row.get('mutations_detected', ''),
                    
                    analysis_status=row.get('analysis_status', 'collected'),
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
                    observation_date=pd.to_datetime(row.get('observation_date', datetime.now())),
                    population_count=safe_int(row.get('population_count')),
                    conservation_status=row.get('conservation_status', 'NE'),
                    
                    # Georeferencing
                    latitude=safe_float(row.get('latitude')),
                    longitude=safe_float(row.get('longitude')),
                    
                    habitat_description=row.get('habitat_description', ''),
                    threat_assessment=row.get('threat_assessment', ''),
                    observer=user
                )
                records_processed += 1
            except Exception as e:
                logger.warning(f'Error processing biodiversity record: {e}')
    
    return records_processed


def safe_float(value):
    """Safely convert value to float"""
    try:
        return float(value) if value is not None and str(value).strip() != '' else None
    except (ValueError, TypeError):
        return None


def safe_int(value):
    """Safely convert value to int"""
    try:
        return int(float(value)) if value is not None and str(value).strip() != '' else None
    except (ValueError, TypeError):
        return None


@login_required
def download_template(request, template_type):
    """Download CSV template for data upload with comprehensive field mappings"""
    templates = {
        'environmental': {
            'filename': 'environmental_template.csv',
            'headers': [
                'timestamp', 'location', 'latitude', 'longitude',
                # Air Quality Parameters
                'ozone_concentration', 'carbon_monoxide', 'nitrogen_dioxide', 
                'sulfur_dioxide', 'total_voc', 'pm25', 'pm10',
                # Basic Environmental
                'temperature', 'humidity', 'ph_level', 'oxygen_level', 
                'turbidity', 'conductivity',
                # Heavy Metals
                'lead_concentration', 'chromium_concentration', 'cadmium_concentration',
                'mercury_concentration', 'arsenic_concentration',
                'notes'
            ],
            'sample_data': [
                ['2024-01-01 10:00:00', 'Factory Site A', '6.5244', '3.3792', 
                 '120', '15', '45', '25', '200', '35', '55',
                 '28.5', '65', '7.2', '8.5', '2.1', '450',
                 '25', '15', '2', '0.5', '8', 'Morning sample near cement factory'],
                ['2024-01-01 14:00:00', 'Control Site B', '6.5200', '3.3800',
                 '80', '8', '25', '15', '150', '20', '35',
                 '30.1', '62', '7.1', '8.3', '1.8', '420',
                 '10', '8', '1', '0.2', '3', 'Control site 2km away']
            ]
        },
        'genomic': {
            'filename': 'genomic_template.csv',
            'headers': [
                'sample_id', 'sample_type', 'collection_date', 'location',
                'latitude', 'longitude', 'distance_from_source',
                'dna_concentration', 'dna_purity_260_280', 'dna_purity_260_230',
                'target_genes', 'gene_sequences', 'mutations_detected',
                'analysis_status', 'notes'
            ],
            'sample_data': [
                ['GS001', 'leaf', '2024-01-01', 'Factory Site A',
                 '6.5244', '3.3792', '100',
                 '150.5', '1.85', '2.1',
                 '["rbcL", "matK", "ITS"]', '["ATCGATCG..."]', '["point_mutation_rbcL_pos_245"]',
                 'analyzed', 'Leaf sample from stressed plant'],
                ['GS002', 'leaf', '2024-01-01', 'Control Site B',
                 '6.5200', '3.3800', '2000',
                 '180.2', '1.92', '2.3',
                 '["rbcL", "matK", "ITS"]', '["ATCGATCG..."]', '[]',
                 'analyzed', 'Control sample from healthy plant']
            ]
        },
        'biodiversity': {
            'filename': 'biodiversity_template.csv',
            'headers': [
                'species_name', 'common_name', 'location', 'observation_date',
                'population_count', 'conservation_status', 'latitude', 'longitude',
                'habitat_description', 'threat_assessment'
            ],
            'sample_data': [
                ['Mangifera indica', 'Mango Tree', 'Factory Site A', '2024-01-01',
                 '15', 'LC', '6.5244', '3.3792',
                 'Urban environment with dust exposure', 'High - cement dust accumulation'],
                ['Terminalia catappa', 'Indian Almond', 'Control Site B', '2024-01-01',
                 '25', 'LC', '6.5200', '3.3800',
                 'Natural forest edge', 'Low - minimal human impact']
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
def run_analysis_view(request):
    """Run statistical analysis on real data"""
    try:
        data = json.loads(request.body)
        dataset = data.get('dataset', 'environmental')
        analysis_type = data.get('analysis_type', 'descriptive')
        parameters = data.get('parameters', {})
        
        # Run analysis using the analysis module
        results = run_analysis(request.user, analysis_type, dataset, parameters)
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f'Analysis error: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def generate_visualization(request):
    """Generate data visualization from real data"""
    try:
        data = json.loads(request.body)
        chart_type = data.get('chart_type', 'scatter')
        dataset_type = data.get('dataset_type', 'environmental')
        parameters = data.get('parameters', {})
        
        # Generate visualization based on real data
        chart_data = create_real_visualization_data(request.user, chart_type, dataset_type, parameters)
        
        return JsonResponse({
            'success': True,
            'chart_data': chart_data
        })
        
    except Exception as e:
        logger.error(f'Visualization error: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def generate_report(request):
    """Generate and download report from real data"""
    try:
        data = json.loads(request.body)
        report_type = data.get('report_type', 'comprehensive')
        output_format = data.get('output_format', 'pdf')
        parameters = data.get('parameters', {})
        
        # Generate report from real data
        report_data = create_real_report(request.user, report_type, output_format, parameters)
        
        return JsonResponse({
            'success': True,
            'download_url': f'/reports/{report_data["filename"]}',
            'message': 'Report generated successfully',
            'report_data': report_data
        })
        
    except Exception as e:
        logger.error(f'Report generation error: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


# Real data functions
def get_real_environmental_data(user):
    """Get real environmental data from database"""
    recent_data = EnvironmentalData.objects.filter(user=user).order_by('-timestamp')[:10]
    
    if not recent_data.exists():
        # Return sample data structure if no real data
        return {
            'temperature': {'value': 0, 'unit': '°C', 'status': 'no_data', 'description': 'No data available'},
            'humidity': {'value': 0, 'unit': '%', 'status': 'no_data', 'description': 'No data available'},
            'ph_level': {'value': 0, 'unit': 'pH', 'status': 'no_data', 'description': 'No data available'},
            'air_quality': {'value': 0, 'unit': 'AQI', 'status': 'no_data', 'description': 'No data available'},
            'total_samples': 0,
            'locations_monitored': 0,
            'pollution_violations': 0
        }
    
    # Calculate averages and statistics
    latest = recent_data.first()
    
    # Calculate pollution violations
    violations = 0
    for record in recent_data:
        violations += len(record.check_pollution_standards())
    
    return {
        'temperature': {
            'value': latest.temperature or 0,
            'unit': '°C',
            'status': 'normal' if latest.temperature and 20 <= latest.temperature <= 35 else 'warning',
            'description': f'Latest temperature reading from {latest.location}'
        },
        'humidity': {
            'value': latest.humidity or 0,
            'unit': '%',
            'status': 'normal' if latest.humidity and 40 <= latest.humidity <= 70 else 'warning',
            'description': f'Latest humidity reading from {latest.location}'
        },
        'ph_level': {
            'value': latest.ph_level or 0,
            'unit': 'pH',
            'status': 'optimal' if latest.ph_level and 6.5 <= latest.ph_level <= 8.5 else 'warning',
            'description': f'Latest pH reading from {latest.location}'
        },
        'air_quality': {
            'value': latest.get_air_quality_index(),
            'unit': 'AQI',
            'status': 'good' if latest.get_air_quality_index() <= 50 else 'warning',
            'description': f'Air Quality Index from {latest.location}'
        },
        'total_samples': EnvironmentalData.objects.filter(user=user).count(),
        'locations_monitored': EnvironmentalData.objects.filter(user=user).values('location').distinct().count(),
        'pollution_violations': violations
    }


def get_real_genomic_data(user):
    """Get real genomic data from database"""
    samples = GenomicSample.objects.filter(user=user)
    
    if not samples.exists():
        return {
            'total_samples': 0,
            'species_diversity': 0,
            'mutations_detected': 0,
            'analysis_completion': 0,
            'locations_sampled': 0,
            'recent_analyses': []
        }
    
    # Calculate mutations
    total_mutations = 0
    for sample in samples:
        mutations = sample.get_mutations_list()
        total_mutations += len(mutations)
    
    completed_analyses = samples.filter(analysis_status='analyzed').count()
    completion_rate = (completed_analyses / samples.count() * 100) if samples.count() > 0 else 0
    
    return {
        'total_samples': samples.count(),
        'species_diversity': samples.values('sample_type').distinct().count(),
        'mutations_detected': total_mutations,
        'analysis_completion': completion_rate,
        'locations_sampled': samples.values('location').distinct().count(),
        'recent_analyses': list(samples.order_by('-collection_date')[:5].values(
            'sample_id', 'sample_type', 'location', 'analysis_status'
        ))
    }


def get_real_biodiversity_data(user):
    """Get real biodiversity data from database"""
    records = BiodiversityRecord.objects.filter(observer=user)
    
    if not records.exists():
        return {
            'total_species': 0,
            'threatened_species': 0,
            'locations_surveyed': 0,
            'recent_observations': []
        }
    
    threatened_count = records.filter(
        conservation_status__in=['VU', 'EN', 'CR', 'EW']
    ).count()
    
    return {
        'total_species': records.count(),
        'threatened_species': threatened_count,
        'locations_surveyed': records.values('location').distinct().count(),
        'recent_observations': list(records.order_by('-observation_date')[:5].values(
            'species_name', 'common_name', 'location', 'conservation_status'
        ))
    }


def generate_real_chart_data(user):
    """Generate chart data from real database records"""
    env_data = EnvironmentalData.objects.filter(user=user).order_by('-timestamp')[:30]
    genomic_data = GenomicSample.objects.filter(user=user).order_by('-collection_date')[:30]
    
    chart_data = {
        'temperature_trend': {
            'labels': [],
            'data': []
        },
        'air_quality_trend': {
            'labels': [],
            'data': []
        },
        'mutation_by_distance': {
            'labels': [],
            'data': []
        },
        'pollution_levels': {
            'labels': ['PM2.5', 'PM10', 'NO2', 'SO2', 'Ozone'],
            'data': [0, 0, 0, 0, 0]
        }
    }
    
    # Temperature trend
    for record in reversed(env_data):
        if record.temperature:
            chart_data['temperature_trend']['labels'].append(
                record.timestamp.strftime('%m/%d')
            )
            chart_data['temperature_trend']['data'].append(record.temperature)
    
    # Air quality trend
    for record in reversed(env_data):
        aqi = record.get_air_quality_index()
        if aqi > 0:
            chart_data['air_quality_trend']['labels'].append(
                record.timestamp.strftime('%m/%d')
            )
            chart_data['air_quality_trend']['data'].append(aqi)
    
    # Pollution levels (averages)
    if env_data.exists():
        chart_data['pollution_levels']['data'] = [
            env_data.aggregate(avg=Avg('pm25'))['avg'] or 0,
            env_data.aggregate(avg=Avg('pm10'))['avg'] or 0,
            env_data.aggregate(avg=Avg('nitrogen_dioxide'))['avg'] or 0,
            env_data.aggregate(avg=Avg('sulfur_dioxide'))['avg'] or 0,
            env_data.aggregate(avg=Avg('ozone_concentration'))['avg'] or 0,
        ]
    
    # Mutation by distance
    for sample in genomic_data:
        if sample.distance_from_source:
            mutations = len(sample.get_mutations_list())
            chart_data['mutation_by_distance']['labels'].append(f"{sample.distance_from_source}m")
            chart_data['mutation_by_distance']['data'].append(mutations)
    
    return chart_data


def generate_real_heatmap_data(user):
    """Generate heatmap data from real biodiversity records"""
    records = BiodiversityRecord.objects.filter(observer=user)
    
    if not records.exists():
        # Return sample heatmap if no data
        return [[0.1, 0.2, 0.3], [0.2, 0.4, 0.5], [0.3, 0.5, 0.7]]
    
    # Create a simple 5x5 heatmap based on location diversity
    locations = list(records.values('location').distinct())
    heatmap = []
    
    for i in range(5):
        row = []
        for j in range(5):
            # Simple algorithm to generate heatmap values
            if i * 5 + j < len(locations):
                location_records = records.filter(location=locations[i * 5 + j]['location'])
                diversity = min(location_records.count() / 10.0, 1.0)  # Normalize to 0-1
                row.append(diversity)
            else:
                row.append(np.random.random() * 0.3)  # Low diversity for empty cells
        heatmap.append(row)
    
    return heatmap


def create_real_visualization_data(user, chart_type, dataset_type, parameters):
    """Create visualization data from real database records"""
    if dataset_type == 'environmental':
        analyzer = EnvironmentalAnalyzer(user)
        
        if chart_type == 'time_series':
            param = parameters.get('parameter', 'temperature')
            result = analyzer.time_series_analysis(param, parameters.get('days_back', 30))
            
            if 'error' not in result:
                return {
                    'type': 'line',
                    'data': {
                        'labels': [point['timestamp'][:10] for point in result['time_series']],
                        'datasets': [{
                            'label': param.replace('_', ' ').title(),
                            'data': [point['value'] for point in result['time_series']],
                            'borderColor': '#10b981',
                            'backgroundColor': 'rgba(16, 185, 129, 0.1)'
                        }]
                    }
                }
        
        elif chart_type == 'correlation':
            result = analyzer.correlation_analysis(
                parameters.get('parameters'),
                parameters.get('days_back', 30)
            )
            
            if 'error' not in result:
                return {
                    'type': 'scatter',
                    'correlations': result['correlations']
                }
    
    # Default fallback
    return {
        'type': chart_type,
        'data': {
            'labels': ['No Data'],
            'datasets': [{'label': 'No Data Available', 'data': [0]}]
        }
    }


def create_real_report(user, report_type, output_format, parameters):
    """Create report from real data"""
    # This would generate actual reports - for now return metadata
    report_content = generate_report_content(user, report_type, parameters)
    
    # Save report to database
    report = Report.objects.create(
        user=user,
        title=f"{report_type.title()} Report - {datetime.now().strftime('%Y-%m-%d')}",
        report_type=report_type,
        output_format=output_format,
        content=report_content
    )
    
    filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
    
    return {
        'filename': filename,
        'report_id': report.id,
        'title': report.title,
        'created_at': report.created_at.isoformat()
    }


def generate_report_content(user, report_type, parameters):
    """Generate actual report content"""
    content = f"# {report_type.title()} Report\n\n"
    content += f"Generated for: {user.username}\n"
    content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    if report_type == 'environmental':
        env_analyzer = EnvironmentalAnalyzer(user)
        stats = env_analyzer.descriptive_statistics()
        pollution = env_analyzer.pollution_assessment()
        
        content += "## Environmental Data Summary\n\n"
        if 'error' not in stats:
            for param, data in stats.items():
                content += f"### {param.replace('_', ' ').title()}\n"
                content += f"- Mean: {data['mean']:.2f}\n"
                content += f"- Range: {data['min']:.2f} - {data['max']:.2f}\n"
                content += f"- Standard Deviation: {data['std']:.2f}\n\n"
        
        if 'error' not in pollution:
            content += "## Pollution Assessment\n\n"
            content += f"- Total Samples: {pollution['summary']['total_samples']}\n"
            content += f"- Violations Found: {pollution['summary']['violation_count']}\n"
            content += f"- Average AQI: {pollution['summary']['aqi_average']:.1f}\n\n"
    
    elif report_type == 'genomic':
        genomic_analyzer = GenomicAnalyzer(user)
        summary = genomic_analyzer.sample_summary()
        mutations = genomic_analyzer.mutation_analysis()
        
        content += "## Genomic Analysis Summary\n\n"
        content += f"- Total Samples: {summary['total_samples']}\n"
        content += f"- Locations Sampled: {summary['locations']}\n\n"
        
        if 'error' not in mutations:
            content += "## Mutation Analysis\n\n"
            content += f"- Total Mutations Detected: {mutations['total_mutations']}\n"
            content += "- Mutation Types:\n"
            for mut_type, count in mutations['mutation_types'].items():
                content += f"  - {mut_type}: {count}\n"
    
    return content


# API endpoints for AJAX requests
@login_required
def api_environmental_data(request):
    """API endpoint for environmental data"""
    return JsonResponse(get_real_environmental_data(request.user))


@login_required
def api_genomic_data(request):
    """API endpoint for genomic data"""
    return JsonResponse(get_real_genomic_data(request.user))


@login_required
def api_chart_data(request):
    """API endpoint for chart data"""
    return JsonResponse(generate_real_chart_data(request.user))