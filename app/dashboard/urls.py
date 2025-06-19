from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Data Upload URLs
    path('upload/', views.upload_data, name='upload_data'),
    path('download-template/<str:template_type>/', views.download_template, name='download_template'),
    
    # Analysis URLs
    path('api/analysis/', views.run_analysis, name='run_analysis'),
    path('api/visualization/', views.generate_visualization, name='generate_visualization'),
    path('api/report/', views.generate_report, name='generate_report'),
    
    # API endpoints (for AJAX requests)
    path('api/environmental/', views.api_environmental_data, name='api_environmental'),
    path('api/genomic/', views.api_genomic_data, name='api_genomic'),
    path('api/charts/', views.api_chart_data, name='api_charts'),
]