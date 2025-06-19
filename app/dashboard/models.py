from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class DataUploadLog(models.Model):
    """Model to track data upload activities"""
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('validation_error', 'Validation Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # in bytes
    upload_timestamp = models.DateTimeField(default=timezone.now)
    processing_status = models.CharField(
        max_length=max(len(v[0]) for v in PROCESSING_STATUS_CHOICES),
        choices=PROCESSING_STATUS_CHOICES,
        default='pending'
    )
    processing_started = models.DateTimeField(null=True, blank=True)
    processing_completed = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    records_processed = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-upload_timestamp']
        verbose_name = 'Data Upload Log'
        verbose_name_plural = 'Data Upload Logs'
    
    def __str__(self):
        return f"{self.file_name} - {self.get_processing_status_display()}"
    
    @property
    def processing_duration(self):
        """Calculate processing duration if both start and end times are available"""
        if self.processing_started and self.processing_completed:
            return self.processing_completed - self.processing_started
        return None


class EnvironmentalData(models.Model):
    """Model to store environmental monitoring data"""
    
    timestamp = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255, blank=True)
    
    # Air Quality Parameters
    ozone_concentration = models.FloatField(null=True, blank=True, help_text="Ozone concentration in µg/m³")
    carbon_monoxide = models.FloatField(null=True, blank=True, help_text="CO concentration in mg/m³")
    nitrogen_dioxide = models.FloatField(null=True, blank=True, help_text="NO2 concentration in µg/m³")
    sulfur_dioxide = models.FloatField(null=True, blank=True, help_text="SO2 concentration in µg/m³")
    total_voc = models.FloatField(null=True, blank=True, help_text="Total VOCs in µg/m³")
    pm25 = models.FloatField(null=True, blank=True, help_text="PM2.5 concentration in µg/m³")
    pm10 = models.FloatField(null=True, blank=True, help_text="PM10 concentration in µg/m³")
    
    # Basic Environmental Parameters
    temperature = models.FloatField(null=True, blank=True, help_text="Temperature in Celsius")
    humidity = models.FloatField(null=True, blank=True, help_text="Humidity percentage")
    ph_level = models.FloatField(null=True, blank=True, help_text="pH level")
    oxygen_level = models.FloatField(null=True, blank=True, help_text="Dissolved oxygen in mg/L")
    turbidity = models.FloatField(null=True, blank=True, help_text="Turbidity in NTU")
    conductivity = models.FloatField(null=True, blank=True, help_text="Electrical conductivity in μS/cm")
    
    # Heavy Metals (from soil/plant samples)
    lead_concentration = models.FloatField(null=True, blank=True, help_text="Lead concentration in mg/kg")
    chromium_concentration = models.FloatField(null=True, blank=True, help_text="Chromium concentration in mg/kg")
    cadmium_concentration = models.FloatField(null=True, blank=True, help_text="Cadmium concentration in mg/kg")
    mercury_concentration = models.FloatField(null=True, blank=True, help_text="Mercury concentration in mg/kg")
    arsenic_concentration = models.FloatField(null=True, blank=True, help_text="Arsenic concentration in mg/kg")
    
    # Georeferencing
    latitude = models.FloatField(null=True, blank=True, help_text="GPS Latitude")
    longitude = models.FloatField(null=True, blank=True, help_text="GPS Longitude")
    
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Environmental Data'
        verbose_name_plural = 'Environmental Data'
    
    def __str__(self):
        return f"Environmental Data - {self.location} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def get_air_quality_index(self):
        """Calculate Air Quality Index based on pollutant concentrations"""
        # Simplified AQI calculation - can be enhanced with proper formulas
        pollutants = []
        if self.pm25: pollutants.append(self.pm25 / 25 * 100)  # WHO guideline: 25 µg/m³
        if self.pm10: pollutants.append(self.pm10 / 50 * 100)  # WHO guideline: 50 µg/m³
        if self.ozone_concentration: pollutants.append(self.ozone_concentration / 100 * 100)
        if self.nitrogen_dioxide: pollutants.append(self.nitrogen_dioxide / 40 * 100)
        
        return max(pollutants) if pollutants else 0
    
    def check_pollution_standards(self):
        """Check against WHO/NESREA standards"""
        violations = []
        
        # WHO Air Quality Guidelines
        if self.pm25 and self.pm25 > 25:
            violations.append(f"PM2.5 exceeds WHO guideline: {self.pm25} µg/m³ > 25 µg/m³")
        if self.pm10 and self.pm10 > 50:
            violations.append(f"PM10 exceeds WHO guideline: {self.pm10} µg/m³ > 50 µg/m³")
        if self.nitrogen_dioxide and self.nitrogen_dioxide > 40:
            violations.append(f"NO2 exceeds WHO guideline: {self.nitrogen_dioxide} µg/m³ > 40 µg/m³")
        if self.sulfur_dioxide and self.sulfur_dioxide > 40:
            violations.append(f"SO2 exceeds WHO guideline: {self.sulfur_dioxide} µg/m³ > 40 µg/m³")
        
        # Heavy metal standards (example thresholds)
        if self.lead_concentration and self.lead_concentration > 100:
            violations.append(f"Lead concentration exceeds safe levels: {self.lead_concentration} mg/kg > 100 mg/kg")
        if self.chromium_concentration and self.chromium_concentration > 100:
            violations.append(f"Chromium concentration exceeds safe levels: {self.chromium_concentration} mg/kg > 100 mg/kg")
        
        return violations


