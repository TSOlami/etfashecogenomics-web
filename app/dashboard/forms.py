from django import forms
from django.core.validators import FileExtensionValidator
from .models import SampleBatch, Location, PollutantType
import pandas as pd
from datetime import datetime


class DataUploadForm(forms.Form):
    """Form for uploading environmental data files"""
    
    # File upload field
    data_file = forms.FileField(
        label="Data File",
        help_text="Upload Excel (.xlsx, .xls) or CSV (.csv) file containing environmental measurements",
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls'])],
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    
    # Batch information
    batch_name = forms.CharField(
        max_length=200,
        help_text="Name or identifier for this sampling batch",
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'e.g., Factory Site Survey - January 2024'
        })
    )
    
    batch_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
            'rows': 3,
            'placeholder': 'Optional description of the sampling campaign...'
        })
    )
    
    project_name = forms.CharField(
        required=False,
        max_length=200,
        help_text="Project or study name",
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'e.g., Cement Factory Impact Assessment'
        })
    )
    
    project_code = forms.CharField(
        required=False,
        max_length=50,
        help_text="Project code or reference number",
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
            'placeholder': 'e.g., ENV-2024-001'
        })
    )
    
    sampling_date = forms.DateField(
        help_text="Date when samples were collected",
        widget=forms.DateInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
            'type': 'date'
        })
    )
    
    study_type = forms.ChoiceField(
        choices=[
            ('baseline', 'Baseline Study'),
            ('monitoring', 'Routine Monitoring'),
            ('compliance', 'Compliance Monitoring'),
            ('research', 'Research Study'),
            ('impact_assessment', 'Impact Assessment'),
            ('emergency', 'Emergency Response'),
            ('other', 'Other'),
        ],
        initial='monitoring',
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500'
        })
    )
    
    # Data processing options
    create_missing_locations = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Automatically create new locations found in the data file",
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded'
        })
    )
    
    skip_invalid_rows = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Skip rows with invalid data instead of stopping the import",
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded'
        })
    )
    
    def clean_data_file(self):
        """Validate the uploaded file"""
        file = self.cleaned_data.get('data_file')
        if not file:
            return file
            
        # Check file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("File size cannot exceed 10MB")
        
        # Try to read the file to validate format
        try:
            if file.name.endswith('.csv'):
                # Try to read first few rows of CSV
                file.seek(0)
                pd.read_csv(file, nrows=5)
            elif file.name.endswith(('.xlsx', '.xls')):
                # Try to read first few rows of Excel
                file.seek(0)
                pd.read_excel(file, nrows=5)
            file.seek(0)  # Reset file pointer
        except Exception as e:
            raise forms.ValidationError(f"Invalid file format or corrupted file: {str(e)}")
        
        return file


class LocationForm(forms.ModelForm):
    """Form for creating/editing locations"""
    
    class Meta:
        model = Location
        fields = [
            'name', 'description', 'latitude', 'longitude', 'elevation',
            'site_type', 'land_use', 'distance_to_source'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
                'rows': 3
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
                'step': '0.0000001',
                'placeholder': 'e.g., 9.0579'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
                'step': '0.0000001',
                'placeholder': 'e.g., 7.4951'
            }),
            'elevation': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
                'step': '0.01',
                'placeholder': 'meters above sea level'
            }),
            'site_type': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500'
            }),
            'land_use': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500'
            }),
            'distance_to_source': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500',
                'step': '0.01',
                'placeholder': 'Distance in meters'
            }),
        }


class DataPreviewForm(forms.Form):
    """Form for confirming data import after preview"""
    
    confirm_import = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded'
        })
    )
    
    # Hidden fields to pass data
    upload_session_id = forms.CharField(widget=forms.HiddenInput())