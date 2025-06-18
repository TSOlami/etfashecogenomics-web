from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Count, Avg, Max, Min, Q
from django.core.paginator import Paginator
import json
import logging
import os
import tempfile
import uuid

from .models import (
    Location, PollutantType, EnvironmentalReading, 
    SampleBatch, BatchReading, DataUploadLog
)
from .forms import DataUploadForm, LocationForm, DataPreviewForm
from .data_processor import DataProcessor, preview_data_file

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
    
    # Get user's recent data
    recent_readings = EnvironmentalReading.objects.filter(
        created_by=request.user
    ).select_related('location', 'pollutant_type').order_by('-measurement_date')[:10]
    
    recent_batches = SampleBatch.objects.filter(
        created_by=request.user
    ).order_by('-sampling_date')[:5]
    
    # Get summary statistics
    total_readings = EnvironmentalReading.objects.filter(created_by=request.user).count()
    total_locations = Location.objects.filter(created_by=request.user).count()
    total_batches = SampleBatch.objects.filter(created_by=request.user).count()
    
    # Get compliance statistics
    compliance_stats = get_compliance_statistics(request.user)
    
    context = {
        'user': request.user,
        'recent_readings': recent_readings,
        'recent_batches': recent_batches,
        'total_readings': total_readings,
        'total_locations': total_locations,
        'total_batches': total_batches,
        'compliance_stats': compliance_stats,
        'environmental_data': get_environmental_data(),
        'genomic_data': get_genomic_data(),
        'heatmap_data': get_heatmap_data(),
        'chart_data': get_chart_data(),
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def data_upload_view(request):
    """Handle data file upload and processing"""
    if request.method == 'POST':
        form = DataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save uploaded file temporarily
                uploaded_file = request.FILES['data_file']
                file_extension = os.path.splitext(uploaded_file.name)[1]
                temp_filename = f"{uuid.uuid4()}{file_extension}"
                
                # Save file
                file_path = default_storage.save(
                    f'uploads/{temp_filename}',
                    ContentFile(uploaded_file.read())
                )
                full_file_path = default_storage.path(file_path)
                
                # Create upload log
                upload_log = DataUploadLog.objects.create(
                    filename=temp_filename,
                    original_filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    file_type='xlsx' if file_extension in ['.xlsx', '.xls'] else 'csv',
                    uploaded_by=request.user,
                    processing_status='pending',
                    processing_start=timezone.now()
                )
                
                # Preview the data
                preview_result = preview_data_file(full_file_path, max_rows=10)
                
                if preview_result['success']:
                    # Store form data and file path in session for confirmation
                    request.session['upload_data'] = {
                        'file_path': file_path,
                        'upload_log_id': str(upload_log.id),
                        'batch_data': {
                            'batch_name': form.cleaned_data['batch_name'],
                            'batch_description': form.cleaned_data['batch_description'],
                            'project_name': form.cleaned_data['project_name'],
                            'project_code': form.cleaned_data['project_code'],
                            'sampling_date': form.cleaned_data['sampling_date'].isoformat(),
                            'study_type': form.cleaned_data['study_type'],
                        },
                        'options': {
                            'create_missing_locations': form.cleaned_data['create_missing_locations'],
                            'skip_invalid_rows': form.cleaned_data['skip_invalid_rows'],
                        }
                    }
                    
                    return render(request, 'dashboard/data_preview.html', {
                        'preview_data': preview_result['data'],
                        'form_data': form.cleaned_data,
                        'upload_log': upload_log
                    })
                else:
                    # Clean up on error
                    default_storage.delete(file_path)
                    upload_log.delete()
                    messages.error(request, f"Error reading file: {preview_result['error']}")
                    
            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
                messages.error(request, f"Upload failed: {str(e)}")
    else:
        form = DataUploadForm()
    
    return render(request, 'dashboard/data_upload.html', {'form': form})


@login_required
def confirm_data_import(request):
    """Confirm and process the data import"""
    if request.method == 'POST':
        upload_data = request.session.get('upload_data')
        if not upload_data:
            messages.error(request, "No upload data found. Please start over.")
            return redirect('data_upload')
        
        try:
            # Get upload log
            upload_log = DataUploadLog.objects.get(
                id=upload_data['upload_log_id'],
                uploaded_by=request.user
            )
            
            # Process the file
            processor = DataProcessor(request.user, upload_log)
            
            # Convert date string back to date object
            batch_data = upload_data['batch_data'].copy()
            batch_data['sampling_date'] = timezone.datetime.fromisoformat(
                batch_data['sampling_date']
            ).date()
            
            result = processor.process_file(
                default_storage.path(upload_data['file_path']),
                batch_data,
                upload_data['options']
            )
            
            # Clean up temporary file
            default_storage.delete(upload_data['file_path'])
            del request.session['upload_data']
            
            if result['success']:
                messages.success(
                    request, 
                    f"Data imported successfully! "
                    f"Processed: {result['processed']}, "
                    f"Successful: {result['successful']}, "
                    f"Failed: {result['failed']}"
                )
                return redirect('batch_detail', batch_id=result['batch'].id)
            else:
                messages.error(request, f"Import failed: {result['error']}")
                
        except Exception as e:
            logger.error(f"Import confirmation error: {str(e)}")
            messages.error(request, f"Import failed: {str(e)}")
    
    return redirect('data_upload')


@login_required
def batch_list_view(request):
    """List all sample batches for the user"""
    batches = SampleBatch.objects.filter(
        created_by=request.user
    ).annotate(
        reading_count=Count('readings')
    ).order_by('-sampling_date')
    
    # Pagination
    paginator = Paginator(batches, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/batch_list.html', {
        'page_obj': page_obj,
        'batches': page_obj
    })