class GenomicSample(models.Model):
    """Model to store genomic sample information"""
    
    SAMPLE_TYPE_CHOICES = [
        ('leaf', 'Leaf Sample'),
        ('soil', 'Soil Sample'),
        ('water', 'Water Sample'),
        ('air', 'Air Sample'),
        ('root', 'Root Sample'),
        ('stem', 'Stem Sample'),
        ('other', 'Other'),
    ]
    
    sample_id = models.CharField(max_length=100, unique=True)
    sample_type = models.CharField(max_length=20, choices=SAMPLE_TYPE_CHOICES)
    collection_date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255)
    
    # Georeferencing
    latitude = models.FloatField(null=True, blank=True, help_text="GPS Latitude")
    longitude = models.FloatField(null=True, blank=True, help_text="GPS Longitude")
    distance_from_source = models.FloatField(null=True, blank=True, help_text="Distance from pollution source in meters")
    
    # DNA Analysis Results
    dna_concentration = models.FloatField(null=True, blank=True, help_text="DNA concentration in ng/µL")
    dna_purity_260_280 = models.FloatField(null=True, blank=True, help_text="260/280 ratio for purity")
    dna_purity_260_230 = models.FloatField(null=True, blank=True, help_text="260/230 ratio for purity")
    
    # Gene Analysis
    target_genes = models.TextField(blank=True, help_text="Target genes analyzed (JSON format)")
    gene_sequences = models.TextField(blank=True, help_text="Gene sequences (JSON format)")
    mutations_detected = models.TextField(blank=True, help_text="Detected mutations (JSON format)")
    
    # Analysis Status
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('collected', 'Sample Collected'),
            ('dna_extracted', 'DNA Extracted'),
            ('pcr_amplified', 'PCR Amplified'),
            ('sequenced', 'Sequenced'),
            ('analyzed', 'Analysis Complete'),
            ('failed', 'Analysis Failed'),
        ],
        default='collected'
    )
    
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-collection_date']
        verbose_name = 'Genomic Sample'
        verbose_name_plural = 'Genomic Samples'
    
    def __str__(self):
        return f"Sample {self.sample_id} - {self.get_sample_type_display()}"
    
    def get_target_genes_list(self):
        """Return target genes as a list"""
        try:
            return json.loads(self.target_genes) if self.target_genes else []
        except json.JSONDecodeError:
            return []
    
    def get_mutations_list(self):
        """Return mutations as a list"""
        try:
            return json.loads(self.mutations_detected) if self.mutations_detected else []
        except json.JSONDecodeError:
            return []


class BiodiversityRecord(models.Model):
    """Model to store biodiversity assessment records"""
    
    CONSERVATION_STATUS_CHOICES = [
        ('LC', 'Least Concern'),
        ('NT', 'Near Threatened'),
        ('VU', 'Vulnerable'),
        ('EN', 'Endangered'),
        ('CR', 'Critically Endangered'),
        ('EW', 'Extinct in the Wild'),
        ('EX', 'Extinct'),
        ('DD', 'Data Deficient'),
        ('NE', 'Not Evaluated'),
    ]
    
    species_name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255)
    observation_date = models.DateTimeField(default=timezone.now)
    population_count = models.PositiveIntegerField(null=True, blank=True)
    conservation_status = models.CharField(
        max_length=2,
        choices=CONSERVATION_STATUS_CHOICES,
        default='NE'
    )
    
    # Georeferencing
    latitude = models.FloatField(null=True, blank=True, help_text="GPS Latitude")
    longitude = models.FloatField(null=True, blank=True, help_text="GPS Longitude")
    
    habitat_description = models.TextField(blank=True)
    threat_assessment = models.TextField(blank=True)
    observer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-observation_date']
        verbose_name = 'Biodiversity Record'
        verbose_name_plural = 'Biodiversity Records'
    
    def __str__(self):
        return f"{self.species_name} - {self.location}"


class AnalysisResult(models.Model):
    """Model to store analysis results"""
    
    ANALYSIS_TYPE_CHOICES = [
        ('descriptive', 'Descriptive Statistics'),
        ('ttest', 'T-Test'),
        ('anova', 'ANOVA'),
        ('correlation', 'Correlation Analysis'),
        ('regression', 'Regression Analysis'),
        ('pollution_assessment', 'Pollution Assessment'),
        ('gene_alignment', 'Gene Alignment'),
        ('protein_structure', 'Protein Structure Prediction'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPE_CHOICES)
    dataset_type = models.CharField(max_length=50)  # environmental, genomic, biodiversity
    parameters = models.TextField(help_text="Analysis parameters (JSON format)")
    results = models.TextField(help_text="Analysis results (JSON format)")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_results_dict(self):
        """Return results as a dictionary"""
        try:
            return json.loads(self.results) if self.results else {}
        except json.JSONDecodeError:
            return {}


class Report(models.Model):
    """Model to store generated reports"""
    
    REPORT_TYPE_CHOICES = [
        ('environmental', 'Environmental Assessment'),
        ('genomic', 'Genomic Analysis'),
        ('biodiversity', 'Biodiversity Assessment'),
        ('comprehensive', 'Comprehensive Report'),
        ('publication', 'Publication Ready'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('docx', 'Word Document'),
        ('xlsx', 'Excel Spreadsheet'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    output_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    content = models.TextField(help_text="Report content")
    file_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"