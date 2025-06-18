from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Data Management URLs
    path('upload/', views.data_upload_view, name='data_upload'),
    path('upload/confirm/', views.confirm_data_import, name='confirm_data_import'),
    path('batches/', views.batch_list_view, name='batch_list'),
    path('batches/<uuid:batch_id>/', views.batch_detail_view, name='batch_detail'),
    
    # Statistical Analysis URLs
    path('analysis/', views.statistical_analysis_view, name='statistical_analysis'),
    path('analysis/run/', views.run_statistical_analysis, name='run_statistical_analysis'),
    path('analysis/report/', views.generate_statistical_report, name='generate_statistical_report'),
    
    # Visualization URLs
    path('visualizations/', views.visualization_dashboard, name='visualization_dashboard'),
    path('visualizations/generate/', views.generate_visualization, name='generate_visualization'),
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/export/<str:format>/', views.export_report, name='export_report'),
    
    # API endpoints (for future AJAX requests)
    path('api/environmental/', views.api_environmental_data, name='api_environmental'),
    path('api/genomic/', views.api_genomic_data, name='api_genomic'),
    path('api/charts/', views.api_chart_data, name='api_charts'),
]