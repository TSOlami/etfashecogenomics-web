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
            ('commercial', 'Commercial Area'),
            ('agricultural', 'Agricultural Area'),
            ('forest', 'Forest/Natural Area'),
            ('urban', 'Urban Area'),
            ('suburban', 'Suburban Area'),
            ('rural', 'Rural Area'),
            ('coastal', 'Coastal Area'),
            ('mining', 'Mining Area'),
            ('landfill', 'Landfill/Waste Site'),
            ('traffic', 'Traffic/Roadside'),
            ('background', 'Background/Remote'),
            ('other', 'Other'),
        ],
        default='other'
    )
    land_use = models.CharField(
        max_length=100,
        blank=True,
        help_text="Detailed land use description"
    )
    distance_to_source = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance to pollution source in meters"
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
    cas_number = models.CharField(max_length=20, blank=True, help_text="Chemical Abstracts Service Registry Number")
    category = models.CharField(
        max_length=50,
        choices=[
            ('criteria_air', 'Criteria Air Pollutant'),
            ('particulate', 'Particulate Matter'),
            ('heavy_metal', 'Heavy Metal'),
            ('voc', 'Volatile Organic Compound'),
            ('pac', 'Polycyclic Aromatic Hydrocarbon'),
            ('pesticide', 'Pesticide/Herbicide'),
            ('nutrient', 'Nutrient'),
            ('physical', 'Physical Parameter'),
            ('biological', 'Biological Parameter'),
            ('radioactive', 'Radioactive Material'),
            ('other', 'Other'),
        ]
    )
    subcategory = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20, help_text="Standard unit of measurement")
    molecular_weight = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Molecular weight in g/mol"
    )
    
    # Regulatory Standards
    who_standard = models.DecimalField(
        max_digits=15, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="WHO guideline value"
    )
    who_averaging_time = models.CharField(
        max_length=50,
        blank=True,
        help_text="WHO averaging time (e.g., 24-hour, annual)"
    )
    nesrea_standard = models.DecimalField(
        max_digits=15, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="NESREA standard value"
    )
    nesrea_averaging_time = models.CharField(
        max_length=50,
        blank=True,
        help_text="NESREA averaging time"
    )
    epa_standard = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="US EPA standard value"
    )
    epa_averaging_time = models.CharField(
        max_length=50,
        blank=True,
        help_text="EPA averaging time"
    )
    eu_standard = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="EU standard value"
    )
    
    # Additional Properties
    description = models.TextField(blank=True)
    health_effects = models.TextField(blank=True)
    environmental_effects = models.TextField(blank=True)
    sources = models.TextField(blank=True, help_text="Common sources of this pollutant")
    sampling_method = models.TextField(blank=True, help_text="Standard sampling methods")
    analytical_method = models.TextField(blank=True, help_text="Standard analytical methods")
    detection_limit = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Typical method detection limit"
    )
    
    is_active = models.BooleanField(default=True)
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
    
    # Measurement Data
    concentration = models.DecimalField(
        max_digits=15, 
        decimal_places=6,
        validators=[MinValueValidator(0)],
        help_text="Measured concentration value"
    )
    measurement_date = models.DateTimeField(help_text="Date and time when measurement was taken")
    sampling_duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Duration of sampling period"
    )
    
    # Quality Control
    quality_flag = models.CharField(
        max_length=20,
        choices=[
            ('valid', 'Valid'),
            ('questionable', 'Questionable'),
            ('invalid', 'Invalid'),
            ('below_detection', 'Below Detection Limit'),
            ('calibration', 'Calibration Check'),
            ('maintenance', 'Maintenance'),
        ],
        default='valid'
    )
    detection_limit = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Detection limit for this measurement"
    )
    uncertainty = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Measurement uncertainty (%)"
    )
    
    # Environmental Conditions
    temperature = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Temperature in Celsius"
    )
    humidity = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Relative humidity percentage"
    )
    pressure = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Atmospheric pressure in hPa"
    )
    wind_speed = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Wind speed in m/s"
    )
    wind_direction = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Wind direction in degrees (0-360)"
    )
    precipitation = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precipitation in mm"
    )
    solar_radiation = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Solar radiation in W/m²"
    )
    
    # Sampling Information
    sampling_method = models.CharField(
        max_length=200,
        blank=True,
        help_text="Sampling method used"
    )
    equipment_used = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Equipment or instrument used"
    )
    equipment_serial = models.CharField(
        max_length=100,
        blank=True,
        help_text="Equipment serial number"
    )
    calibration_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last calibration date of equipment"
    )
    operator = models.CharField(
        max_length=100,
        blank=True,
        help_text="Person who conducted the measurement"
    )
    
    # Additional Data
    sample_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Laboratory sample ID"
    )
    chain_of_custody = models.CharField(
        max_length=100,
        blank=True,
        help_text="Chain of custody number"
    )
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='environmental_readings')

    class Meta:
        ordering = ['-measurement_date']
        indexes = [
            models.Index(fields=['location', 'measurement_date']),
            models.Index(fields=['pollutant_type', 'measurement_date']),
            models.Index(fields=['created_by', 'measurement_date']),
            models.Index(fields=['quality_flag']),
        ]

    def __str__(self):
        return f"{self.pollutant_type.name}: {self.concentration} {self.pollutant_type.unit} at {self.location.name}"

    @property
    def exceeds_who_standard(self):
        """Check if reading exceeds WHO standard"""
        if self.pollutant_type.who_standard and self.quality_flag == 'valid':
            return self.concentration > self.pollutant_type.who_standard
        return None

    @property
    def exceeds_nesrea_standard(self):
        """Check if reading exceeds NESREA standard"""
        if self.pollutant_type.nesrea_standard and self.quality_flag == 'valid':
            return self.concentration > self.pollutant_type.nesrea_standard
        return None

    @property
    def exceeds_epa_standard(self):
        """Check if reading exceeds EPA standard"""
        if self.pollutant_type.epa_standard and self.quality_flag == 'valid':
            return self.concentration > self.pollutant_type.epa_standard
        return None

    @property
    def compliance_status(self):
        """Get overall compliance status"""
        if self.quality_flag != 'valid':
            return 'invalid_data'
            
        standards_exceeded = []
        if self.exceeds_who_standard:
            standards_exceeded.append('WHO')
        if self.exceeds_nesrea_standard:
            standards_exceeded.append('NESREA')
        if self.exceeds_epa_standard:
            standards_exceeded.append('EPA')
            
        if standards_exceeded:
            return f"exceeds_{'+'.join(standards_exceeded)}"
        elif any([self.exceeds_who_standard is False, 
                 self.exceeds_nesrea_standard is False, 
                 self.exceeds_epa_standard is False]):
            return 'within_standards'
        else:
            return 'no_standards_defined'


