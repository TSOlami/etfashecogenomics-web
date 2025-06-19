import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import json
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Count, Q
from .models import EnvironmentalData, GenomicSample, BiodiversityRecord, AnalysisResult

class EnvironmentalAnalyzer:
    """Class for environmental data analysis"""
    
    def __init__(self, user):
        self.user = user
    
    def get_data_queryset(self, days_back=30):
        """Get environmental data for the specified time period"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return EnvironmentalData.objects.filter(
            user=self.user,
            timestamp__gte=cutoff_date
        )
    
    def descriptive_statistics(self, parameters=None, days_back=30):
        """Calculate descriptive statistics for environmental parameters"""
        queryset = self.get_data_queryset(days_back)
        
        if not queryset.exists():
            return {"error": "No data available for the specified period"}
        
        # Default parameters if none specified
        if not parameters:
            parameters = [
                'temperature', 'humidity', 'ph_level', 'oxygen_level',
                'pm25', 'pm10', 'ozone_concentration', 'nitrogen_dioxide',
                'lead_concentration', 'chromium_concentration'
            ]
        
        results = {}
        
        for param in parameters:
            values = list(queryset.exclude(**{f"{param}__isnull": True}).values_list(param, flat=True))
            
            if values:
                results[param] = {
                    'count': len(values),
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'q25': np.percentile(values, 25),
                    'q75': np.percentile(values, 75)
                }
        
        return results
    
    def pollution_assessment(self, days_back=30):
        """Assess pollution levels against standards"""
        queryset = self.get_data_queryset(days_back)
        
        if not queryset.exists():
            return {"error": "No data available for assessment"}
        
        violations = []
        summary = {
            'total_samples': queryset.count(),
            'locations_monitored': queryset.values('location').distinct().count(),
            'violation_count': 0,
            'aqi_average': 0
        }
        
        aqi_values = []
        
        for record in queryset:
            record_violations = record.check_pollution_standards()
            if record_violations:
                violations.extend([{
                    'location': record.location,
                    'timestamp': record.timestamp.isoformat(),
                    'violation': violation
                } for violation in record_violations])
            
            aqi = record.get_air_quality_index()
            if aqi > 0:
                aqi_values.append(aqi)
        
        summary['violation_count'] = len(violations)
        summary['aqi_average'] = np.mean(aqi_values) if aqi_values else 0
        
        return {
            'summary': summary,
            'violations': violations,
            'aqi_classification': self._classify_aqi(summary['aqi_average'])
        }
    
    def _classify_aqi(self, aqi):
        """Classify AQI value"""
        if aqi <= 50:
            return {'level': 'Good', 'color': 'green', 'description': 'Air quality is satisfactory'}
        elif aqi <= 100:
            return {'level': 'Moderate', 'color': 'yellow', 'description': 'Air quality is acceptable for most people'}
        elif aqi <= 150:
            return {'level': 'Unhealthy for Sensitive Groups', 'color': 'orange', 'description': 'Members of sensitive groups may experience health effects'}
        elif aqi <= 200:
            return {'level': 'Unhealthy', 'color': 'red', 'description': 'Everyone may begin to experience health effects'}
        else:
            return {'level': 'Very Unhealthy', 'color': 'purple', 'description': 'Health warnings of emergency conditions'}
    
    def correlation_analysis(self, parameters=None, days_back=30):
        """Perform correlation analysis between parameters"""
        queryset = self.get_data_queryset(days_back)
        
        if not queryset.exists():
            return {"error": "No data available for correlation analysis"}
        
        if not parameters:
            parameters = ['temperature', 'humidity', 'pm25', 'pm10', 'ozone_concentration']
        
        # Create DataFrame
        data = []
        for record in queryset:
            row = {}
            for param in parameters:
                value = getattr(record, param, None)
                if value is not None:
                    row[param] = value
            if len(row) >= 2:  # Need at least 2 parameters
                data.append(row)
        
        if len(data) < 3:
            return {"error": "Insufficient data for correlation analysis"}
        
        df = pd.DataFrame(data)
        correlation_matrix = df.corr()
        
        # Convert to serializable format
        correlations = []
        for i, param1 in enumerate(correlation_matrix.columns):
            for j, param2 in enumerate(correlation_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr_value = correlation_matrix.iloc[i, j]
                    if not np.isnan(corr_value):
                        correlations.append({
                            'parameter1': param1,
                            'parameter2': param2,
                            'correlation': float(corr_value),
                            'strength': self._interpret_correlation(abs(corr_value))
                        })
        
        return {
            'correlations': correlations,
            'matrix': correlation_matrix.to_dict()
        }
    
    def _interpret_correlation(self, r):
        """Interpret correlation strength"""
        if r < 0.3:
            return 'Weak'
        elif r < 0.7:
            return 'Moderate'
        else:
            return 'Strong'
    
    def time_series_analysis(self, parameter, days_back=30):
        """Analyze time series trends for a parameter"""
        queryset = self.get_data_queryset(days_back).exclude(**{f"{parameter}__isnull": True}).order_by('timestamp')
        
        if not queryset.exists():
            return {"error": f"No data available for {parameter}"}
        
        timestamps = [record.timestamp for record in queryset]
        values = [getattr(record, parameter) for record in queryset]
        
        # Calculate trend
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        return {
            'parameter': parameter,
            'data_points': len(values),
            'trend': {
                'slope': float(slope),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'interpretation': 'Increasing' if slope > 0 else 'Decreasing' if slope < 0 else 'Stable'
            },
            'time_series': [
                {'timestamp': ts.isoformat(), 'value': val}
                for ts, val in zip(timestamps, values)
            ]
        }


class GenomicAnalyzer:
    """Class for genomic data analysis"""
    
    def __init__(self, user):
        self.user = user
    
    def get_samples_queryset(self):
        """Get genomic samples for the user"""
        return GenomicSample.objects.filter(user=self.user)
    
    def sample_summary(self):
        """Get summary of genomic samples"""
        queryset = self.get_samples_queryset()
        
        return {
            'total_samples': queryset.count(),
            'by_type': dict(queryset.values('sample_type').annotate(count=Count('id')).values_list('sample_type', 'count')),
            'by_status': dict(queryset.values('analysis_status').annotate(count=Count('id')).values_list('analysis_status', 'count')),
            'locations': queryset.values('location').distinct().count(),
            'recent_samples': queryset.order_by('-collection_date')[:5].values(
                'sample_id', 'sample_type', 'location', 'collection_date', 'analysis_status'
            )
        }
    
    def mutation_analysis(self):
        """Analyze mutations across samples"""
        samples_with_mutations = self.get_samples_queryset().exclude(mutations_detected='')
        
        if not samples_with_mutations.exists():
            return {"error": "No mutation data available"}
        
        all_mutations = []
        mutation_counts = {}
        location_mutations = {}
        
        for sample in samples_with_mutations:
            mutations = sample.get_mutations_list()
            sample_location = sample.location
            
            if sample_location not in location_mutations:
                location_mutations[sample_location] = []
            
            for mutation in mutations:
                all_mutations.append({
                    'sample_id': sample.sample_id,
                    'location': sample_location,
                    'distance_from_source': sample.distance_from_source,
                    'mutation': mutation
                })
                
                mutation_type = mutation.get('type', 'unknown')
                mutation_counts[mutation_type] = mutation_counts.get(mutation_type, 0) + 1
                location_mutations[sample_location].append(mutation)
        
        return {
            'total_mutations': len(all_mutations),
            'mutation_types': mutation_counts,
            'mutations_by_location': location_mutations,
            'detailed_mutations': all_mutations
        }
    
    def distance_correlation_analysis(self):
        """Analyze correlation between distance from pollution source and mutations"""
        samples = self.get_samples_queryset().exclude(
            distance_from_source__isnull=True
        ).exclude(mutations_detected='')
        
        if samples.count() < 3:
            return {"error": "Insufficient data for distance correlation analysis"}
        
        distances = []
        mutation_counts = []
        
        for sample in samples:
            mutations = sample.get_mutations_list()
            distances.append(sample.distance_from_source)
            mutation_counts.append(len(mutations))
        
        if len(distances) < 3:
            return {"error": "Insufficient data points for correlation"}
        
        correlation, p_value = stats.pearsonr(distances, mutation_counts)
        
        return {
            'correlation': float(correlation),
            'p_value': float(p_value),
            'interpretation': self._interpret_distance_correlation(correlation, p_value),
            'data_points': len(distances),
            'scatter_data': [
                {'distance': d, 'mutations': m, 'sample_id': s.sample_id}
                for d, m, s in zip(distances, mutation_counts, samples)
            ]
        }
    
    def _interpret_distance_correlation(self, correlation, p_value):
        """Interpret distance-mutation correlation"""
        significance = "significant" if p_value < 0.05 else "not significant"
        
        if abs(correlation) < 0.3:
            strength = "weak"
        elif abs(correlation) < 0.7:
            strength = "moderate"
        else:
            strength = "strong"
        
        direction = "negative" if correlation < 0 else "positive"
        
        return f"{strength.capitalize()} {direction} correlation ({significance}, p={p_value:.4f})"


class StatisticalAnalyzer:
    """Class for statistical tests"""
    
    @staticmethod
    def t_test(group1, group2, test_type='two-sided'):
        """Perform t-test between two groups"""
        if len(group1) < 2 or len(group2) < 2:
            return {"error": "Insufficient data for t-test (need at least 2 samples per group)"}
        
        statistic, p_value = stats.ttest_ind(group1, group2, alternative=test_type)
        
        effect_size = (np.mean(group1) - np.mean(group2)) / np.sqrt(
            ((len(group1) - 1) * np.var(group1, ddof=1) + (len(group2) - 1) * np.var(group2, ddof=1)) /
            (len(group1) + len(group2) - 2)
        )
        
        return {
            'statistic': float(statistic),
            'p_value': float(p_value),
            'effect_size': float(effect_size),
            'significant': p_value < 0.05,
            'interpretation': StatisticalAnalyzer._interpret_t_test(p_value, effect_size)
        }
    
    @staticmethod
    def anova(*groups):
        """Perform one-way ANOVA"""
        if len(groups) < 2:
            return {"error": "Need at least 2 groups for ANOVA"}
        
        # Filter out empty groups
        valid_groups = [group for group in groups if len(group) >= 2]
        
        if len(valid_groups) < 2:
            return {"error": "Need at least 2 groups with sufficient data for ANOVA"}
        
        statistic, p_value = stats.f_oneway(*valid_groups)
        
        return {
            'f_statistic': float(statistic),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'groups_tested': len(valid_groups),
            'interpretation': StatisticalAnalyzer._interpret_anova(p_value)
        }
    
    @staticmethod
    def _interpret_t_test(p_value, effect_size):
        """Interpret t-test results"""
        significance = "significant" if p_value < 0.05 else "not significant"
        
        if abs(effect_size) < 0.2:
            effect = "small"
        elif abs(effect_size) < 0.8:
            effect = "medium"
        else:
            effect = "large"
        
        return f"The difference is {significance} (p={p_value:.4f}) with a {effect} effect size"
    
    @staticmethod
    def _interpret_anova(p_value):
        """Interpret ANOVA results"""
        if p_value < 0.05:
            return f"Significant differences found between groups (p={p_value:.4f})"
        else:
            return f"No significant differences found between groups (p={p_value:.4f})"


def run_analysis(user, analysis_type, dataset_type, parameters):
    """Main function to run different types of analysis"""
    
    try:
        if dataset_type == 'environmental':
            analyzer = EnvironmentalAnalyzer(user)
            
            if analysis_type == 'descriptive':
                results = analyzer.descriptive_statistics(
                    parameters.get('parameters'),
                    parameters.get('days_back', 30)
                )
            elif analysis_type == 'pollution_assessment':
                results = analyzer.pollution_assessment(parameters.get('days_back', 30))
            elif analysis_type == 'correlation':
                results = analyzer.correlation_analysis(
                    parameters.get('parameters'),
                    parameters.get('days_back', 30)
                )
            elif analysis_type == 'time_series':
                results = analyzer.time_series_analysis(
                    parameters.get('parameter'),
                    parameters.get('days_back', 30)
                )
            else:
                results = {"error": f"Unknown analysis type: {analysis_type}"}
        
        elif dataset_type == 'genomic':
            analyzer = GenomicAnalyzer(user)
            
            if analysis_type == 'sample_summary':
                results = analyzer.sample_summary()
            elif analysis_type == 'mutation_analysis':
                results = analyzer.mutation_analysis()
            elif analysis_type == 'distance_correlation':
                results = analyzer.distance_correlation_analysis()
            else:
                results = {"error": f"Unknown analysis type: {analysis_type}"}
        
        else:
            results = {"error": f"Unknown dataset type: {dataset_type}"}
        
        # Save analysis result
        if 'error' not in results:
            AnalysisResult.objects.create(
                user=user,
                analysis_type=analysis_type,
                dataset_type=dataset_type,
                parameters=json.dumps(parameters),
                results=json.dumps(results)
            )
        
        return results
    
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}