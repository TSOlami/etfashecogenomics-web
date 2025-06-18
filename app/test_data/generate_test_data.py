import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducible results
np.random.seed(42)
random.seed(42)

def generate_water_quality_simple():
    """Generate simple water quality data"""
    locations = ['Lagos Lagoon', 'Ogun River', 'Niger Delta', 'Cross River', 'Benue River']
    parameters = ['pH', 'Dissolved Oxygen', 'Turbidity', 'Total Dissolved Solids', 'Temperature']
    
    data = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(100):
        date = base_date + timedelta(days=i//20, hours=random.randint(6, 18))
        location = random.choice(locations)
        
        for param in parameters:
            if param == 'pH':
                concentration = round(np.random.normal(7.2, 0.8), 2)
                unit = 'pH units'
            elif param == 'Dissolved Oxygen':
                concentration = round(np.random.normal(6.5, 1.2), 2)
                unit = 'mg/L'
            elif param == 'Turbidity':
                concentration = round(np.random.lognormal(1.5, 0.8), 2)
                unit = 'NTU'
            elif param == 'Total Dissolved Solids':
                concentration = round(np.random.normal(250, 80), 1)
                unit = 'mg/L'
            else:  # Temperature
                concentration = round(np.random.normal(26.5, 2.1), 1)
                unit = '°C'
            
            data.append({
                'Location': location,
                'Parameter': param,
                'Concentration': max(0, concentration),
                'Unit': unit,
                'Sampling_Date': date.strftime('%Y-%m-%d %H:%M'),
                'Depth': round(np.random.uniform(0.5, 3.0), 1),
                'Weather': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy']),
                'Operator': random.choice(['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson'])
            })
    
    df = pd.DataFrame(data)
    df.to_excel('app/test_data/water_quality_simple.xlsx', index=False)
    print("Generated water_quality_simple.xlsx")

def generate_multi_location_monitoring():
    """Generate multi-location monitoring data"""
    # Nigerian cities and their typical pollution characteristics
    locations = {
        'Lagos_Mainland': {'traffic': 'high', 'industrial': 'medium', 'lat': 6.5244, 'lon': 3.3792},
        'Lagos_Island': {'traffic': 'very_high', 'industrial': 'low', 'lat': 6.4541, 'lon': 3.3947},
        'Kano_Industrial': {'traffic': 'medium', 'industrial': 'very_high', 'lat': 12.0022, 'lon': 8.5920},
        'Abuja_Central': {'traffic': 'medium', 'industrial': 'low', 'lat': 9.0765, 'lon': 7.3986},
        'Port_Harcourt': {'traffic': 'high', 'industrial': 'very_high', 'lat': 4.8156, 'lon': 7.0498},
        'Ibadan_Urban': {'traffic': 'high', 'industrial': 'medium', 'lat': 7.3775, 'lon': 3.9470},
        'Kaduna_City': {'traffic': 'medium', 'industrial': 'high', 'lat': 10.5222, 'lon': 7.4383},
        'Benin_City': {'traffic': 'medium', 'industrial': 'medium', 'lat': 6.3350, 'lon': 5.6037},
        'Jos_Plateau': {'traffic': 'low', 'industrial': 'medium', 'lat': 9.8965, 'lon': 8.8583},
        'Warri_Delta': {'traffic': 'medium', 'industrial': 'very_high', 'lat': 5.5160, 'lon': 5.7500}
    }
    
    pollutants = {
        'PM2.5': {'base': 25, 'traffic_factor': 1.5, 'industrial_factor': 2.0, 'unit': 'µg/m³'},
        'PM10': {'base': 45, 'traffic_factor': 1.3, 'industrial_factor': 1.8, 'unit': 'µg/m³'},
        'NO2': {'base': 30, 'traffic_factor': 2.0, 'industrial_factor': 1.2, 'unit': 'µg/m³'},
        'SO2': {'base': 15, 'traffic_factor': 1.1, 'industrial_factor': 3.0, 'unit': 'µg/m³'},
        'CO': {'base': 2.5, 'traffic_factor': 2.5, 'industrial_factor': 1.5, 'unit': 'mg/m³'},
        'O3': {'base': 80, 'traffic_factor': 1.2, 'industrial_factor': 0.8, 'unit': 'µg/m³'},
        'Lead': {'base': 0.1, 'traffic_factor': 1.8, 'industrial_factor': 4.0, 'unit': 'µg/m³'},
        'Benzene': {'base': 2.0, 'traffic_factor': 3.0, 'industrial_factor': 2.5, 'unit': 'µg/m³'}
    }
    
    intensity_multipliers = {
        'low': 0.6, 'medium': 1.0, 'high': 1.4, 'very_high': 2.0
    }
    
    data = []
    base_date = datetime(2024, 1, 1)
    
    for day in range(90):  # 3 months of data
        current_date = base_date + timedelta(days=day)
        
        for location, characteristics in locations.items():
            # Generate 3 measurements per day (morning, afternoon, evening)
            for hour in [8, 14, 20]:
                measurement_time = current_date + timedelta(hours=hour)
                
                # Environmental conditions
                temp = 25 + 8 * np.sin(2 * np.pi * day / 365) + np.random.normal(0, 2)
                humidity = 60 + 20 * np.sin(2 * np.pi * (day + 90) / 365) + np.random.normal(0, 5)
                wind_speed = max(0.1, np.random.lognormal(1.2, 0.6))
                wind_direction = np.random.uniform(0, 360)
                pressure = np.random.normal(1013.25, 5)
                
                for pollutant, props in pollutants.items():
                    # Calculate concentration based on location characteristics
                    traffic_mult = intensity_multipliers[characteristics['traffic']]
                    industrial_mult = intensity_multipliers[characteristics['industrial']]
                    
                    base_conc = props['base']
                    traffic_effect = base_conc * (props['traffic_factor'] - 1) * traffic_mult
                    industrial_effect = base_conc * (props['industrial_factor'] - 1) * industrial_mult
                    
                    # Time of day effects
                    if hour == 8:  # Morning rush
                        time_factor = 1.3 if 'traffic' in characteristics else 1.0
                    elif hour == 14:  # Afternoon
                        time_factor = 1.1
                    else:  # Evening
                        time_factor = 1.2 if 'traffic' in characteristics else 0.9
                    
                    # Weather effects
                    weather_factor = 1.0
                    if wind_speed < 2:  # Low wind increases pollution
                        weather_factor *= 1.4
                    if humidity > 80:  # High humidity affects some pollutants
                        weather_factor *= 1.1
                    
                    concentration = (base_conc + traffic_effect + industrial_effect) * time_factor * weather_factor
                    concentration *= np.random.lognormal(0, 0.2)  # Add variability
                    concentration = max(0.01, concentration)
                    
                    # Quality flags
                    quality_flag = 'valid'
                    if np.random.random() < 0.02:  # 2% chance of issues
                        quality_flag = random.choice(['questionable', 'calibration'])
                    
                    data.append({
                        'Location': location.replace('_', ' '),
                        'Latitude': characteristics['lat'] + np.random.normal(0, 0.001),
                        'Longitude': characteristics['lon'] + np.random.normal(0, 0.001),
                        'Pollutant': pollutant,
                        'Concentration': round(concentration, 3),
                        'Unit': props['unit'],
                        'Measurement_Date': measurement_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Temperature': round(temp, 1),
                        'Humidity': round(max(20, min(95, humidity)), 1),
                        'Wind_Speed': round(wind_speed, 1),
                        'Wind_Direction': round(wind_direction, 1),
                        'Pressure': round(pressure, 2),
                        'Quality_Flag': quality_flag,
                        'Equipment': random.choice(['BAM-1020', 'TEOM-1405', 'AC32M', 'ML9841']),
                        'Operator': random.choice(['A. Adebayo', 'C. Okafor', 'F. Ibrahim', 'M. Yusuf', 'S. Eze']),
                        'Site_Type': random.choice(['urban', 'industrial', 'residential', 'commercial']),
                        'Sampling_Method': random.choice(['Continuous', 'Integrated', 'Grab Sample'])
                    })
    
    df = pd.DataFrame(data)
    df.to_csv('app/test_data/multi_location_monitoring.csv', index=False)
    print(f"Generated multi_location_monitoring.csv with {len(df)} records")

def generate_temporal_analysis_data():
    """Generate temporal analysis data with clear trends"""
    locations = ['Industrial_Zone_A', 'Residential_Area_B', 'Commercial_District_C']
    pollutants = ['PM2.5', 'NO2', 'SO2', 'O3']
    
    data = []
    base_date = datetime(2023, 1, 1)
    
    for day in range(365):  # Full year of data
        current_date = base_date + timedelta(days=day)
        
        # Seasonal effects
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * day / 365)
        
        for location in locations:
            for hour in range(0, 24, 3):  # Every 3 hours
                measurement_time = current_date + timedelta(hours=hour)
                
                for pollutant in pollutants:
                    # Base concentrations with trends
                    if pollutant == 'PM2.5':
                        base = 20 + 0.02 * day  # Increasing trend
                        daily_pattern = 1 + 0.5 * np.sin(2 * np.pi * hour / 24)
                    elif pollutant == 'NO2':
                        base = 40 - 0.01 * day  # Decreasing trend
                        daily_pattern = 1 + 0.8 * np.sin(2 * np.pi * (hour - 8) / 24)
                    elif pollutant == 'SO2':
                        base = 15 + 0.005 * day  # Slight increase
                        daily_pattern = 1 + 0.3 * np.sin(2 * np.pi * (hour - 12) / 24)
                    else:  # O3
                        base = 60 + 0.03 * day  # Increasing trend
                        daily_pattern = 1 + 0.6 * np.sin(2 * np.pi * (hour - 14) / 24)
                    
                    # Location effects
                    if 'Industrial' in location:
                        location_factor = 1.5
                    elif 'Commercial' in location:
                        location_factor = 1.2
                    else:
                        location_factor = 0.8
                    
                    concentration = base * seasonal_factor * daily_pattern * location_factor
                    concentration *= np.random.lognormal(0, 0.15)
                    concentration = max(0.1, concentration)
                    
                    # Environmental conditions
                    temp = 25 + 8 * np.sin(2 * np.pi * day / 365) + 5 * np.sin(2 * np.pi * hour / 24)
                    humidity = 65 + 15 * np.sin(2 * np.pi * (day + 90) / 365)
                    
                    data.append({
                        'Location': location.replace('_', ' '),
                        'Pollutant_Name': pollutant,
                        'Concentration': round(concentration, 2),
                        'Date': measurement_time.strftime('%Y-%m-%d'),
                        'Time': measurement_time.strftime('%H:%M'),
                        'DateTime': measurement_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Temperature': round(temp, 1),
                        'Humidity': round(humidity, 1),
                        'Day_of_Week': measurement_time.strftime('%A'),
                        'Month': measurement_time.strftime('%B'),
                        'Season': get_season(day),
                        'Hour_Category': get_hour_category(hour)
                    })
    
    df = pd.DataFrame(data)
    
    # Create Excel file with multiple sheets
    with pd.ExcelWriter('app/test_data/temporal_analysis_data.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All_Data', index=False)
        
        # Create separate sheets for each pollutant
        for pollutant in pollutants:
            pollutant_data = df[df['Pollutant_Name'] == pollutant]
            pollutant_data.to_excel(writer, sheet_name=f'{pollutant}_Data', index=False)
        
        # Create summary statistics sheet
        summary = df.groupby(['Location', 'Pollutant_Name']).agg({
            'Concentration': ['mean', 'std', 'min', 'max', 'count']
        }).round(2)
        summary.to_excel(writer, sheet_name='Summary_Statistics')
    
    print(f"Generated temporal_analysis_data.xlsx with {len(df)} records")