@login_required
def batch_detail_view(request, batch_id):
    """Display detailed view of a sample batch"""
    batch = get_object_or_404(SampleBatch, id=batch_id, created_by=request.user)
    
    # Get readings for this batch
    readings = EnvironmentalReading.objects.filter(
        batches__batch=batch
    ).select_related('location', 'pollutant_type').order_by('-measurement_date')
    
    # Get summary statistics
    stats = {
        'total_readings': readings.count(),
        'locations_count': readings.values('location').distinct().count(),
        'pollutants_count': readings.values('pollutant_type').distinct().count(),
        'date_range': {
            'start': readings.aggregate(Min('measurement_date'))['measurement_date__min'],
            'end': readings.aggregate(Max('measurement_date'))['measurement_date__max']
        }
    }
    
    # Get compliance summary
    compliance_summary = get_batch_compliance_summary(batch)
    
    # Pagination for readings
    paginator = Paginator(readings, 50)
    page_number = request.GET.get('page')
    readings_page = paginator.get_page(page_number)
    
    return render(request, 'dashboard/batch_detail.html', {
        'batch': batch,
        'readings': readings_page,
        'stats': stats,
        'compliance_summary': compliance_summary
    })


def logout_view(request):
    """Handle user logout"""
    username = request.user.username if request.user.is_authenticated else "User"
    logout(request)
    logger.info(f'User {username} logged out')
    messages.success(request, f'You have been successfully logged out. Goodbye, {username}!')
    return redirect('login')


# Utility functions
def get_compliance_statistics(user):
    """Get compliance statistics for user's data"""
    readings = EnvironmentalReading.objects.filter(
        created_by=user,
        quality_flag='valid'
    ).select_related('pollutant_type')
    
    total_readings = readings.count()
    if total_readings == 0:
        return {'total': 0, 'compliant': 0, 'non_compliant': 0, 'percentage': 0}
    
    compliant_count = 0
    non_compliant_count = 0
    
    for reading in readings:
        if (reading.exceeds_who_standard or 
            reading.exceeds_nesrea_standard or 
            reading.exceeds_epa_standard):
            non_compliant_count += 1
        else:
            compliant_count += 1
    
    return {
        'total': total_readings,
        'compliant': compliant_count,
        'non_compliant': non_compliant_count,
        'percentage': (compliant_count / total_readings) * 100 if total_readings > 0 else 0
    }


def get_batch_compliance_summary(batch):
    """Get compliance summary for a specific batch"""
    readings = EnvironmentalReading.objects.filter(
        batches__batch=batch,
        quality_flag='valid'
    ).select_related('pollutant_type')
    
    summary = {
        'total': readings.count(),
        'who_violations': 0,
        'nesrea_violations': 0,
        'epa_violations': 0,
        'compliant': 0
    }
    
    for reading in readings:
        has_violation = False
        if reading.exceeds_who_standard:
            summary['who_violations'] += 1
            has_violation = True
        if reading.exceeds_nesrea_standard:
            summary['nesrea_violations'] += 1
            has_violation = True
        if reading.exceeds_epa_standard:
            summary['epa_violations'] += 1
            has_violation = True
        
        if not has_violation:
            summary['compliant'] += 1
    
    return summary


# Data functions (hardcoded for demo purposes - will be replaced with real data)
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


# API endpoints for AJAX requests (future use)
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