import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from io import BytesIO
import base64
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Max, Min
from .models import EnvironmentalReading, Location, PollutantType, SampleBatch
import logging

logger = logging.getLogger('dashboard')

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class VisualizationGenerator:
    """Generate various types of visualizations for environmental data"""
    
    def __init__(self, user):
        self.user = user
        self.colors = {
            'primary': '#10b981',
            'secondary': '#06b6d4', 
            'accent': '#8b5cf6',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'success': '#22c55e'
        }
    
    def get_data_for_visualization(self, filters=None):
        """Get environmental data based on filters"""
        queryset = EnvironmentalReading.objects.filter(
            created_by=self.user,
            quality_flag='valid'
        ).select_related('location', 'pollutant_type')
        
        if filters:
            if filters.get('pollutant_types'):
                queryset = queryset.filter(pollutant_type__in=filters['pollutant_types'])
            if filters.get('locations'):
                queryset = queryset.filter(location__in=filters['locations'])
            if filters.get('date_from'):
                queryset = queryset.filter(measurement_date__gte=filters['date_from'])
            if filters.get('date_to'):
                queryset = queryset.filter(measurement_date__lte=filters['date_to'])
            if filters.get('batches'):
                queryset = queryset.filter(batches__batch__in=filters['batches'])
        
        return queryset
    
    def prepare_dataframe(self, queryset):
        """Convert queryset to pandas DataFrame"""
        data = []
        for reading in queryset:
            data.append({
                'location_name': reading.location.name,
                'pollutant_name': reading.pollutant_type.name,
                'concentration': float(reading.concentration),
                'measurement_date': reading.measurement_date,
                'latitude': float(reading.location.latitude) if reading.location.latitude else None,
                'longitude': float(reading.location.longitude) if reading.location.longitude else None,
                'site_type': reading.location.site_type,
                'who_standard': float(reading.pollutant_type.who_standard) if reading.pollutant_type.who_standard else None,
                'nesrea_standard': float(reading.pollutant_type.nesrea_standard) if reading.pollutant_type.nesrea_standard else None,
                'temperature': float(reading.temperature) if reading.temperature else None,
                'humidity': float(reading.humidity) if reading.humidity else None,
                'wind_speed': float(reading.wind_speed) if reading.wind_speed else None,
            })
        
        return pd.DataFrame(data)
    
    def generate_time_series_chart(self, filters=None, chart_type='line'):
        """Generate time series visualization"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for visualization'}
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Group by pollutant and create traces
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant].sort_values('measurement_date')
            
            if chart_type == 'line':
                fig.add_trace(go.Scatter(
                    x=pollutant_data['measurement_date'],
                    y=pollutant_data['concentration'],
                    mode='lines+markers',
                    name=pollutant,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
            elif chart_type == 'scatter':
                fig.add_trace(go.Scatter(
                    x=pollutant_data['measurement_date'],
                    y=pollutant_data['concentration'],
                    mode='markers',
                    name=pollutant,
                    marker=dict(size=8, opacity=0.7)
                ))
        
        # Update layout
        fig.update_layout(
            title='Pollutant Concentrations Over Time',
            xaxis_title='Date',
            yaxis_title='Concentration',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }
    
    def generate_spatial_map(self, filters=None):
        """Generate spatial distribution map"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        # Filter out records without coordinates
        df = df.dropna(subset=['latitude', 'longitude'])
        
        if df.empty:
            return {'error': 'No location data available for mapping'}
        
        # Aggregate data by location
        location_data = df.groupby(['location_name', 'latitude', 'longitude']).agg({
            'concentration': ['mean', 'max', 'count'],
            'pollutant_name': lambda x: ', '.join(x.unique())
        }).reset_index()
        
        # Flatten column names
        location_data.columns = ['location_name', 'latitude', 'longitude', 'mean_concentration', 
                               'max_concentration', 'reading_count', 'pollutants']
        
        # Create map
        fig = px.scatter_mapbox(
            location_data,
            lat='latitude',
            lon='longitude',
            size='reading_count',
            color='mean_concentration',
            hover_name='location_name',
            hover_data={
                'mean_concentration': ':.3f',
                'max_concentration': ':.3f',
                'reading_count': True,
                'pollutants': True
            },
            color_continuous_scale='Viridis',
            size_max=20,
            zoom=10,
            mapbox_style='open-street-map',
            title='Spatial Distribution of Pollutant Concentrations'
        )
        
        fig.update_layout(height=600)
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }
    
    def generate_correlation_heatmap(self, filters=None):
        """Generate correlation heatmap between pollutants"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for correlation analysis'}
        
        # Pivot data to get pollutants as columns
        pivot_df = df.pivot_table(
            index=['location_name', 'measurement_date'],
            columns='pollutant_name',
            values='concentration'
        )
        
        if pivot_df.shape[1] < 2:
            return {'error': 'Need at least 2 pollutants for correlation analysis'}
        
        # Calculate correlation matrix
        corr_matrix = pivot_df.corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect='auto',
            color_continuous_scale='RdBu_r',
            title='Pollutant Correlation Matrix'
        )
        
        fig.update_layout(height=500)
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }
    
    def generate_box_plot(self, filters=None, group_by='location'):
        """Generate box plot for concentration distributions"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for box plot'}
        
        # Create box plot
        if group_by == 'location':
            fig = px.box(
                df,
                x='location_name',
                y='concentration',
                color='pollutant_name',
                title='Concentration Distribution by Location'
            )
        else:  # group by pollutant
            fig = px.box(
                df,
                x='pollutant_name',
                y='concentration',
                color='location_name',
                title='Concentration Distribution by Pollutant'
            )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }
    
    def generate_compliance_chart(self, filters=None):
        """Generate compliance visualization"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for compliance chart'}
        
        # Calculate compliance for each pollutant
        compliance_data = []
        
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            
            for standard_col, standard_name in [('who_standard', 'WHO'), 
                                              ('nesrea_standard', 'NESREA')]:
                if pollutant_data[standard_col].notna().any():
                    standard_value = pollutant_data[standard_col].iloc[0]
                    exceedances = (pollutant_data['concentration'] > standard_value).sum()
                    total = len(pollutant_data)
                    compliance_rate = ((total - exceedances) / total) * 100
                    
                    compliance_data.append({
                        'pollutant': pollutant,
                        'standard': standard_name,
                        'compliance_rate': compliance_rate,
                        'exceedances': exceedances,
                        'total_readings': total
                    })
        
        if not compliance_data:
            return {'error': 'No standard data available for compliance analysis'}
        
        compliance_df = pd.DataFrame(compliance_data)
        
        # Create grouped bar chart
        fig = px.bar(
            compliance_df,
            x='pollutant',
            y='compliance_rate',
            color='standard',
            title='Regulatory Compliance Rates by Pollutant',
            labels={'compliance_rate': 'Compliance Rate (%)', 'pollutant': 'Pollutant'},
            text='compliance_rate'
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500, yaxis_range=[0, 105])
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }
    
    def generate_trend_analysis_chart(self, filters=None, time_period='monthly'):
        """Generate trend analysis visualization"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for trend analysis'}
        
        # Group by time period
        df['date'] = pd.to_datetime(df['measurement_date'])
        
        if time_period == 'daily':
            df['period'] = df['date'].dt.date
        elif time_period == 'weekly':
            df['period'] = df['date'].dt.to_period('W').astype(str)
        elif time_period == 'monthly':
            df['period'] = df['date'].dt.to_period('M').astype(str)
        elif time_period == 'quarterly':
            df['period'] = df['date'].dt.to_period('Q').astype(str)
        else:
            df['period'] = df['date'].dt.to_period('Y').astype(str)
        
        # Calculate trends for each pollutant
        fig = make_subplots(
            rows=len(df['pollutant_name'].unique()),
            cols=1,
            subplot_titles=df['pollutant_name'].unique(),
            vertical_spacing=0.1
        )
        
        for i, pollutant in enumerate(df['pollutant_name'].unique(), 1):
            pollutant_data = df[df['pollutant_name'] == pollutant]
            
            # Calculate mean concentration per period
            trend_data = pollutant_data.groupby('period')['concentration'].agg([
                'mean', 'std', 'count'
            ]).reset_index()
            
            # Add trend line
            fig.add_trace(
                go.Scatter(
                    x=trend_data['period'],
                    y=trend_data['mean'],
                    mode='lines+markers',
                    name=f'{pollutant} Mean',
                    error_y=dict(type='data', array=trend_data['std']),
                    showlegend=i==1
                ),
                row=i, col=1
            )
        
        fig.update_layout(
            height=300 * len(df['pollutant_name'].unique()),
            title=f'Pollutant Concentration Trends ({time_period.title()})',
            showlegend=True
        )
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }
    
    def generate_environmental_factors_chart(self, filters=None):
        """Generate environmental factors correlation chart"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        # Filter out records without environmental data
        env_df = df.dropna(subset=['temperature', 'humidity'])
        
        if env_df.empty:
            return {'error': 'No environmental data available'}
        
        # Create subplot for each pollutant
        pollutants = env_df['pollutant_name'].unique()
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Temperature vs Concentration', 'Humidity vs Concentration',
                          'Wind Speed vs Concentration', 'Temporal Pattern'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        colors = px.colors.qualitative.Set1[:len(pollutants)]
        
        for i, pollutant in enumerate(pollutants):
            pollutant_data = env_df[env_df['pollutant_name'] == pollutant]
            color = colors[i % len(colors)]
            
            # Temperature vs Concentration
            fig.add_trace(
                go.Scatter(
                    x=pollutant_data['temperature'],
                    y=pollutant_data['concentration'],
                    mode='markers',
                    name=pollutant,
                    marker=dict(color=color, opacity=0.6),
                    showlegend=i==0
                ),
                row=1, col=1
            )
            
            # Humidity vs Concentration
            fig.add_trace(
                go.Scatter(
                    x=pollutant_data['humidity'],
                    y=pollutant_data['concentration'],
                    mode='markers',
                    name=pollutant,
                    marker=dict(color=color, opacity=0.6),
                    showlegend=False
                ),
                row=1, col=2
            )
            
            # Wind Speed vs Concentration (if available)
            wind_data = pollutant_data.dropna(subset=['wind_speed'])
            if not wind_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=wind_data['wind_speed'],
                        y=wind_data['concentration'],
                        mode='markers',
                        name=pollutant,
                        marker=dict(color=color, opacity=0.6),
                        showlegend=False
                    ),
                    row=2, col=1
                )
            
            # Temporal pattern
            daily_avg = pollutant_data.groupby(pollutant_data['measurement_date'].dt.hour)['concentration'].mean()
            fig.add_trace(
                go.Scatter(
                    x=daily_avg.index,
                    y=daily_avg.values,
                    mode='lines+markers',
                    name=pollutant,
                    line=dict(color=color),
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Update axes labels
        fig.update_xaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_xaxes(title_text="Humidity (%)", row=1, col=2)
        fig.update_xaxes(title_text="Wind Speed (m/s)", row=2, col=1)
        fig.update_xaxes(title_text="Hour of Day", row=2, col=2)
        
        fig.update_yaxes(title_text="Concentration", row=1, col=1)
        fig.update_yaxes(title_text="Concentration", row=1, col=2)
        fig.update_yaxes(title_text="Concentration", row=2, col=1)
        fig.update_yaxes(title_text="Concentration", row=2, col=2)
        
        fig.update_layout(
            height=800,
            title='Environmental Factors vs Pollutant Concentrations'
        )
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }
    
    def generate_dashboard_summary(self, filters=None):
        """Generate comprehensive dashboard with multiple visualizations"""
        queryset = self.get_data_for_visualization(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for dashboard'}
        
        # Create dashboard with multiple subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Concentration by Location', 'Temporal Trends',
                'Pollutant Distribution', 'Compliance Status',
                'Site Type Analysis', 'Data Coverage'
            ],
            specs=[
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "box"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "bar"}]
            ]
        )
        
        # 1. Average concentration by location
        location_avg = df.groupby('location_name')['concentration'].mean().sort_values(ascending=True)
        fig.add_trace(
            go.Bar(x=location_avg.values, y=location_avg.index, orientation='h', name='Avg Concentration'),
            row=1, col=1
        )
        
        # 2. Temporal trends (monthly averages)
        df['month'] = pd.to_datetime(df['measurement_date']).dt.to_period('M').astype(str)
        monthly_data = df.groupby(['month', 'pollutant_name'])['concentration'].mean().reset_index()
        
        for pollutant in monthly_data['pollutant_name'].unique():
            pollutant_data = monthly_data[monthly_data['pollutant_name'] == pollutant]
            fig.add_trace(
                go.Scatter(
                    x=pollutant_data['month'],
                    y=pollutant_data['concentration'],
                    mode='lines+markers',
                    name=pollutant
                ),
                row=1, col=2
            )
        
        # 3. Pollutant distribution (box plot)
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            fig.add_trace(
                go.Box(y=pollutant_data['concentration'], name=pollutant),
                row=2, col=1
            )
        
        # 4. Compliance status
        compliance_data = []
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            if pollutant_data['who_standard'].notna().any():
                standard = pollutant_data['who_standard'].iloc[0]
                compliant = (pollutant_data['concentration'] <= standard).sum()
                total = len(pollutant_data)
                compliance_data.append({
                    'pollutant': pollutant,
                    'compliance_rate': (compliant / total) * 100
                })
        
        if compliance_data:
            compliance_df = pd.DataFrame(compliance_data)
            fig.add_trace(
                go.Bar(
                    x=compliance_df['pollutant'],
                    y=compliance_df['compliance_rate'],
                    name='Compliance Rate'
                ),
                row=2, col=2
            )
        
        # 5. Site type distribution
        site_counts = df['site_type'].value_counts()
        fig.add_trace(
            go.Pie(labels=site_counts.index, values=site_counts.values, name='Site Types'),
            row=3, col=1
        )
        
        # 6. Data coverage by month
        coverage_data = df.groupby('month').size()
        fig.add_trace(
            go.Bar(x=coverage_data.index, y=coverage_data.values, name='Readings per Month'),
            row=3, col=2
        )
        
        fig.update_layout(
            height=1200,
            title='Environmental Monitoring Dashboard',
            showlegend=True
        )
        
        return {
            'chart_html': fig.to_html(include_plotlyjs='cdn'),
            'chart_json': fig.to_json()
        }


class ReportGenerator:
    """Generate comprehensive environmental monitoring reports"""
    
    def __init__(self, user):
        self.user = user
        self.visualization_generator = VisualizationGenerator(user)
    
    def generate_comprehensive_report(self, filters=None, include_charts=True):
        """Generate a comprehensive environmental monitoring report"""
        queryset = self.visualization_generator.get_data_for_visualization(filters)
        df = self.visualization_generator.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for report generation'}
        
        report = {
            'title': 'Environmental Monitoring Report',
            'generated_at': datetime.now().isoformat(),
            'period': self._get_report_period(df),
            'executive_summary': self._generate_executive_summary(df),
            'data_overview': self._generate_data_overview(df),
            'pollutant_analysis': self._generate_pollutant_analysis(df),
            'spatial_analysis': self._generate_spatial_analysis(df),
            'temporal_analysis': self._generate_temporal_analysis(df),
            'compliance_analysis': self._generate_compliance_analysis(df),
            'environmental_factors': self._generate_environmental_factors_analysis(df),
            'recommendations': self._generate_recommendations(df),
            'methodology': self._generate_methodology_section(),
            'data_quality': self._generate_data_quality_section(df)
        }
        
        if include_charts:
            report['visualizations'] = self._generate_report_visualizations(filters)
        
        return report
    
    def _get_report_period(self, df):
        """Get the time period covered by the report"""
        start_date = df['measurement_date'].min()
        end_date = df['measurement_date'].max()
        
        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'duration_days': (end_date - start_date).days
        }
    
    def _generate_executive_summary(self, df):
        """Generate executive summary"""
        total_readings = len(df)
        unique_locations = df['location_name'].nunique()
        unique_pollutants = df['pollutant_name'].nunique()
        
        # Calculate compliance rates
        compliance_issues = []
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            if pollutant_data['who_standard'].notna().any():
                standard = pollutant_data['who_standard'].iloc[0]
                exceedances = (pollutant_data['concentration'] > standard).sum()
                if exceedances > 0:
                    compliance_issues.append({
                        'pollutant': pollutant,
                        'exceedances': exceedances,
                        'total_readings': len(pollutant_data),
                        'exceedance_rate': (exceedances / len(pollutant_data)) * 100
                    })
        
        return {
            'total_readings': total_readings,
            'unique_locations': unique_locations,
            'unique_pollutants': unique_pollutants,
            'compliance_issues': compliance_issues,
            'key_findings': self._generate_key_findings(df),
            'overall_assessment': self._generate_overall_assessment(df, compliance_issues)
        }
    
    def _generate_data_overview(self, df):
        """Generate data overview section"""
        return {
            'sampling_locations': df.groupby('location_name').agg({
                'concentration': ['count', 'mean', 'std'],
                'pollutant_name': lambda x: list(x.unique())
            }).to_dict(),
            'pollutant_summary': df.groupby('pollutant_name').agg({
                'concentration': ['count', 'mean', 'std', 'min', 'max'],
                'location_name': lambda x: list(x.unique())
            }).to_dict(),
            'temporal_coverage': df.groupby(df['measurement_date'].dt.date)['concentration'].count().to_dict()
        }
    
    def _generate_pollutant_analysis(self, df):
        """Generate detailed pollutant analysis"""
        analysis = {}
        
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            
            analysis[pollutant] = {
                'descriptive_stats': {
                    'count': len(pollutant_data),
                    'mean': float(pollutant_data['concentration'].mean()),
                    'median': float(pollutant_data['concentration'].median()),
                    'std': float(pollutant_data['concentration'].std()),
                    'min': float(pollutant_data['concentration'].min()),
                    'max': float(pollutant_data['concentration'].max()),
                    'q25': float(pollutant_data['concentration'].quantile(0.25)),
                    'q75': float(pollutant_data['concentration'].quantile(0.75))
                },
                'spatial_distribution': pollutant_data.groupby('location_name')['concentration'].agg(['mean', 'count']).to_dict(),
                'temporal_pattern': self._analyze_temporal_pattern(pollutant_data),
                'regulatory_comparison': self._compare_with_standards(pollutant_data)
            }
        
        return analysis
    
    def _generate_spatial_analysis(self, df):
        """Generate spatial analysis section"""
        spatial_data = df.dropna(subset=['latitude', 'longitude'])
        
        if spatial_data.empty:
            return {'error': 'No spatial data available'}
        
        return {
            'location_summary': spatial_data.groupby('location_name').agg({
                'concentration': ['mean', 'max', 'count'],
                'latitude': 'first',
                'longitude': 'first',
                'site_type': 'first'
            }).to_dict(),
            'site_type_analysis': spatial_data.groupby('site_type')['concentration'].agg(['mean', 'count']).to_dict(),
            'hotspot_analysis': self._identify_pollution_hotspots(spatial_data)
        }
    
    def _generate_temporal_analysis(self, df):
        """Generate temporal analysis section"""
        df['hour'] = pd.to_datetime(df['measurement_date']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['measurement_date']).dt.day_name()
        df['month'] = pd.to_datetime(df['measurement_date']).dt.month_name()
        
        return {
            'hourly_patterns': df.groupby('hour')['concentration'].mean().to_dict(),
            'daily_patterns': df.groupby('day_of_week')['concentration'].mean().to_dict(),
            'monthly_patterns': df.groupby('month')['concentration'].mean().to_dict(),
            'trend_analysis': self._analyze_trends(df)
        }
    
    def _generate_compliance_analysis(self, df):
        """Generate compliance analysis section"""
        compliance_results = {}
        
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            compliance_results[pollutant] = {}
            
            for standard_col, standard_name in [('who_standard', 'WHO'), ('nesrea_standard', 'NESREA')]:
                if pollutant_data[standard_col].notna().any():
                    standard_value = pollutant_data[standard_col].iloc[0]
                    exceedances = pollutant_data['concentration'] > standard_value
                    
                    compliance_results[pollutant][standard_name] = {
                        'standard_value': float(standard_value),
                        'exceedances': int(exceedances.sum()),
                        'total_readings': len(pollutant_data),
                        'compliance_rate': float(((~exceedances).sum() / len(pollutant_data)) * 100),
                        'max_exceedance': float(pollutant_data[exceedances]['concentration'].max()) if exceedances.any() else 0,
                        'exceedance_locations': pollutant_data[exceedances]['location_name'].unique().tolist() if exceedances.any() else []
                    }
        
        return compliance_results
    
    def _generate_environmental_factors_analysis(self, df):
        """Generate environmental factors analysis"""
        env_data = df.dropna(subset=['temperature', 'humidity'])
        
        if env_data.empty:
            return {'error': 'No environmental data available'}
        
        correlations = {}
        for pollutant in env_data['pollutant_name'].unique():
            pollutant_data = env_data[env_data['pollutant_name'] == pollutant]
            
            correlations[pollutant] = {
                'temperature_correlation': float(pollutant_data[['temperature', 'concentration']].corr().iloc[0, 1]),
                'humidity_correlation': float(pollutant_data[['humidity', 'concentration']].corr().iloc[0, 1])
            }
            
            if 'wind_speed' in pollutant_data.columns and pollutant_data['wind_speed'].notna().any():
                wind_data = pollutant_data.dropna(subset=['wind_speed'])
                if len(wind_data) > 1:
                    correlations[pollutant]['wind_speed_correlation'] = float(wind_data[['wind_speed', 'concentration']].corr().iloc[0, 1])
        
        return correlations
    
    def _generate_recommendations(self, df):
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for compliance issues
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            if pollutant_data['who_standard'].notna().any():
                standard = pollutant_data['who_standard'].iloc[0]
                exceedances = (pollutant_data['concentration'] > standard).sum()
                if exceedances > 0:
                    recommendations.append({
                        'priority': 'High',
                        'category': 'Compliance',
                        'recommendation': f'Address {pollutant} exceedances at {exceedances} measurement points',
                        'details': f'{pollutant} exceeded WHO standards in {(exceedances/len(pollutant_data)*100):.1f}% of measurements'
                    })
        
        # Check for data gaps
        date_range = pd.date_range(df['measurement_date'].min(), df['measurement_date'].max(), freq='D')
        missing_dates = len(date_range) - df['measurement_date'].dt.date.nunique()
        if missing_dates > 0:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Data Quality',
                'recommendation': 'Improve temporal coverage of monitoring',
                'details': f'{missing_dates} days without measurements in the monitoring period'
            })
        
        # Check for spatial coverage
        if df['latitude'].notna().sum() < len(df) * 0.8:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Data Quality',
                'recommendation': 'Improve spatial data collection',
                'details': 'Many measurements lack GPS coordinates for spatial analysis'
            })
        
        return recommendations
    
    def _generate_methodology_section(self):
        """Generate methodology section"""
        return {
            'data_collection': 'Environmental measurements collected using standardized protocols',
            'quality_control': 'Data filtered to include only valid measurements (quality_flag = valid)',
            'statistical_methods': 'Descriptive statistics, correlation analysis, and compliance assessment',
            'standards_reference': 'WHO and NESREA environmental quality standards',
            'visualization_tools': 'Interactive charts and maps generated using Plotly',
            'limitations': [
                'Analysis limited to available data points',
                'Spatial analysis requires GPS coordinates',
                'Temporal trends depend on measurement frequency'
            ]
        }
    
    def _generate_data_quality_section(self, df):
        """Generate data quality assessment"""
        total_readings = len(df)
        
        return {
            'completeness': {
                'total_readings': total_readings,
                'spatial_coverage': float(df['latitude'].notna().sum() / total_readings * 100),
                'temporal_coverage': df['measurement_date'].dt.date.nunique(),
                'environmental_data_coverage': float(df['temperature'].notna().sum() / total_readings * 100)
            },
            'data_distribution': {
                'readings_per_location': df.groupby('location_name').size().to_dict(),
                'readings_per_pollutant': df.groupby('pollutant_name').size().to_dict()
            },
            'outlier_analysis': self._detect_outliers(df)
        }
    
    def _generate_report_visualizations(self, filters):
        """Generate visualizations for the report"""
        visualizations = {}
        
        # Generate key visualizations
        viz_types = [
            'time_series_chart',
            'spatial_map',
            'correlation_heatmap',
            'compliance_chart',
            'box_plot',
            'environmental_factors_chart'
        ]
        
        for viz_type in viz_types:
            try:
                if viz_type == 'time_series_chart':
                    result = self.visualization_generator.generate_time_series_chart(filters)
                elif viz_type == 'spatial_map':
                    result = self.visualization_generator.generate_spatial_map(filters)
                elif viz_type == 'correlation_heatmap':
                    result = self.visualization_generator.generate_correlation_heatmap(filters)
                elif viz_type == 'compliance_chart':
                    result = self.visualization_generator.generate_compliance_chart(filters)
                elif viz_type == 'box_plot':
                    result = self.visualization_generator.generate_box_plot(filters)
                elif viz_type == 'environmental_factors_chart':
                    result = self.visualization_generator.generate_environmental_factors_chart(filters)
                
                if 'error' not in result:
                    visualizations[viz_type] = result
                    
            except Exception as e:
                logger.error(f"Error generating {viz_type}: {str(e)}")
                visualizations[viz_type] = {'error': str(e)}
        
        return visualizations
    
    # Helper methods
    def _generate_key_findings(self, df):
        """Generate key findings from the data"""
        findings = []
        
        # Highest concentration pollutant
        max_conc = df.loc[df['concentration'].idxmax()]
        findings.append(f"Highest concentration recorded: {max_conc['concentration']:.3f} for {max_conc['pollutant_name']} at {max_conc['location_name']}")
        
        # Most monitored pollutant
        most_monitored = df['pollutant_name'].value_counts().index[0]
        findings.append(f"Most frequently monitored pollutant: {most_monitored}")
        
        # Location with most readings
        most_active_location = df['location_name'].value_counts().index[0]
        findings.append(f"Most active monitoring location: {most_active_location}")
        
        return findings
    
    def _generate_overall_assessment(self, df, compliance_issues):
        """Generate overall assessment"""
        if not compliance_issues:
            return "Overall environmental quality appears to be within acceptable limits based on available standards."
        else:
            total_issues = sum(issue['exceedances'] for issue in compliance_issues)
            return f"Environmental monitoring identified {total_issues} standard exceedances across {len(compliance_issues)} pollutants requiring attention."
    
    def _analyze_temporal_pattern(self, pollutant_data):
        """Analyze temporal patterns for a specific pollutant"""
        pollutant_data['hour'] = pd.to_datetime(pollutant_data['measurement_date']).dt.hour
        hourly_avg = pollutant_data.groupby('hour')['concentration'].mean()
        
        peak_hour = hourly_avg.idxmax()
        min_hour = hourly_avg.idxmin()
        
        return {
            'peak_hour': int(peak_hour),
            'peak_concentration': float(hourly_avg[peak_hour]),
            'minimum_hour': int(min_hour),
            'minimum_concentration': float(hourly_avg[min_hour]),
            'daily_variation': float(hourly_avg.std())
        }
    
    def _compare_with_standards(self, pollutant_data):
        """Compare pollutant data with regulatory standards"""
        comparison = {}
        
        for standard_col, standard_name in [('who_standard', 'WHO'), ('nesrea_standard', 'NESREA')]:
            if pollutant_data[standard_col].notna().any():
                standard_value = pollutant_data[standard_col].iloc[0]
                mean_conc = pollutant_data['concentration'].mean()
                max_conc = pollutant_data['concentration'].max()
                
                comparison[standard_name] = {
                    'standard_value': float(standard_value),
                    'mean_ratio': float(mean_conc / standard_value),
                    'max_ratio': float(max_conc / standard_value),
                    'exceeds_standard': bool(max_conc > standard_value)
                }
        
        return comparison
    
    def _identify_pollution_hotspots(self, spatial_data):
        """Identify pollution hotspots based on spatial data"""
        location_stats = spatial_data.groupby('location_name').agg({
            'concentration': ['mean', 'max', 'count'],
            'latitude': 'first',
            'longitude': 'first'
        })
        
        # Identify locations with highest average concentrations
        mean_threshold = spatial_data['concentration'].quantile(0.75)
        hotspots = location_stats[location_stats[('concentration', 'mean')] > mean_threshold]
        
        return {
            'threshold': float(mean_threshold),
            'hotspot_locations': hotspots.index.tolist(),
            'hotspot_details': hotspots.to_dict()
        }
    
    def _analyze_trends(self, df):
        """Analyze temporal trends in the data"""
        df['date'] = pd.to_datetime(df['measurement_date']).dt.date
        daily_avg = df.groupby('date')['concentration'].mean()
        
        if len(daily_avg) < 3:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Simple linear trend
        x = np.arange(len(daily_avg))
        y = daily_avg.values
        slope, intercept = np.polyfit(x, y, 1)
        
        return {
            'slope': float(slope),
            'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
            'daily_average_range': {
                'min': float(daily_avg.min()),
                'max': float(daily_avg.max()),
                'mean': float(daily_avg.mean())
            }
        }
    
    def _detect_outliers(self, df):
        """Detect outliers in the data"""
        outliers = {}
        
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]['concentration']
            
            Q1 = pollutant_data.quantile(0.25)
            Q3 = pollutant_data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_count = ((pollutant_data < lower_bound) | (pollutant_data > upper_bound)).sum()
            
            outliers[pollutant] = {
                'count': int(outlier_count),
                'percentage': float(outlier_count / len(pollutant_data) * 100),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            }
        
        return outliers