class SampleBatch(models.Model):
    """Model to group related environmental readings from a sampling session"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Name or identifier for this sampling batch")
    description = models.TextField(blank=True)
    sampling_date = models.DateField(help_text="Date when samples were collected")
    project_name = models.CharField(max_length=200, blank=True)
    project_code = models.CharField(max_length=50, blank=True)
    purpose = models.TextField(blank=True)
    study_type = models.CharField(
        max_length=50,
        choices=[
            ('baseline', 'Baseline Study'),
            ('monitoring', 'Routine Monitoring'),
            ('compliance', 'Compliance Monitoring'),
            ('research', 'Research Study'),
            ('impact_assessment', 'Impact Assessment'),
            ('emergency', 'Emergency Response'),
            ('other', 'Other'),
        ],
        default='monitoring'
    )
    weather_summary = models.TextField(blank=True)
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

    @property
    def pollutants_count(self):
        """Get number of unique pollutants measured in this batch"""
        return self.readings.values('pollutant_type').distinct().count()


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
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_type = models.CharField(
        max_length=20,
        choices=[
            ('csv', 'CSV File'),
            ('xlsx', 'Excel File'),
            ('json', 'JSON File'),
            ('xml', 'XML File'),
            ('other', 'Other'),
        ],
        default='csv'
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_uploads')
    
    # Processing Statistics
    records_processed = models.PositiveIntegerField(default=0)
    records_successful = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    records_skipped = models.PositiveIntegerField(default=0)
    
    processing_status = models.CharField(
        max_length=25,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('completed_with_errors', 'Completed with Errors'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    processing_start = models.DateTimeField(null=True, blank=True)
    processing_end = models.DateTimeField(null=True, blank=True)
    error_log = models.TextField(blank=True)
    warning_log = models.TextField(blank=True)
    
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

    @property
    def processing_duration(self):
        """Calculate processing duration"""
        if self.processing_start and self.processing_end:
            return self.processing_end - self.processing_start
        return None