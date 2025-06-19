from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    temperature = models.FloatField(help_text="Temperature in Celsius")
    humidity = models.FloatField(help_text="Humidity percentage")
    ph_level = models.FloatField(help_text="pH level")
    oxygen_level = models.FloatField(help_text="Dissolved oxygen in mg/L")
    turbidity = models.FloatField(help_text="Turbidity in NTU")
    conductivity = models.FloatField(help_text="Electrical conductivity in μS/cm")
    location = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Environmental Data'
        verbose_name_plural = 'Environmental Data'
    
    def __str__(self):
        return f"Environmental Data - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class GenomicSample(models.Model):
    """Model to store genomic sample information"""
    
    SAMPLE_TYPE_CHOICES = [
        ('water', 'Water Sample'),
        ('soil', 'Soil Sample'),
        ('air', 'Air Sample'),
        ('tissue', 'Tissue Sample'),
        ('other', 'Other'),
    ]
    
    sample_id = models.CharField(max_length=100, unique=True)
    sample_type = models.CharField(max_length=20, choices=SAMPLE_TYPE_CHOICES)
    collection_date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255)
    species_identified = models.PositiveIntegerField(default=0)
    genetic_variants = models.PositiveIntegerField(default=0)
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-collection_date']
        verbose_name = 'Genomic Sample'
        verbose_name_plural = 'Genomic Samples'
    
    def __str__(self):
        return f"Sample {self.sample_id} - {self.get_sample_type_display()}"


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
    habitat_description = models.TextField(blank=True)
    threat_assessment = models.TextField(blank=True)
    observer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-observation_date']
        verbose_name = 'Biodiversity Record'
        verbose_name_plural = 'Biodiversity Records'
    
    def __str__(self):
        return f"{self.species_name} - {self.location}"