def get_season(day_of_year):
    """Get season based on day of year"""
    if day_of_year < 80 or day_of_year >= 355:
        return 'Dry_Season'
    elif day_of_year < 140:
        return 'Transition'
    elif day_of_year < 290:
        return 'Rainy_Season'
    else:
        return 'Transition'

def get_hour_category(hour):
    """Categorize hour of day"""
    if 6 <= hour < 10:
        return 'Morning_Rush'
    elif 10 <= hour < 16:
        return 'Daytime'
    elif 16 <= hour < 20:
        return 'Evening_Rush'
    else:
        return 'Night'

def generate_comprehensive_environmental_study():
    """Generate comprehensive environmental study data"""
    # Extended pollutant list with all major categories
    pollutants = {
        # Criteria Air Pollutants
        'PM2.5': {'base': 25, 'unit': 'µg/m³', 'who_std': 15, 'nesrea_std': 35},
        'PM10': {'base': 45, 'unit': 'µg/m³', 'who_std': 45, 'nesrea_std': 150},
        'NO2': {'base': 35, 'unit': 'µg/m³', 'who_std': 40, 'nesrea_std': 100},
        'SO2': {'base': 20, 'unit': 'µg/m³', 'who_std': 20, 'nesrea_std': 365},
        'CO': {'base': 3.5, 'unit': 'mg/m³', 'who_std': 10, 'nesrea_std': 10},
        'O3': {'base': 85, 'unit': 'µg/m³', 'who_std': 100, 'nesrea_std': 157},
        
        # Heavy Metals
        'Lead': {'base': 0.15, 'unit': 'µg/m³', 'who_std': 0.5, 'nesrea_std': 1.5},
        'Mercury': {'base': 0.05, 'unit': 'µg/m³', 'who_std': 1.0, 'nesrea_std': None},
        'Cadmium': {'base': 0.8, 'unit': 'µg/m³', 'who_std': 5.0, 'nesrea_std': None},
        'Arsenic': {'base': 1.2, 'unit': 'µg/m³', 'who_std': 6.6, 'nesrea_std': None},
        
        # VOCs
        'Benzene': {'base': 3.2, 'unit': 'µg/m³', 'who_std': 1.7, 'nesrea_std': None},
        'Toluene': {'base': 15.5, 'unit': 'µg/m³', 'who_std': 260, 'nesrea_std': None},
        'Xylene': {'base': 8.7, 'unit': 'µg/m³', 'who_std': 870, 'nesrea_std': None},
        'Formaldehyde': {'base': 12.3, 'unit': 'µg/m³', 'who_std': 100, 'nesrea_std': None},
        
        # Other Important Pollutants
        'TSP': {'base': 120, 'unit': 'µg/m³', 'who_std': None, 'nesrea_std': 250},
        'H2S': {'base': 8.5, 'unit': 'µg/m³', 'who_std': 150, 'nesrea_std': None},
        'NH3': {'base': 25.2, 'unit': 'µg/m³', 'who_std': 200, 'nesrea_std': None}
    }
    
    # Comprehensive location network
    locations = {
        'Lagos_Victoria_Island': {'type': 'commercial', 'lat': 6.4281, 'lon': 3.4219, 'elevation': 5},
        'Lagos_Ikeja_Industrial': {'type': 'industrial', 'lat': 6.6018, 'lon': 3.3515, 'elevation': 45},
        'Lagos_Surulere_Residential': {'type': 'residential', 'lat': 6.5027, 'lon': 3.3641, 'elevation': 25},
        'Kano_Industrial_Estate': {'type': 'industrial', 'lat': 12.0022, 'lon': 8.5920, 'elevation': 472},
        'Abuja_City_Center': {'type': 'commercial', 'lat': 9.0579, 'lon': 7.4951, 'elevation': 840},
        'Port_Harcourt_Refinery': {'type': 'industrial', 'lat': 4.8156, 'lon': 7.0498, 'elevation': 15},
        'Ibadan_University': {'type': 'institutional', 'lat': 7.3775, 'lon': 3.9470, 'elevation': 200},
        'Jos_Mining_Area': {'type': 'mining', 'lat': 9.8965, 'lon': 8.8583, 'elevation': 1238},
        'Warri_Petrochemical': {'type': 'industrial', 'lat': 5.5160, 'lon': 5.7500, 'elevation': 8},
        'Kaduna_Textile_Zone': {'type': 'industrial', 'lat': 10.5222, 'lon': 7.4383, 'elevation': 645},
        'Benin_Urban_Background': {'type': 'urban', 'lat': 6.3350, 'lon': 5.6037, 'elevation': 85},
        'Calabar_Coastal': {'type': 'coastal', 'lat': 4.9517, 'lon': 8.3220, 'elevation': 62}
    }
    
    data = []
    base_date = datetime(2023, 6, 1)
    
    # Generate 6 months of comprehensive data
    for day in range(180):
        current_date = base_date + timedelta(days=day)
        
        for location_name, location_info in locations.items():
            # Generate measurements at different times
            for hour in [6, 10, 14, 18, 22]:
                measurement_time = current_date + timedelta(hours=hour)
                
                # Environmental conditions with realistic variations
                base_temp = 26 + 6 * np.sin(2 * np.pi * day / 365)
                temp = base_temp + 8 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1.5)
                
                humidity = 70 + 20 * np.sin(2 * np.pi * (day + 90) / 365) + np.random.normal(0, 5)
                humidity = max(30, min(95, humidity))
                
                wind_speed = max(0.1, np.random.weibull(2) * 5)
                wind_direction = np.random.uniform(0, 360)
                pressure = np.random.normal(1013.25, 8)
                
                # Solar radiation (daytime only)
                if 6 <= hour <= 18:
                    solar_radiation = 800 * np.sin(np.pi * (hour - 6) / 12) + np.random.normal(0, 50)
                    solar_radiation = max(0, solar_radiation)
                else:
                    solar_radiation = 0
                
                for pollutant, props in pollutants.items():
                    # Complex concentration calculation
                    base_conc = props['base']
                    
                    # Location type effects
                    type_multipliers = {
                        'industrial': 2.5, 'commercial': 1.3, 'residential': 0.8,
                        'urban': 1.2, 'coastal': 0.7, 'institutional': 0.9, 'mining': 1.8
                    }
                    location_factor = type_multipliers.get(location_info['type'], 1.0)
                    
                    # Temporal effects
                    if hour in [7, 8, 17, 18]:  # Rush hours
                        time_factor = 1.4
                    elif hour in [10, 11, 14, 15]:  # Business hours
                        time_factor = 1.2
                    else:
                        time_factor = 0.8
                    
                    # Weather effects
                    weather_factor = 1.0
                    if wind_speed < 2:
                        weather_factor *= 1.5  # Low wind increases pollution
                    if humidity > 85:
                        weather_factor *= 1.1  # High humidity effects
                    if solar_radiation > 500 and pollutant == 'O3':
                        weather_factor *= 1.3  # Photochemical formation
                    
                    # Seasonal effects
                    if 150 <= day <= 270:  # Rainy season
                        if pollutant in ['PM2.5', 'PM10', 'TSP']:
                            weather_factor *= 0.7  # Rain washes out particles
                    
                    concentration = base_conc * location_factor * time_factor * weather_factor
                    concentration *= np.random.lognormal(0, 0.25)
                    concentration = max(0.001, concentration)
                    
                    # Quality control
                    quality_flag = 'valid'
                    uncertainty = np.random.uniform(5, 15)
                    
                    if np.random.random() < 0.03:  # 3% chance of issues
                        quality_flag = random.choice(['questionable', 'calibration', 'maintenance'])
                        uncertainty *= 2
                    
                    # Detection limit
                    detection_limit = concentration * 0.1 * np.random.uniform(0.5, 1.5)
                    
                    # Equipment and methods
                    equipment_options = {
                        'PM2.5': ['BAM-1020', 'TEOM-1405', 'DustTrak-8533'],
                        'PM10': ['BAM-1020', 'TEOM-1405', 'Partisol-2000i'],
                        'NO2': ['AC32M', 'ML9841A', 'T200'],
                        'SO2': ['AF22M', 'ML9850A', 'T100'],
                        'CO': ['AL5002', 'ML9830A', 'T300'],
                        'O3': ['ML9810A', 'T400', 'UV-100']
                    }
                    
                    equipment = random.choice(equipment_options.get(pollutant, ['Generic_Analyzer']))
                    
                    data.append({
                        'Location_Name': location_name.replace('_', ' '),
                        'Latitude': location_info['lat'] + np.random.normal(0, 0.0005),
                        'Longitude': location_info['lon'] + np.random.normal(0, 0.0005),
                        'Elevation': location_info['elevation'],
                        'Site_Type': location_info['type'],
                        'Pollutant_Name': pollutant,
                        'Concentration': round(concentration, 4),
                        'Unit': props['unit'],
                        'WHO_Standard': props['who_std'],
                        'NESREA_Standard': props['nesrea_std'],
                        'Measurement_Date': measurement_time.strftime('%Y-%m-%d'),
                        'Measurement_Time': measurement_time.strftime('%H:%M:%S'),
                        'Full_DateTime': measurement_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Temperature': round(temp, 1),
                        'Humidity': round(humidity, 1),
                        'Wind_Speed': round(wind_speed, 1),
                        'Wind_Direction': round(wind_direction, 1),
                        'Atmospheric_Pressure': round(pressure, 2),
                        'Solar_Radiation': round(solar_radiation, 1),
                        'Quality_Flag': quality_flag,
                        'Uncertainty_Percent': round(uncertainty, 1),
                        'Detection_Limit': round(detection_limit, 4),
                        'Equipment_Used': equipment,
                        'Sampling_Method': random.choice(['Continuous', 'Integrated_24h', 'Integrated_8h']),
                        'Calibration_Date': (measurement_time - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                        'Operator': random.choice(['Dr. A. Adebayo', 'Eng. C. Okafor', 'Prof. F. Ibrahim', 'Mr. M. Yusuf', 'Mrs. S. Eze']),
                        'Sample_ID': f"ENV_{measurement_time.strftime('%Y%m%d')}_{location_name[:3]}_{pollutant}_{hour:02d}",
                        'Chain_of_Custody': f"COC_{measurement_time.strftime('%Y%m%d')}_{random.randint(1000, 9999)}",
                        'Laboratory': random.choice(['NESREA Lab Lagos', 'University of Lagos', 'FMENV Lab Abuja']),
                        'Analysis_Date': (measurement_time + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
                        'Notes': random.choice(['', 'Normal conditions', 'High traffic nearby', 'Construction activity', 'Industrial emission event']) if np.random.random() < 0.2 else ''
                    })
    
    df = pd.DataFrame(data)
    df.to_csv('app/test_data/comprehensive_environmental_study.csv', index=False)
    print(f"Generated comprehensive_environmental_study.csv with {len(df)} records")

def generate_massive_dataset():
    """Generate massive dataset for stress testing"""
    print("Generating massive dataset (this may take a few minutes)...")
    
    # Simplified but large dataset
    locations = [f"Location_{i:03d}" for i in range(50)]  # 50 locations
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'Lead', 'Benzene']
    
    data = []
    base_date = datetime(2022, 1, 1)
    
    # Generate 2 years of hourly data for stress testing
    for day in range(730):  # 2 years
        if day % 100 == 0:
            print(f"Processing day {day}/730...")
        
        current_date = base_date + timedelta(days=day)
        
        # Sample every 6 hours to keep dataset manageable but large
        for hour in range(0, 24, 6):
            measurement_time = current_date + timedelta(hours=hour)
            
            for location in locations:
                for pollutant in pollutants:
                    # Simple concentration calculation for speed
                    base_conc = {'PM2.5': 25, 'PM10': 45, 'NO2': 35, 'SO2': 20, 
                               'CO': 3.5, 'O3': 85, 'Lead': 0.15, 'Benzene': 3.2}[pollutant]
                    
                    concentration = base_conc * np.random.lognormal(0, 0.3)
                    
                    data.append({
                        'Location': location,
                        'Pollutant': pollutant,
                        'Concentration': round(concentration, 3),
                        'Date': measurement_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Temperature': round(np.random.normal(26, 5), 1),
                        'Humidity': round(np.random.normal(65, 15), 1),
                        'Quality_Flag': 'valid' if np.random.random() > 0.02 else 'questionable'
                    })
    
    df = pd.DataFrame(data)
    df.to_csv('app/test_data/massive_dataset.csv', index=False)
    print(f"Generated massive_dataset.csv with {len(df)} records")

def generate_edge_cases_data():
    """Generate data with edge cases and missing values"""
    data = []
    base_date = datetime(2024, 1, 1)
    
    locations = ['Test_Location_A', 'Test_Location_B', 'Test_Location_C']
    pollutants = ['PM2.5', 'NO2', 'SO2', 'CO']
    
    for i in range(200):
        date = base_date + timedelta(days=i//10, hours=random.randint(0, 23))
        location = random.choice(locations)
        pollutant = random.choice(pollutants)
        
        # Create various edge cases
        if i % 20 == 0:  # Missing concentration
            concentration = None
        elif i % 25 == 0:  # Extremely high value
            concentration = 999.999
        elif i % 30 == 0:  # Zero value
            concentration = 0.0
        elif i % 35 == 0:  # Negative value (should be caught by validation)
            concentration = -5.2
        elif i % 40 == 0:  # Very small value
            concentration = 0.001
        else:
            concentration = round(np.random.lognormal(2, 1), 3)
        
        # Missing environmental data
        temp = None if i % 15 == 0 else round(np.random.normal(26, 5), 1)
        humidity = None if i % 18 == 0 else round(np.random.normal(65, 15), 1)
        
        # Invalid coordinates
        if i % 45 == 0:
            lat, lon = None, None
        elif i % 50 == 0:
            lat, lon = 999, 999  # Invalid coordinates
        else:
            lat = round(6.5 + np.random.normal(0, 0.1), 6)
            lon = round(3.4 + np.random.normal(0, 0.1), 6)
        
        # Special characters in text fields
        if i % 60 == 0:
            location = "Location with special chars: @#$%^&*()"
            notes = "Notes with unicode: αβγδε and emojis: 🌍🔬"
        else:
            notes = ""
        
        data.append({
            'Location': location,
            'Latitude': lat,
            'Longitude': lon,
            'Pollutant': pollutant,
            'Concentration': concentration,
            'Date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'Temperature': temp,
            'Humidity': humidity,
            'Quality_Flag': random.choice(['valid', 'questionable', 'invalid', 'below_detection', '']),
            'Equipment': random.choice(['Equipment_A', '', 'Unknown', 'N/A']),
            'Operator': random.choice(['John Doe', '', 'TBD', 'Multiple']),
            'Notes': notes
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel with multiple problematic sheets
    with pd.ExcelWriter('app/test_data/edge_cases_data.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Main_Data', index=False)
        
        # Sheet with different column names
        df_renamed = df.copy()
        df_renamed.columns = ['Site', 'Lat', 'Long', 'Parameter', 'Value', 'DateTime', 'Temp', 'RH', 'QC', 'Instrument', 'Tech', 'Comments']
        df_renamed.to_excel(writer, sheet_name='Different_Columns', index=False)
        
        # Sheet with extra columns
        df_extra = df.copy()
        df_extra['Extra_Column_1'] = 'Extra data'
        df_extra['Extra_Column_2'] = np.random.randn(len(df))
        df_extra.to_excel(writer, sheet_name='Extra_Columns', index=False)
    
    print(f"Generated edge_cases_data.xlsx with {len(df)} records")

def generate_factory_monitoring_campaign():
    """Generate realistic factory monitoring campaign data"""
    # Cement factory case study
    factory_location = {'lat': 6.5244, 'lon': 3.3792, 'name': 'Dangote Cement Factory'}
    
    # Monitoring locations at different distances from factory
    monitoring_sites = {
        'Factory_Boundary_North': {'lat': 6.5254, 'lon': 3.3792, 'distance': 100, 'direction': 'N'},
        'Factory_Boundary_South': {'lat': 6.5234, 'lon': 3.3792, 'distance': 100, 'direction': 'S'},
        'Factory_Boundary_East': {'lat': 6.5244, 'lon': 3.3802, 'distance': 100, 'direction': 'E'},
        'Factory_Boundary_West': {'lat': 6.5244, 'lon': 3.3782, 'distance': 100, 'direction': 'W'},
        'Residential_Area_500m': {'lat': 6.5289, 'lon': 3.3792, 'distance': 500, 'direction': 'N'},
        'School_1km_East': {'lat': 6.5244, 'lon': 3.3892, 'distance': 1000, 'direction': 'E'},
        'Hospital_1km_West': {'lat': 6.5244, 'lon': 3.3692, 'distance': 1000, 'direction': 'W'},
        'Background_Site_5km': {'lat': 6.5694, 'lon': 3.3792, 'distance': 5000, 'direction': 'N'}
    }
    
    # Pollutants relevant to cement manufacturing
    cement_pollutants = {
        'PM2.5': {'baseline': 15, 'factory_impact': 25, 'unit': 'µg/m³'},
        'PM10': {'baseline': 30, 'factory_impact': 80, 'unit': 'µg/m³'},
        'TSP': {'baseline': 60, 'factory_impact': 200, 'unit': 'µg/m³'},
        'SO2': {'baseline': 10, 'factory_impact': 45, 'unit': 'µg/m³'},
        'NO2': {'baseline': 25, 'factory_impact': 15, 'unit': 'µg/m³'},
        'CO': {'baseline': 2, 'factory_impact': 3, 'unit': 'mg/m³'},
        'Lead': {'baseline': 0.05, 'factory_impact': 0.3, 'unit': 'µg/m³'},
        'Mercury': {'baseline': 0.01, 'factory_impact': 0.08, 'unit': 'µg/m³'},
        'Cadmium': {'baseline': 0.2, 'factory_impact': 1.5, 'unit': 'µg/m³'}
    }
    
    data = []
    base_date = datetime(2024, 1, 1)
    
    # 6 months of monitoring (before, during, after factory operations)
    for day in range(180):
        current_date = base_date + timedelta(days=day)
        
        # Factory operation schedule
        if day < 30:  # Pre-operation baseline
            factory_operation = 0.0
            operation_phase = 'Baseline'
        elif day < 150:  # Full operation
            factory_operation = 1.0
            operation_phase = 'Operation'
        else:  # Reduced operation
            factory_operation = 0.6
            operation_phase = 'Reduced_Operation'
        
        for site_name, site_info in monitoring_sites.items():
            # Measurements every 4 hours
            for hour in [6, 10, 14, 18, 22]:
                measurement_time = current_date + timedelta(hours=hour)
                
                # Environmental conditions
                temp = 27 + 6 * np.sin(2 * np.pi * day / 365) + 4 * np.sin(2 * np.pi * hour / 24)
                humidity = 70 + 15 * np.sin(2 * np.pi * (day + 90) / 365)
                wind_speed = max(0.5, np.random.weibull(2) * 4)
                wind_direction = np.random.uniform(0, 360)
                
                # Wind direction effect (pollution higher when downwind)
                wind_effect = 1.0
                site_direction = site_info['direction']
                if site_direction == 'N' and 315 <= wind_direction <= 360 or 0 <= wind_direction <= 45:
                    wind_effect = 2.0  # Downwind
                elif site_direction == 'S' and 135 <= wind_direction <= 225:
                    wind_effect = 2.0
                elif site_direction == 'E' and 45 <= wind_direction <= 135:
                    wind_effect = 2.0
                elif site_direction == 'W' and 225 <= wind_direction <= 315:
                    wind_effect = 2.0
                
                for pollutant, props in cement_pollutants.items():
                    # Distance decay effect
                    distance_factor = 1.0 / (1 + site_info['distance'] / 200)
                    
                    # Base concentration
                    baseline = props['baseline']
                    factory_impact = props['factory_impact'] * factory_operation * distance_factor * wind_effect
                    
                    # Time of day effects (factory operates 24/7 but varies)
                    if 6 <= hour <= 18:  # Day shift - higher activity
                        time_factor = 1.2
                    else:  # Night shift - lower activity
                        time_factor = 0.8
                    
                    concentration = baseline + factory_impact * time_factor
                    concentration *= np.random.lognormal(0, 0.2)
                    concentration = max(0.001, concentration)
                    
                    # Quality assurance
                    quality_flag = 'valid'
                    if np.random.random() < 0.01:  # 1% QC issues
                        quality_flag = random.choice(['calibration', 'maintenance'])
                    
                    data.append({
                        'Site_Name': site_name.replace('_', ' '),
                        'Site_Code': site_name,
                        'Latitude': site_info['lat'],
                        'Longitude': site_info['lon'],
                        'Distance_from_Factory_m': site_info['distance'],
                        'Direction_from_Factory': site_info['direction'],
                        'Pollutant': pollutant,
                        'Concentration': round(concentration, 4),
                        'Unit': props['unit'],
                        'Measurement_DateTime': measurement_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Date': measurement_time.strftime('%Y-%m-%d'),
                        'Time': measurement_time.strftime('%H:%M'),
                        'Day_of_Study': day + 1,
                        'Operation_Phase': operation_phase,
                        'Factory_Operation_Level': factory_operation,
                        'Temperature_C': round(temp, 1),
                        'Humidity_Percent': round(humidity, 1),
                        'Wind_Speed_ms': round(wind_speed, 1),
                        'Wind_Direction_deg': round(wind_direction, 1),
                        'Wind_Effect_Factor': round(wind_effect, 2),
                        'Quality_Flag': quality_flag,
                        'Sampling_Duration_hours': 1,
                        'Equipment_ID': f"MON_{site_name[:3]}_{pollutant}",
                        'Calibration_Status': 'Valid',
                        'Data_Completeness_Percent': 100 if quality_flag == 'valid' else 75,
                        'Meteorological_Station': 'Factory_Met_Station',
                        'Project_Code': 'CEMENT_IMPACT_2024',
                        'Study_Phase': f"Phase_{1 if day < 60 else 2 if day < 120 else 3}",
                        'Regulatory_Standard_WHO': props.get('who_std'),
                        'Regulatory_Standard_NESREA': props.get('nesrea_std'),
                        'Exceeds_WHO': concentration > props.get('who_std', float('inf')),
                        'Exceeds_NESREA': concentration > props.get('nesrea_std', float('inf')),
                        'Comments': f"Factory operation at {factory_operation*100:.0f}%" if day % 30 == 0 else ""
                    })
    
    df = pd.DataFrame(data)
    df.to_csv('app/test_data/factory_monitoring_campaign.csv', index=False)
    print(f"Generated factory_monitoring_campaign.csv with {len(df)} records")

def generate_urban_air_quality_network():
    """Generate urban air quality network data"""
    # Lagos air quality monitoring network
    network_sites = {
        'Lagos_Island_Commercial': {'lat': 6.4541, 'lon': 3.3947, 'type': 'commercial', 'traffic': 'very_high'},
        'Victoria_Island_Business': {'lat': 6.4281, 'lon': 3.4219, 'type': 'commercial', 'traffic': 'high'},
        'Ikeja_Industrial': {'lat': 6.6018, 'lon': 3.3515, 'type': 'industrial', 'traffic': 'medium'},
        'Surulere_Residential': {'lat': 6.5027, 'lon': 3.3641, 'type': 'residential', 'traffic': 'medium'},
        'Yaba_Mixed_Use': {'lat': 6.5158, 'lon': 3.3696, 'type': 'mixed', 'traffic': 'high'},
        'Apapa_Port_Industrial': {'lat': 6.4474, 'lon': 3.3619, 'type': 'industrial', 'traffic': 'very_high'},
        'Lekki_Residential': {'lat': 6.4698, 'lon': 3.5852, 'type': 'residential', 'traffic': 'low'},
        'Mainland_Urban': {'lat': 6.5244, 'lon': 3.3792, 'type': 'urban', 'traffic': 'high'},
        'Airport_Road': {'lat': 6.5770, 'lon': 3.3211, 'type': 'transport', 'traffic': 'very_high'},
        'University_Campus': {'lat': 6.5158, 'lon': 3.3696, 'type': 'institutional', 'traffic': 'low'}
    }
    
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
    
    data = []
    base_date = datetime(2024, 1, 1)
    
    # Generate 3 months of hourly data
    for day in range(90):
        current_date = base_date + timedelta(days=day)
        
        for hour in range(24):
            measurement_time = current_date + timedelta(hours=hour)
            
            # City-wide meteorological conditions
            temp = 26 + 6 * np.sin(2 * np.pi * day / 365) + 6 * np.sin(2 * np.pi * hour / 24)
            humidity = 75 + 15 * np.sin(2 * np.pi * (day + 90) / 365)
            wind_speed = max(0.1, np.random.weibull(1.5) * 3)
            wind_direction = np.random.uniform(0, 360)
            
            # Traffic patterns
            if 6 <= hour <= 9 or 17 <= hour <= 20:  # Rush hours
                traffic_factor = 2.0
            elif 10 <= hour <= 16:  # Business hours
                traffic_factor = 1.3
            elif 21 <= hour <= 23:  # Evening
                traffic_factor = 1.1
            else:  # Night
                traffic_factor = 0.5
            
            for site_name, site_info in network_sites.items():
                # Site-specific factors
                traffic_multipliers = {'low': 0.6, 'medium': 1.0, 'high': 1.5, 'very_high': 2.2}
                site_traffic_factor = traffic_multipliers[site_info['traffic']]
                
                type_multipliers = {
                    'residential': 0.8, 'commercial': 1.2, 'industrial': 1.8,
                    'mixed': 1.1, 'transport': 1.6, 'institutional': 0.7, 'urban': 1.0
                }
                site_type_factor = type_multipliers[site_info['type']]
                
                for pollutant in pollutants:
                    # Base concentrations for Lagos
                    base_concentrations = {
                        'PM2.5': 35, 'PM10': 65, 'NO2': 45, 'SO2': 25, 'CO': 4.5, 'O3': 75
                    }
                    
                    base_conc = base_concentrations[pollutant]
                    
                    # Pollutant-specific factors
                    if pollutant in ['NO2', 'CO']:  # Traffic-related
                        traffic_effect = traffic_factor * site_traffic_factor
                    else:
                        traffic_effect = 1 + 0.3 * (traffic_factor - 1) * site_traffic_factor
                    
                    # Weather effects
                    weather_factor = 1.0
                    if wind_speed < 1.5:
                        weather_factor *= 1.4  # Low wind increases pollution
                    if humidity > 85:
                        weather_factor *= 1.1
                    
                    # Ozone photochemistry
                    if pollutant == 'O3' and 10 <= hour <= 16:
                        weather_factor *= 1.3  # Daytime ozone formation
                    
                    concentration = base_conc * site_type_factor * traffic_effect * weather_factor
                    concentration *= np.random.lognormal(0, 0.2)
                    concentration = max(0.1, concentration)
                    
                    # Data quality
                    data_completeness = 100
                    quality_flag = 'valid'
                    
                    if np.random.random() < 0.02:  # 2% data issues
                        quality_flag = random.choice(['questionable', 'calibration', 'maintenance'])
                        data_completeness = random.randint(75, 95)
                    
                    data.append({
                        'Station_Name': site_name.replace('_', ' '),
                        'Station_Code': site_name,
                        'Network': 'Lagos_Air_Quality_Network',
                        'Latitude': site_info['lat'],
                        'Longitude': site_info['lon'],
                        'Site_Type': site_info['type'],
                        'Traffic_Level': site_info['traffic'],
                        'Pollutant': pollutant,
                        'Concentration': round(concentration, 2),
                        'Unit': 'µg/m³' if pollutant != 'CO' else 'mg/m³',
                        'DateTime': measurement_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Date': measurement_time.strftime('%Y-%m-%d'),
                        'Hour': hour,
                        'Day_of_Week': measurement_time.strftime('%A'),
                        'Month': measurement_time.strftime('%B'),
                        'Temperature': round(temp, 1),
                        'Humidity': round(humidity, 1),
                        'Wind_Speed': round(wind_speed, 1),
                        'Wind_Direction': round(wind_direction, 1),
                        'Traffic_Factor': round(traffic_factor, 2),
                        'Quality_Flag': quality_flag,
                        'Data_Completeness': data_completeness,
                        'Instrument_Type': random.choice(['Continuous', 'Reference', 'Indicative']),
                        'Maintenance_Status': 'OK' if quality_flag == 'valid' else 'Attention_Required',
                        'Last_Calibration': (measurement_time - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                        'Network_Status': 'Operational',
                        'Data_Source': 'Lagos_State_Environmental_Protection_Agency',
                        'QA_QC_Status': 'Passed' if quality_flag == 'valid' else 'Review_Required'
                    })
    
    df = pd.DataFrame(data)
    
    # Create comprehensive Excel file with multiple sheets
    with pd.ExcelWriter('app/test_data/urban_air_quality_network.xlsx', engine='openpyxl') as writer:
        # Main data
        df.to_excel(writer, sheet_name='Hourly_Data', index=False)
        
        # Daily averages
        daily_avg = df.groupby(['Station_Name', 'Date', 'Pollutant']).agg({
            'Concentration': 'mean',
            'Temperature': 'mean',
            'Humidity': 'mean',
            'Wind_Speed': 'mean',
            'Data_Completeness': 'mean'
        }).round(2).reset_index()
        daily_avg.to_excel(writer, sheet_name='Daily_Averages', index=False)
        
        # Station metadata
        station_meta = []
        for station, info in network_sites.items():
            station_meta.append({
                'Station_Name': station.replace('_', ' '),
                'Station_Code': station,
                'Latitude': info['lat'],
                'Longitude': info['lon'],
                'Site_Type': info['type'],
                'Traffic_Level': info['traffic'],
                'Installation_Date': '2023-01-01',
                'Status': 'Active',
                'Pollutants_Measured': ', '.join(pollutants)
            })
        
        pd.DataFrame(station_meta).to_excel(writer, sheet_name='Station_Metadata', index=False)
        
        # Summary statistics
        summary = df.groupby(['Station_Name', 'Pollutant']).agg({
            'Concentration': ['count', 'mean', 'std', 'min', 'max']
        }).round(3)
        summary.to_excel(writer, sheet_name='Summary_Statistics')
    
    print(f"Generated urban_air_quality_network.xlsx with {len(df)} records")

if __name__ == "__main__":
    print("Generating comprehensive test datasets...")
    print("This may take several minutes for large datasets...")
    
    # Generate all test files
    generate_water_quality_simple()
    generate_multi_location_monitoring()
    generate_temporal_analysis_data()
    generate_comprehensive_environmental_study()
    generate_massive_dataset()
    generate_edge_cases_data()
    generate_factory_monitoring_campaign()
    generate_urban_air_quality_network()
    
    print("\n" + "="*60)
    print("TEST DATA GENERATION COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("1. basic_air_quality.csv - Simple air quality data (20 records)")
    print("2. water_quality_simple.xlsx - Basic water quality (100 records)")
    print("3. multi_location_monitoring.csv - Multi-location data (~21,600 records)")
    print("4. temporal_analysis_data.xlsx - Temporal trends (87,600 records)")
    print("5. comprehensive_environmental_study.csv - Full study (~183,600 records)")
    print("6. massive_dataset.csv - Stress test (~584,000 records)")
    print("7. edge_cases_data.xlsx - Edge cases and errors (200 records)")
    print("8. factory_monitoring_campaign.csv - Factory impact study (~32,400 records)")
    print("9. urban_air_quality_network.xlsx - Urban network (~194,400 records)")
    print("\nTotal: ~1,100,000+ test records across all files")
    print("\nRecommended testing order:")
    print("1. Start with basic_air_quality.csv")
    print("2. Test water_quality_simple.xlsx")
    print("3. Progress to multi_location_monitoring.csv")
    print("4. Test statistical analysis with temporal_analysis_data.xlsx")
    print("5. Full system test with comprehensive_environmental_study.csv")
    print("6. Stress test with massive_dataset.csv")
    print("7. Error handling with edge_cases_data.xlsx")
    print("8. Real-world scenarios with factory and urban network data")