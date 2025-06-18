from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
import logging

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
        'heatmap_data': get_heatmap_data(),
        'chart_data': get_chart_data(),
    }
    return render(request, 'dashboard/dashboard.html', context)


def logout_view(request):
    """Handle user logout"""
    username = request.user.username if request.user.is_authenticated else "User"
    logout(request)
    logger.info(f'User {username} logged out')
    messages.success(request, f'You have been successfully logged out. Goodbye, {username}!')
    return redirect('login')


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