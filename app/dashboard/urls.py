from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API endpoints (for future AJAX requests)
    path('api/environmental/', views.api_environmental_data, name='api_environmental'),
    path('api/genomic/', views.api_genomic_data, name='api_genomic'),
    path('api/charts/', views.api_chart_data, name='api_charts'),
]