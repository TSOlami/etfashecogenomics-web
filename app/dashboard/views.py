from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
import json


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # For demo purposes, accept any username/password combination
        if username and password:
            # Try to get or create a user for demo purposes
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
            
            # Authenticate and login
            user = authenticate(request, username=username, password=password)
            if not user:
                # For demo, create and authenticate
                user = User.objects.get(username=username)
                login(request, user)
            else:
                login(request, user)
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'dashboard/login.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'dashboard/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'dashboard/signup.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'dashboard/signup.html')


@login_required
def dashboard_view(request):
    # Hardcoded data matching the demo
    context = {
        'user': request.user,
        'environmental_data': get_environmental_data(),
        'genomic_data': get_genomic_data(),
        'heatmap_data': get_heatmap_data(),
        'chart_data': get_chart_data(),
    }
    return render(request, 'dashboard/dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


def get_environmental_data():
    """Return hardcoded environmental monitoring data"""
    return {
        'temperature': {'value': 23.5, 'unit': '°C', 'status': 'normal'},
        'humidity': {'value': 65, 'unit': '%', 'status': 'normal'},
        'ph_level': {'value': 7.2, 'unit': 'pH', 'status': 'optimal'},
        'oxygen': {'value': 8.5, 'unit': 'mg/L', 'status': 'good'},
        'turbidity': {'value': 2.1, 'unit': 'NTU', 'status': 'clear'},
        'conductivity': {'value': 450, 'unit': 'μS/cm', 'status': 'normal'},
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
    """Return hardcoded chart data"""
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
        }
    }