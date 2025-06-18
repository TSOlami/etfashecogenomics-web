import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import f_oneway, ttest_ind, ttest_rel, chi2_contingency, pearsonr, spearmanr
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import warnings
from datetime import datetime, timedelta
from django.db.models import Q, Avg, Count, Max, Min, StdDev
from .models import EnvironmentalReading, Location, PollutantType, SampleBatch
import logging

logger = logging.getLogger('dashboard')
warnings.filterwarnings('ignore')


class StatisticalAnalyzer:
    """Comprehensive statistical analysis for environmental data"""
    
    def __init__(self, user):
        self.user = user
        self.results = {}
        
    def get_data_for_analysis(self, filters=None):
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
        """Convert queryset to pandas DataFrame for analysis"""
        data = []
        for reading in queryset:
            data.append({
                'id': reading.id,
                'location_id': reading.location.id,
                'location_name': reading.location.name,
                'pollutant_id': reading.pollutant_type.id,
                'pollutant_name': reading.pollutant_type.name,
                'concentration': float(reading.concentration),
                'measurement_date': reading.measurement_date,
                'temperature': float(reading.temperature) if reading.temperature else None,
                'humidity': float(reading.humidity) if reading.humidity else None,
                'pressure': float(reading.pressure) if reading.pressure else None,
                'wind_speed': float(reading.wind_speed) if reading.wind_speed else None,
                'wind_direction': float(reading.wind_direction) if reading.wind_direction else None,
                'site_type': reading.location.site_type,
                'who_standard': float(reading.pollutant_type.who_standard) if reading.pollutant_type.who_standard else None,
                'nesrea_standard': float(reading.pollutant_type.nesrea_standard) if reading.pollutant_type.nesrea_standard else None,
                'epa_standard': float(reading.pollutant_type.epa_standard) if reading.pollutant_type.epa_standard else None,
            })
        
        return pd.DataFrame(data)
    
    def descriptive_statistics(self, filters=None):
        """Calculate comprehensive descriptive statistics"""
        queryset = self.get_data_for_analysis(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        results = {}
        
        # Overall statistics
        results['overall'] = {
            'total_readings': len(df),
            'unique_locations': df['location_name'].nunique(),
            'unique_pollutants': df['pollutant_name'].nunique(),
            'date_range': {
                'start': df['measurement_date'].min().strftime('%Y-%m-%d'),
                'end': df['measurement_date'].max().strftime('%Y-%m-%d')
            }
        }
        
        # Statistics by pollutant
        results['by_pollutant'] = {}
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]['concentration']
            results['by_pollutant'][pollutant] = {
                'count': len(pollutant_data),
                'mean': float(pollutant_data.mean()),
                'median': float(pollutant_data.median()),
                'std': float(pollutant_data.std()),
                'min': float(pollutant_data.min()),
                'max': float(pollutant_data.max()),
                'q25': float(pollutant_data.quantile(0.25)),
                'q75': float(pollutant_data.quantile(0.75)),
                'skewness': float(pollutant_data.skew()),
                'kurtosis': float(pollutant_data.kurtosis())
            }
        
        # Statistics by location
        results['by_location'] = {}
        for location in df['location_name'].unique():
            location_data = df[df['location_name'] == location]['concentration']
            results['by_location'][location] = {
                'count': len(location_data),
                'mean': float(location_data.mean()),
                'median': float(location_data.median()),
                'std': float(location_data.std()),
                'pollutants_measured': df[df['location_name'] == location]['pollutant_name'].unique().tolist()
            }
        
        return results
    
    def t_test_analysis(self, group1_filters, group2_filters, test_type='independent'):
        """Perform t-test analysis between two groups"""
        group1_data = self.get_data_for_analysis(group1_filters)
        group2_data = self.get_data_for_analysis(group2_filters)
        
        df1 = self.prepare_dataframe(group1_data)
        df2 = self.prepare_dataframe(group2_data)
        
        if df1.empty or df2.empty:
            return {'error': 'Insufficient data for t-test analysis'}
        
        results = {}
        
        # Get common pollutants
        common_pollutants = set(df1['pollutant_name'].unique()) & set(df2['pollutant_name'].unique())
        
        for pollutant in common_pollutants:
            conc1 = df1[df1['pollutant_name'] == pollutant]['concentration']
            conc2 = df2[df2['pollutant_name'] == pollutant]['concentration']
            
            if len(conc1) < 2 or len(conc2) < 2:
                continue
            
            # Perform appropriate t-test
            if test_type == 'independent':
                # Check for equal variances
                levene_stat, levene_p = stats.levene(conc1, conc2)
                equal_var = levene_p > 0.05
                
                t_stat, p_value = ttest_ind(conc1, conc2, equal_var=equal_var)
                test_name = f"Independent t-test ({'equal' if equal_var else 'unequal'} variances)"
            else:
                # Paired t-test (requires same number of observations)
                min_len = min(len(conc1), len(conc2))
                t_stat, p_value = ttest_rel(conc1[:min_len], conc2[:min_len])
                test_name = "Paired t-test"
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt(((len(conc1) - 1) * conc1.var() + (len(conc2) - 1) * conc2.var()) / 
                               (len(conc1) + len(conc2) - 2))
            cohens_d = (conc1.mean() - conc2.mean()) / pooled_std if pooled_std > 0 else 0
            
            results[pollutant] = {
                'test_type': test_name,
                'group1_stats': {
                    'n': len(conc1),
                    'mean': float(conc1.mean()),
                    'std': float(conc1.std())
                },
                'group2_stats': {
                    'n': len(conc2),
                    'mean': float(conc2.mean()),
                    'std': float(conc2.std())
                },
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'cohens_d': float(cohens_d),
                'significant': p_value < 0.05,
                'interpretation': self._interpret_t_test(p_value, cohens_d, conc1.mean(), conc2.mean())
            }
        
        return results
    
    def anova_analysis(self, group_filters_list, factor_name="Group"):
        """Perform one-way ANOVA analysis across multiple groups"""
        groups_data = []
        group_names = []
        
        for i, filters in enumerate(group_filters_list):
            data = self.get_data_for_analysis(filters)
            df = self.prepare_dataframe(data)
            if not df.empty:
                groups_data.append(df)
                group_names.append(filters.get('group_name', f'Group {i+1}'))
        
        if len(groups_data) < 2:
            return {'error': 'Need at least 2 groups for ANOVA analysis'}
        
        results = {}
        
        # Get common pollutants across all groups
        common_pollutants = set(groups_data[0]['pollutant_name'].unique())
        for df in groups_data[1:]:
            common_pollutants &= set(df['pollutant_name'].unique())
        
        for pollutant in common_pollutants:
            group_concentrations = []
            group_stats = []
            
            for i, df in enumerate(groups_data):
                conc = df[df['pollutant_name'] == pollutant]['concentration']
                if len(conc) >= 2:  # Need at least 2 observations per group
                    group_concentrations.append(conc)
                    group_stats.append({
                        'group_name': group_names[i],
                        'n': len(conc),
                        'mean': float(conc.mean()),
                        'std': float(conc.std())
                    })
            
            if len(group_concentrations) < 2:
                continue
            
            # Perform ANOVA
            f_stat, p_value = f_oneway(*group_concentrations)
            
            # Calculate effect size (eta-squared)
            all_data = np.concatenate(group_concentrations)
            ss_total = np.sum((all_data - np.mean(all_data)) ** 2)
            ss_between = sum(len(group) * (np.mean(group) - np.mean(all_data)) ** 2 
                           for group in group_concentrations)
            eta_squared = ss_between / ss_total if ss_total > 0 else 0
            
            results[pollutant] = {
                'test_type': 'One-way ANOVA',
                'factor_name': factor_name,
                'group_stats': group_stats,
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'eta_squared': float(eta_squared),
                'significant': p_value < 0.05,
                'interpretation': self._interpret_anova(p_value, eta_squared, len(group_concentrations))
            }
            
            # Post-hoc analysis if significant
            if p_value < 0.05 and len(group_concentrations) > 2:
                results[pollutant]['post_hoc'] = self._tukey_hsd_analysis(
                    group_concentrations, group_names[:len(group_concentrations)]
                )
        
        return results
    
    def correlation_analysis(self, filters=None):
        """Perform correlation analysis between pollutants and environmental factors"""
        queryset = self.get_data_for_analysis(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for correlation analysis'}
        
        results = {}
        
        # Correlation between pollutants
        pollutant_matrix = df.pivot_table(
            index=['location_name', 'measurement_date'], 
            columns='pollutant_name', 
            values='concentration'
        )
        
        if pollutant_matrix.shape[1] > 1:
            corr_matrix = pollutant_matrix.corr()
            results['pollutant_correlations'] = {}
            
            for i, pol1 in enumerate(corr_matrix.columns):
                for j, pol2 in enumerate(corr_matrix.columns):
                    if i < j:  # Avoid duplicates
                        corr_coef = corr_matrix.loc[pol1, pol2]
                        if not np.isnan(corr_coef):
                            # Calculate p-value
                            data1 = pollutant_matrix[pol1].dropna()
                            data2 = pollutant_matrix[pol2].dropna()
                            common_idx = data1.index.intersection(data2.index)
                            
                            if len(common_idx) > 2:
                                _, p_value = pearsonr(data1[common_idx], data2[common_idx])
                                
                                results['pollutant_correlations'][f'{pol1}_vs_{pol2}'] = {
                                    'correlation_coefficient': float(corr_coef),
                                    'p_value': float(p_value),
                                    'n_observations': len(common_idx),
                                    'significant': p_value < 0.05,
                                    'strength': self._interpret_correlation_strength(abs(corr_coef))
                                }
        
        # Correlation with environmental factors
        env_factors = ['temperature', 'humidity', 'pressure', 'wind_speed']
        results['environmental_correlations'] = {}
        
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            results['environmental_correlations'][pollutant] = {}
            
            for factor in env_factors:
                if factor in pollutant_data.columns:
                    factor_data = pollutant_data[[factor, 'concentration']].dropna()
                    
                    if len(factor_data) > 2:
                        corr_coef, p_value = pearsonr(factor_data[factor], factor_data['concentration'])
                        
                        results['environmental_correlations'][pollutant][factor] = {
                            'correlation_coefficient': float(corr_coef),
                            'p_value': float(p_value),
                            'n_observations': len(factor_data),
                            'significant': p_value < 0.05,
                            'strength': self._interpret_correlation_strength(abs(corr_coef))
                        }
        
        return results
    
    def trend_analysis(self, filters=None, time_period='monthly'):
        """Perform temporal trend analysis"""
        queryset = self.get_data_for_analysis(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for trend analysis'}
        
        results = {}
        
        # Group by time period
        df['date'] = pd.to_datetime(df['measurement_date'])
        
        if time_period == 'daily':
            df['period'] = df['date'].dt.date
        elif time_period == 'weekly':
            df['period'] = df['date'].dt.to_period('W')
        elif time_period == 'monthly':
            df['period'] = df['date'].dt.to_period('M')
        elif time_period == 'quarterly':
            df['period'] = df['date'].dt.to_period('Q')
        else:
            df['period'] = df['date'].dt.to_period('Y')
        
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            
            # Calculate mean concentration per period
            trend_data = pollutant_data.groupby('period')['concentration'].agg([
                'mean', 'std', 'count'
            ]).reset_index()
            
            if len(trend_data) < 3:
                continue
            
            # Convert period to numeric for regression
            trend_data['period_numeric'] = range(len(trend_data))
            
            # Linear regression for trend
            X = trend_data[['period_numeric']]
            y = trend_data['mean']
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate R-squared and p-value
            y_pred = model.predict(X)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Statistical significance of trend
            slope = model.coef_[0]
            n = len(trend_data)
            
            # Calculate t-statistic for slope
            if n > 2:
                mse = ss_res / (n - 2)
                se_slope = np.sqrt(mse / np.sum((trend_data['period_numeric'] - np.mean(trend_data['period_numeric'])) ** 2))
                t_stat = slope / se_slope if se_slope > 0 else 0
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
            else:
                t_stat = 0
                p_value = 1
            
            results[pollutant] = {
                'time_period': time_period,
                'n_periods': len(trend_data),
                'slope': float(slope),
                'intercept': float(model.intercept_),
                'r_squared': float(r_squared),
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant_trend': p_value < 0.05,
                'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                'trend_data': [
                    {
                        'period': str(row['period']),
                        'mean_concentration': float(row['mean']),
                        'std_concentration': float(row['std']) if not pd.isna(row['std']) else 0,
                        'n_observations': int(row['count'])
                    }
                    for _, row in trend_data.iterrows()
                ],
                'interpretation': self._interpret_trend(slope, p_value, r_squared)
            }
        
        return results
    
    def compliance_analysis(self, filters=None):
        """Analyze compliance with regulatory standards"""
        queryset = self.get_data_for_analysis(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for compliance analysis'}
        
        results = {}
        standards = ['who_standard', 'nesrea_standard', 'epa_standard']
        
        for pollutant in df['pollutant_name'].unique():
            pollutant_data = df[df['pollutant_name'] == pollutant]
            results[pollutant] = {}
            
            for standard in standards:
                if pollutant_data[standard].notna().any():
                    standard_value = pollutant_data[standard].iloc[0]
                    concentrations = pollutant_data['concentration']
                    
                    exceedances = concentrations > standard_value
                    n_exceedances = exceedances.sum()
                    exceedance_rate = (n_exceedances / len(concentrations)) * 100
                    
                    # Calculate exceedance statistics
                    if n_exceedances > 0:
                        exceedance_values = concentrations[exceedances]
                        max_exceedance = exceedance_values.max()
                        mean_exceedance = exceedance_values.mean()
                        exceedance_factor = max_exceedance / standard_value
                    else:
                        max_exceedance = 0
                        mean_exceedance = 0
                        exceedance_factor = 0
                    
                    results[pollutant][standard.replace('_standard', '')] = {
                        'standard_value': float(standard_value),
                        'total_measurements': len(concentrations),
                        'exceedances': int(n_exceedances),
                        'exceedance_rate_percent': float(exceedance_rate),
                        'max_concentration': float(concentrations.max()),
                        'max_exceedance': float(max_exceedance),
                        'mean_exceedance': float(mean_exceedance),
                        'exceedance_factor': float(exceedance_factor),
                        'compliance_status': 'Non-compliant' if n_exceedances > 0 else 'Compliant'
                    }
        
        return results
    
    def multivariate_analysis(self, filters=None):
        """Perform multivariate analysis including PCA and clustering"""
        queryset = self.get_data_for_analysis(filters)
        df = self.prepare_dataframe(queryset)
        
        if df.empty:
            return {'error': 'No data available for multivariate analysis'}
        
        results = {}
        
        # Prepare data matrix
        pollutant_matrix = df.pivot_table(
            index=['location_name', 'measurement_date'], 
            columns='pollutant_name', 
            values='concentration'
        ).fillna(0)
        
        if pollutant_matrix.shape[1] < 2:
            return {'error': 'Need at least 2 pollutants for multivariate analysis'}
        
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(pollutant_matrix)
        
        # Principal Component Analysis
        pca = PCA()
        pca_result = pca.fit_transform(scaled_data)
        
        results['pca'] = {
            'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
            'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
            'components': pca.components_.tolist(),
            'feature_names': pollutant_matrix.columns.tolist(),
            'n_components_95_variance': int(np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.95)) + 1
        }
        
        # K-means clustering
        optimal_k = self._find_optimal_clusters(scaled_data)
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        results['clustering'] = {
            'optimal_k': optimal_k,
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'cluster_labels': cluster_labels.tolist(),
            'inertia': float(kmeans.inertia_)
        }
        
        return results
    
    def _interpret_t_test(self, p_value, cohens_d, mean1, mean2):
        """Interpret t-test results"""
        significance = "significant" if p_value < 0.05 else "not significant"
        
        if abs(cohens_d) < 0.2:
            effect_size = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_size = "small"
        elif abs(cohens_d) < 0.8:
            effect_size = "medium"
        else:
            effect_size = "large"
        
        direction = "higher" if mean1 > mean2 else "lower"
        
        return f"The difference is {significance} (p={p_value:.4f}) with a {effect_size} effect size (d={cohens_d:.3f}). Group 1 has {direction} concentrations than Group 2."
    
    def _interpret_anova(self, p_value, eta_squared, n_groups):
        """Interpret ANOVA results"""
        significance = "significant" if p_value < 0.05 else "not significant"
        
        if eta_squared < 0.01:
            effect_size = "negligible"
        elif eta_squared < 0.06:
            effect_size = "small"
        elif eta_squared < 0.14:
            effect_size = "medium"
        else:
            effect_size = "large"
        
        return f"The difference between {n_groups} groups is {significance} (p={p_value:.4f}) with a {effect_size} effect size (η²={eta_squared:.3f})."
    
    def _interpret_correlation_strength(self, r):
        """Interpret correlation strength"""
        if r < 0.1:
            return "negligible"
        elif r < 0.3:
            return "weak"
        elif r < 0.5:
            return "moderate"
        elif r < 0.7:
            return "strong"
        else:
            return "very strong"
    
    def _interpret_trend(self, slope, p_value, r_squared):
        """Interpret trend analysis results"""
        significance = "significant" if p_value < 0.05 else "not significant"
        direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        
        if r_squared < 0.25:
            fit_quality = "poor"
        elif r_squared < 0.5:
            fit_quality = "moderate"
        elif r_squared < 0.75:
            fit_quality = "good"
        else:
            fit_quality = "excellent"
        
        return f"There is a {significance} {direction} trend (p={p_value:.4f}) with {fit_quality} model fit (R²={r_squared:.3f})."
    
    def _tukey_hsd_analysis(self, groups, group_names):
        """Perform Tukey HSD post-hoc analysis"""
        from scipy.stats import tukey_hsd
        
        try:
            result = tukey_hsd(*groups)
            
            post_hoc_results = []
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    post_hoc_results.append({
                        'group1': group_names[i],
                        'group2': group_names[j],
                        'p_value': float(result.pvalue[i, j]),
                        'significant': result.pvalue[i, j] < 0.05
                    })
            
            return post_hoc_results
        except:
            return []
    
    def _find_optimal_clusters(self, data, max_k=10):
        """Find optimal number of clusters using elbow method"""
        if len(data) < 4:
            return 2
        
        max_k = min(max_k, len(data) - 1)
        inertias = []
        
        for k in range(1, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(data)
            inertias.append(kmeans.inertia_)
        
        # Find elbow point
        if len(inertias) < 3:
            return 2
        
        # Calculate rate of change
        rates = []
        for i in range(1, len(inertias) - 1):
            rate = (inertias[i-1] - inertias[i]) / (inertias[i] - inertias[i+1])
            rates.append(rate)
        
        # Find the point where rate of change is maximum
        optimal_k = rates.index(max(rates)) + 2 if rates else 2
        return min(optimal_k, max_k)


class StatisticalReportGenerator:
    """Generate comprehensive statistical reports"""
    
    def __init__(self, analyzer_results):
        self.results = analyzer_results
    
    def generate_summary_report(self):
        """Generate a summary statistical report"""
        report = {
            'title': 'Environmental Data Statistical Analysis Report',
            'generated_at': datetime.now().isoformat(),
            'sections': []
        }
        
        # Add sections based on available results
        if 'descriptive' in self.results:
            report['sections'].append(self._descriptive_section())
        
        if 't_test' in self.results:
            report['sections'].append(self._t_test_section())
        
        if 'anova' in self.results:
            report['sections'].append(self._anova_section())
        
        if 'correlation' in self.results:
            report['sections'].append(self._correlation_section())
        
        if 'trend' in self.results:
            report['sections'].append(self._trend_section())
        
        if 'compliance' in self.results:
            report['sections'].append(self._compliance_section())
        
        return report
    
    def _descriptive_section(self):
        """Generate descriptive statistics section"""
        data = self.results['descriptive']
        
        return {
            'title': 'Descriptive Statistics',
            'summary': f"Analysis of {data['overall']['total_readings']} readings across {data['overall']['unique_locations']} locations and {data['overall']['unique_pollutants']} pollutants.",
            'content': data
        }
    
    def _t_test_section(self):
        """Generate t-test results section"""
        data = self.results['t_test']
        
        significant_results = [k for k, v in data.items() if isinstance(v, dict) and v.get('significant', False)]
        
        return {
            'title': 'T-Test Analysis',
            'summary': f"Compared two groups across {len(data)} pollutants. {len(significant_results)} pollutants showed significant differences.",
            'content': data,
            'significant_pollutants': significant_results
        }
    
    def _anova_section(self):
        """Generate ANOVA results section"""
        data = self.results['anova']
        
        significant_results = [k for k, v in data.items() if isinstance(v, dict) and v.get('significant', False)]
        
        return {
            'title': 'ANOVA Analysis',
            'summary': f"Compared multiple groups across {len(data)} pollutants. {len(significant_results)} pollutants showed significant differences between groups.",
            'content': data,
            'significant_pollutants': significant_results
        }
    
    def _correlation_section(self):
        """Generate correlation analysis section"""
        data = self.results['correlation']
        
        return {
            'title': 'Correlation Analysis',
            'summary': 'Analysis of relationships between pollutants and environmental factors.',
            'content': data
        }
    
    def _trend_section(self):
        """Generate trend analysis section"""
        data = self.results['trend']
        
        significant_trends = [k for k, v in data.items() if isinstance(v, dict) and v.get('significant_trend', False)]
        
        return {
            'title': 'Temporal Trend Analysis',
            'summary': f"Analyzed temporal trends for {len(data)} pollutants. {len(significant_trends)} pollutants showed significant trends over time.",
            'content': data,
            'significant_trends': significant_trends
        }
    
    def _compliance_section(self):
        """Generate compliance analysis section"""
        data = self.results['compliance']
        
        return {
            'title': 'Regulatory Compliance Analysis',
            'summary': 'Analysis of compliance with WHO, NESREA, and EPA standards.',
            'content': data
        }