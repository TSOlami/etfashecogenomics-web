from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Location(models.Model):
    """Model to store sampling locations with geographic coordinates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Descriptive name for the location")
    description = models.TextField(blank=True, help_text="Additional details about the location")
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude in decimal degrees"
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude in decimal degrees"
    )
    elevation = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Elevation in meters above sea level"
    )
    site_type = models.CharField(
        max_length=50,
        choices=[
            ('industrial', 'Industrial Area'),
            ('residential', 'Residential Area'),
            ('agricultural', 'Agricultural Area'),
            ('forest', 'Forest/Natural Area'),
            ('urban', 'Urban Area'),
            ('rural', 'Rural Area'),
            ('coastal', 'Coastal Area'),
            ('other', 'Other'),
        ],
        default='other'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')

    class Meta:
        ordering = ['name']
        unique_together = ['latitude', 'longitude', 'created_by']

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class PollutantType(models.Model):
    """Model to define different types of pollutants and their properties"""
    name = models.CharField(max_length=100, unique=True)
    chemical_formula = models.CharField(max_length=50, blank=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('air_quality', 'Air Quality'),
            ('heavy_metal', 'Heavy Metal'),
            ('organic_compound', 'Organic Compound'),
            ('particulate', 'Particulate Matter'),
            ('gas', 'Gas'),
            ('other', 'Other'),
        ]
    )
    unit = models.CharField(max_length=20, help_text="Standard unit of measurement (e.g., mg/L, ppm, µg/m³)")
    who_standard = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        help_text="WHO guideline value in standard unit"
    )
    nesrea_standard = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        help_text="NESREA standard value in standard unit"
    )
    description = models.TextField(blank=True)
    health_effects = models.TextField(blank=True, help_text="Known health effects of this pollutant")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.unit})"


class EnvironmentalReading(models.Model):
    """Model to store individual environmental measurements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='readings')
    pollutant_type = models.ForeignKey(PollutantType, on_delete=models.CASCADE, related_name='readings')
    concentration = models.DecimalField(
        max_digits=12, 
        decimal_places=6,
        validators=[MinValueValidator(0)],
        help_text="Measured concentration value"
    )
    measurement_date = models.DateTimeField(help_text="Date and time when measurement was taken")
    weather_conditions = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Weather conditions during measurement"
    )
    temperature = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Temperature in Celsius during measurement"
    )
    humidity = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Relative humidity percentage"
    )
    wind_speed = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Wind speed in m/s"
    )
    wind_direction = models.CharField(
        max_length=10, 
        blank=True,
        help_text="Wind direction (N, NE, E, SE, S, SW, W, NW)"
    )
    equipment_used = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Equipment or method used for measurement"
    )
    quality_flag = models.CharField(
        max_length=20,
        choices=[
            ('valid', 'Valid'),
            ('questionable', 'Questionable'),
            ('invalid', 'Invalid'),
            ('calibration', 'Calibration Check'),
        ],
        default='valid'
    )
    notes = models.TextField(blank=True, help_text="Additional notes about the measurement")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='environmental_readings')

    class Meta:
        ordering = ['-measurement_date']
        indexes = [
            models.Index(fields=['location', 'measurement_date']),
            models.Index(fields=['pollutant_type', 'measurement_date']),
            models.Index(fields=['created_by', 'measurement_date']),
        ]

    def __str__(self):
        return f"{self.pollutant_type.name}: {self.concentration} {self.pollutant_type.unit} at {self.location.name}"

    @property
    def exceeds_who_standard(self):
        """Check if reading exceeds WHO standard"""
        if self.pollutant_type.who_standard:
            return self.concentration > self.pollutant_type.who_standard
        return None

    @property
    def exceeds_nesrea_standard(self):
        """Check if reading exceeds NESREA standard"""
        if self.pollutant_type.nesrea_standard:
            return self.concentration > self.pollutant_type.nesrea_standard
        return None

    @property
    def compliance_status(self):
        """Get overall compliance status"""
        who_exceeded = self.exceeds_who_standard
        nesrea_exceeded = self.exceeds_nesrea_standard
        
        if who_exceeded or nesrea_exceeded:
            return 'exceeds_standards'
        elif who_exceeded is False or nesrea_exceeded is False:
            return 'within_standards'
        else:
            return 'no_standards_defined'


class SampleBatch(models.Model):
    """Model to group related environmental readings from a sampling session"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Name or identifier for this sampling batch")
    description = models.TextField(blank=True)
    sampling_date = models.DateField(help_text="Date when samples were collected")
    project_name = models.CharField(max_length=200, blank=True, help_text="Associated research project")
    purpose = models.TextField(blank=True, help_text="Purpose or objective of this sampling")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sample_batches')

    class Meta:
        ordering = ['-sampling_date']
        verbose_name_plural = "Sample batches"

    def __str__(self):
        return f"{self.name} - {self.sampling_date}"

    @property
    def total_readings(self):
        """Get total number of readings in this batch"""
        return self.readings.count()

    @property
    def locations_count(self):
        """Get number of unique locations in this batch"""
        return self.readings.values('location').distinct().count()


class BatchReading(models.Model):
    """Model to link environmental readings to sample batches"""
    batch = models.ForeignKey(SampleBatch, on_delete=models.CASCADE, related_name='readings')
    reading = models.ForeignKey(EnvironmentalReading, on_delete=models.CASCADE, related_name='batches')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['batch', 'reading']

    def __str__(self):
        return f"{self.batch.name} - {self.reading}"


class DataUploadLog(models.Model):
    """Model to track data upload history"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_uploads')
    records_processed = models.PositiveIntegerField(default=0)
    records_successful = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_log = models.TextField(blank=True, help_text="Error messages from processing")
    batch = models.ForeignKey(
        SampleBatch, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Associated sample batch if created"
    )

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.filename} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def success_rate(self):
        """Calculate success rate of data processing"""
        if self.records_processed > 0:
            return (self.records_successful / self.records_processed) * 100
        return 0