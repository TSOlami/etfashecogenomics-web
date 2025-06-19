"""
Initial migration for dashboard app.

This migration creates all the necessary tables for the EcoGenomics Suite:
1. DataUploadLog - Track file upload activities
2. EnvironmentalData - Store environmental monitoring data
3. GenomicSample - Store genomic sample information
4. BiodiversityRecord - Store biodiversity assessment records
5. AnalysisResult - Store analysis results
6. Report - Store generated reports
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataUploadLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_size', models.PositiveIntegerField()),
                ('upload_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('processing_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('validation_error', 'Validation Error')], default='pending', max_length=16)),
                ('processing_started', models.DateTimeField(blank=True, null=True)),
                ('processing_completed', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('records_processed', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Data Upload Log',
                'verbose_name_plural': 'Data Upload Logs',
                'ordering': ['-upload_timestamp'],
            },
        ),
        migrations.CreateModel(
            name='EnvironmentalData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('ozone_concentration', models.FloatField(blank=True, help_text='Ozone concentration in µg/m³', null=True)),
                ('carbon_monoxide', models.FloatField(blank=True, help_text='CO concentration in mg/m³', null=True)),
                ('nitrogen_dioxide', models.FloatField(blank=True, help_text='NO2 concentration in µg/m³', null=True)),
                ('sulfur_dioxide', models.FloatField(blank=True, help_text='SO2 concentration in µg/m³', null=True)),
                ('total_voc', models.FloatField(blank=True, help_text='Total VOCs in µg/m³', null=True)),
                ('pm25', models.FloatField(blank=True, help_text='PM2.5 concentration in µg/m³', null=True)),
                ('pm10', models.FloatField(blank=True, help_text='PM10 concentration in µg/m³', null=True)),
                ('temperature', models.FloatField(blank=True, help_text='Temperature in Celsius', null=True)),
                ('humidity', models.FloatField(blank=True, help_text='Humidity percentage', null=True)),
                ('ph_level', models.FloatField(blank=True, help_text='pH level', null=True)),
                ('oxygen_level', models.FloatField(blank=True, help_text='Dissolved oxygen in mg/L', null=True)),
                ('turbidity', models.FloatField(blank=True, help_text='Turbidity in NTU', null=True)),
                ('conductivity', models.FloatField(blank=True, help_text='Electrical conductivity in μS/cm', null=True)),
                ('lead_concentration', models.FloatField(blank=True, help_text='Lead concentration in mg/kg', null=True)),
                ('chromium_concentration', models.FloatField(blank=True, help_text='Chromium concentration in mg/kg', null=True)),
                ('cadmium_concentration', models.FloatField(blank=True, help_text='Cadmium concentration in mg/kg', null=True)),
                ('mercury_concentration', models.FloatField(blank=True, help_text='Mercury concentration in mg/kg', null=True)),
                ('arsenic_concentration', models.FloatField(blank=True, help_text='Arsenic concentration in mg/kg', null=True)),
                ('latitude', models.FloatField(blank=True, help_text='GPS Latitude', null=True)),
                ('longitude', models.FloatField(blank=True, help_text='GPS Longitude', null=True)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Environmental Data',
                'verbose_name_plural': 'Environmental Data',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='GenomicSample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_id', models.CharField(max_length=100, unique=True)),
                ('sample_type', models.CharField(choices=[('leaf', 'Leaf Sample'), ('soil', 'Soil Sample'), ('water', 'Water Sample'), ('air', 'Air Sample'), ('root', 'Root Sample'), ('stem', 'Stem Sample'), ('other', 'Other')], max_length=20)),
                ('collection_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('location', models.CharField(max_length=255)),
                ('latitude', models.FloatField(blank=True, help_text='GPS Latitude', null=True)),
                ('longitude', models.FloatField(blank=True, help_text='GPS Longitude', null=True)),
                ('distance_from_source', models.FloatField(blank=True, help_text='Distance from pollution source in meters', null=True)),
                ('dna_concentration', models.FloatField(blank=True, help_text='DNA concentration in ng/µL', null=True)),
                ('dna_purity_260_280', models.FloatField(blank=True, help_text='260/280 ratio for purity', null=True)),
                ('dna_purity_260_230', models.FloatField(blank=True, help_text='260/230 ratio for purity', null=True)),
                ('target_genes', models.TextField(blank=True, help_text='Target genes analyzed (JSON format)')),
                ('gene_sequences', models.TextField(blank=True, help_text='Gene sequences (JSON format)')),
                ('mutations_detected', models.TextField(blank=True, help_text='Detected mutations (JSON format)')),
                ('analysis_status', models.CharField(choices=[('collected', 'Sample Collected'), ('dna_extracted', 'DNA Extracted'), ('pcr_amplified', 'PCR Amplified'), ('sequenced', 'Sequenced'), ('analyzed', 'Analysis Complete'), ('failed', 'Analysis Failed')], default='collected', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Genomic Sample',
                'verbose_name_plural': 'Genomic Samples',
                'ordering': ['-collection_date'],
            },
        ),
        migrations.CreateModel(
            name='BiodiversityRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('species_name', models.CharField(max_length=255)),
                ('common_name', models.CharField(blank=True, max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('observation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('population_count', models.PositiveIntegerField(blank=True, null=True)),
                ('conservation_status', models.CharField(choices=[('LC', 'Least Concern'), ('NT', 'Near Threatened'), ('VU', 'Vulnerable'), ('EN', 'Endangered'), ('CR', 'Critically Endangered'), ('EW', 'Extinct in the Wild'), ('EX', 'Extinct'), ('DD', 'Data Deficient'), ('NE', 'Not Evaluated')], default='NE', max_length=2)),
                ('latitude', models.FloatField(blank=True, help_text='GPS Latitude', null=True)),
                ('longitude', models.FloatField(blank=True, help_text='GPS Longitude', null=True)),
                ('habitat_description', models.TextField(blank=True)),
                ('threat_assessment', models.TextField(blank=True)),
                ('observer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Biodiversity Record',
                'verbose_name_plural': 'Biodiversity Records',
                'ordering': ['-observation_date'],
            },
        ),
        migrations.CreateModel(
            name='AnalysisResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_type', models.CharField(choices=[('descriptive', 'Descriptive Statistics'), ('ttest', 'T-Test'), ('anova', 'ANOVA'), ('correlation', 'Correlation Analysis'), ('regression', 'Regression Analysis'), ('pollution_assessment', 'Pollution Assessment'), ('gene_alignment', 'Gene Alignment'), ('protein_structure', 'Protein Structure Prediction')], max_length=50)),
                ('dataset_type', models.CharField(max_length=50)),
                ('parameters', models.TextField(help_text='Analysis parameters (JSON format)')),
                ('results', models.TextField(help_text='Analysis results (JSON format)')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('report_type', models.CharField(choices=[('environmental', 'Environmental Assessment'), ('genomic', 'Genomic Analysis'), ('biodiversity', 'Biodiversity Assessment'), ('comprehensive', 'Comprehensive Report'), ('publication', 'Publication Ready')], max_length=50)),
                ('output_format', models.CharField(choices=[('pdf', 'PDF'), ('html', 'HTML'), ('docx', 'Word Document'), ('xlsx', 'Excel Spreadsheet')], max_length=10)),
                ('content', models.TextField(help_text='Report content')),
                ('file_path', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]