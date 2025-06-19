# EcoGenomics Suite - Test Data

This directory contains test data files for comprehensive testing of the EcoGenomics Suite platform.

## Test Levels

### 1. Simple Tests (`simple/`)
- Basic functionality testing
- Small datasets (5-10 records)
- Single location data
- Perfect data quality

### 2. Intermediate Tests (`intermediate/`)
- Multi-location testing
- Medium datasets (50-100 records)
- Some missing values
- Real-world scenarios

### 3. Advanced Tests (`advanced/`)
- Complex multi-site studies
- Large datasets (500+ records)
- Multiple data types
- Edge cases and validation

### 4. Stress Tests (`stress_test/`)
- Performance testing
- Very large datasets (1000+ records)
- Extreme values
- System limits testing

## File Formats Supported
- ✅ CSV (.csv)
- ✅ Excel (.xlsx)
- ✅ Excel Legacy (.xls)

## Data Types
- **Environmental**: Air quality, water quality, soil analysis
- **Genomic**: DNA samples, mutations, gene analysis
- **Biodiversity**: Species observations, conservation status

## Usage Instructions

1. **Start Simple**: Begin with files in `simple/` directory
2. **Progress Gradually**: Move to `intermediate/` then `advanced/`
3. **Stress Test**: Use `stress_test/` files for performance evaluation
4. **Mix and Match**: Combine different data types for comprehensive testing

## Test Scenarios

### Basic Upload Test
```bash
1. Upload simple_environmental_data.csv
2. Check dashboard updates
3. Verify charts display correctly
```

### Multi-Data Type Test
```bash
1. Upload environmental data
2. Upload genomic samples
3. Upload biodiversity records
4. Run correlation analysis
5. Generate comprehensive report
```

### Performance Test
```bash
1. Upload large_environmental_dataset.xlsx
2. Monitor processing time
3. Check memory usage
4. Verify data integrity
```

## Expected Results

Each test level should demonstrate:
- ✅ Successful file upload
- ✅ Data processing and validation
- ✅ Dashboard metric updates
- ✅ Chart generation with real data
- ✅ Analysis functionality
- ✅ Report generation