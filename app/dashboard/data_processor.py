import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Location, PollutantType, EnvironmentalReading, 
    SampleBatch, BatchReading, DataUploadLog
)
import logging
import uuid
import re

logger = logging.getLogger('dashboard')


class DataProcessor:
    """Class to handle processing of uploaded environmental data files"""
    
    def __init__(self, user, upload_log=None):
        self.user = user
        self.upload_log = upload_log
        self.errors = []
        self.warnings = []
        self.processed_count = 0
        self.successful_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
    def process_file(self, file_path, batch_data, options=None):
        """Main method to process uploaded data file"""
        options = options or {}
        
        try:
            # Read the file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            logger.info(f"Processing file with {len(df)} rows")
            
            # Validate and clean the dataframe
            df_clean = self.validate_and_clean_dataframe(df)
            
            # Create sample batch
            batch = self.create_sample_batch(batch_data)
            
            # Process each row
            readings = []
            for index, row in df_clean.iterrows():
                try:
                    reading = self.process_row(row, batch, options)
                    if reading:
                        readings.append(reading)
                        self.successful_count += 1
                    else:
                        self.skipped_count += 1
                except Exception as e:
                    self.failed_count += 1
                    error_msg = f"Row {index + 2}: {str(e)}"
                    self.errors.append(error_msg)
                    logger.error(error_msg)
                    
                    if not options.get('skip_invalid_rows', True):
                        raise
                
                self.processed_count += 1
            
            # Bulk create readings for better performance
            if readings:
                created_readings = EnvironmentalReading.objects.bulk_create(readings)
                
                # Create batch-reading relationships
                batch_readings = [
                    BatchReading(batch=batch, reading=reading)
                    for reading in created_readings
                ]
                BatchReading.objects.bulk_create(batch_readings)
            
            # Update upload log
            if self.upload_log:
                self.update_upload_log(batch)
            
            logger.info(f"Processing completed: {self.successful_count} successful, {self.failed_count} failed")
            
            return {
                'success': True,
                'batch': batch,
                'processed': self.processed_count,
                'successful': self.successful_count,
                'failed': self.failed_count,
                'skipped': self.skipped_count,
                'errors': self.errors,
                'warnings': self.warnings
            }
            
        except Exception as e:
            logger.error(f"File processing failed: {str(e)}")
            if self.upload_log:
                self.upload_log.processing_status = 'failed'
                self.upload_log.error_log = str(e)
                self.upload_log.save()
            
            return {
                'success': False,
                'error': str(e),
                'errors': self.errors,
                'warnings': self.warnings
            }
    
    def validate_and_clean_dataframe(self, df):
        """Validate and clean the input dataframe"""
        logger.info("Validating and cleaning dataframe")
        
        # Convert column names to lowercase and remove spaces
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        # Required columns mapping (flexible column name matching)
        required_mappings = {
            'location': ['location', 'site', 'location_name', 'site_name'],
            'pollutant': ['pollutant', 'parameter', 'pollutant_name', 'parameter_name'],
            'concentration': ['concentration', 'value', 'result', 'measurement'],
            'date': ['date', 'sampling_date', 'measurement_date', 'datetime'],
        }
        
        # Map columns to standard names
        column_mapping = {}
        for standard_name, possible_names in required_mappings.items():
            for col in df.columns:
                if any(name in col for name in possible_names):
                    column_mapping[col] = standard_name
                    break
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Check for required columns
        required_cols = ['location', 'pollutant', 'concentration', 'date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Remove rows with missing critical data
        initial_count = len(df)
        df = df.dropna(subset=required_cols)
        dropped_count = initial_count - len(df)
        
        if dropped_count > 0:
            self.warnings.append(f"Dropped {dropped_count} rows with missing critical data")
        
        # Clean and validate data types
        df = self.clean_data_types(df)
        
        return df
    
    def clean_data_types(self, df):
        """Clean and validate data types"""
        
        # Clean concentration values
        df['concentration'] = df['concentration'].apply(self.clean_numeric_value)
        
        # Clean date values
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Remove rows with invalid dates or concentrations
        initial_count = len(df)
        df = df.dropna(subset=['date', 'concentration'])
        dropped_count = initial_count - len(df)
        
        if dropped_count > 0:
            self.warnings.append(f"Dropped {dropped_count} rows with invalid dates or concentrations")
        
        return df
    
    def clean_numeric_value(self, value):
        """Clean numeric values, handling various formats"""
        if pd.isna(value):
            return None
        
        # Convert to string and clean
        str_value = str(value).strip()
        
        # Handle common patterns
        str_value = re.sub(r'[<>≤≥]', '', str_value)  # Remove comparison operators
        str_value = re.sub(r'[^\d.-]', '', str_value)  # Keep only digits, dots, and minus
        
        try:
            return float(str_value) if str_value else None
        except ValueError:
            return None
    
    def create_sample_batch(self, batch_data):
        """Create a new sample batch"""
        batch = SampleBatch.objects.create(
            name=batch_data['batch_name'],
            description=batch_data.get('batch_description', ''),
            sampling_date=batch_data['sampling_date'],
            project_name=batch_data.get('project_name', ''),
            project_code=batch_data.get('project_code', ''),
            study_type=batch_data.get('study_type', 'monitoring'),
            created_by=self.user
        )
        logger.info(f"Created sample batch: {batch.name}")
        return batch
    
    def process_row(self, row, batch, options):
        """Process a single row of data"""
        
        # Get or create location
        location = self.get_or_create_location(
            row['location'], 
            row.get('latitude'), 
            row.get('longitude'),
            options.get('create_missing_locations', True)
        )
        
        if not location:
            raise ValueError(f"Location '{row['location']}' not found and auto-creation disabled")
        
        # Get pollutant type
        pollutant_type = self.get_pollutant_type(row['pollutant'])
        if not pollutant_type:
            raise ValueError(f"Pollutant type '{row['pollutant']}' not found")
        
        # Validate concentration
        concentration = self.validate_concentration(row['concentration'])
        if concentration is None:
            raise ValueError("Invalid concentration value")
        
        # Create environmental reading
        reading = EnvironmentalReading(
            location=location,
            pollutant_type=pollutant_type,
            concentration=Decimal(str(concentration)),
            measurement_date=timezone.make_aware(row['date'].to_pydatetime()),
            created_by=self.user
        )
        
        # Add optional fields if present
        optional_fields = {
            'temperature': 'temperature',
            'humidity': 'humidity', 
            'pressure': 'pressure',
            'wind_speed': 'wind_speed',
            'wind_direction': 'wind_direction',
            'sampling_method': 'sampling_method',
            'equipment_used': 'equipment_used',
            'operator': 'operator',
            'notes': 'notes',
            'quality_flag': 'quality_flag'
        }
        
        for csv_field, model_field in optional_fields.items():
            if csv_field in row and pd.notna(row[csv_field]):
                value = row[csv_field]
                if csv_field in ['temperature', 'humidity', 'pressure', 'wind_speed', 'wind_direction']:
                    value = self.clean_numeric_value(value)
                    if value is not None:
                        setattr(reading, model_field, Decimal(str(value)))
                else:
                    setattr(reading, model_field, str(value))
        
        return reading
    
    def get_or_create_location(self, location_name, latitude=None, longitude=None, create_if_missing=True):
        """Get existing location or create new one"""
        
        # Try to find existing location by name
        try:
            location = Location.objects.get(
                name__iexact=location_name.strip(),
                created_by=self.user
            )
            return location
        except Location.DoesNotExist:
            pass
        
        # If coordinates provided, try to find by coordinates
        if latitude and longitude:
            try:
                lat_decimal = Decimal(str(latitude))
                lon_decimal = Decimal(str(longitude))
                location = Location.objects.get(
                    latitude=lat_decimal,
                    longitude=lon_decimal,
                    created_by=self.user
                )
                return location
            except (Location.DoesNotExist, InvalidOperation):
                pass
        
        # Create new location if allowed
        if create_if_missing:
            location_data = {
                'name': location_name.strip(),
                'created_by': self.user
            }
            
            if latitude and longitude:
                try:
                    location_data['latitude'] = Decimal(str(latitude))
                    location_data['longitude'] = Decimal(str(longitude))
                except InvalidOperation:
                    self.warnings.append(f"Invalid coordinates for location '{location_name}'")
            
            location = Location.objects.create(**location_data)
            logger.info(f"Created new location: {location.name}")
            return location
        
        return None
    
    def get_pollutant_type(self, pollutant_name):
        """Get pollutant type by name (flexible matching)"""
        pollutant_name = pollutant_name.strip()
        
        # Try exact match first
        try:
            return PollutantType.objects.get(name__iexact=pollutant_name, is_active=True)
        except PollutantType.DoesNotExist:
            pass
        
        # Try partial match
        try:
            return PollutantType.objects.filter(
                name__icontains=pollutant_name, 
                is_active=True
            ).first()
        except PollutantType.DoesNotExist:
            pass
        
        # Try matching by chemical formula
        try:
            return PollutantType.objects.get(
                chemical_formula__iexact=pollutant_name, 
                is_active=True
            )
        except PollutantType.DoesNotExist:
            pass
        
        return None
    
    def validate_concentration(self, concentration):
        """Validate concentration value"""
        if pd.isna(concentration):
            return None
        
        try:
            value = float(concentration)
            if value < 0:
                raise ValueError("Concentration cannot be negative")
            return value
        except (ValueError, TypeError):
            return None
    
    def update_upload_log(self, batch):
        """Update the upload log with processing results"""
        if not self.upload_log:
            return
        
        self.upload_log.records_processed = self.processed_count
        self.upload_log.records_successful = self.successful_count
        self.upload_log.records_failed = self.failed_count
        self.upload_log.records_skipped = self.skipped_count
        self.upload_log.batch = batch
        self.upload_log.processing_end = timezone.now()
        
        if self.failed_count > 0:
            self.upload_log.processing_status = 'completed_with_errors'
        else:
            self.upload_log.processing_status = 'completed'
        
        if self.errors:
            self.upload_log.error_log = '\n'.join(self.errors)
        
        if self.warnings:
            self.upload_log.warning_log = '\n'.join(self.warnings)
        
        self.upload_log.save()
        logger.info(f"Updated upload log: {self.upload_log.id}")


def preview_data_file(file_path, max_rows=10):
    """Preview data file contents for user confirmation"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=max_rows)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path, nrows=max_rows)
        else:
            raise ValueError("Unsupported file format")
        
        # Basic info about the file
        info = {
            'columns': list(df.columns),
            'row_count': len(df),
            'sample_data': df.to_dict('records'),
            'data_types': df.dtypes.to_dict()
        }
        
        return {'success': True, 'data': info}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}