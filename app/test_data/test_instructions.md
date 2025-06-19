# EcoGenomics Suite - Testing Instructions

## Quick Start Testing Guide

### 1. Basic Functionality Test (5 minutes)
```bash
# Test simple file upload
1. Login to the dashboard
2. Go to Environmental Monitoring tab
3. Download environmental template
4. Upload: test_data/simple/simple_environmental_data.csv
5. Verify dashboard updates with real data
6. Check that charts display actual values
```

### 2. Multi-Data Type Test (10 minutes)
```bash
# Test all data types
1. Upload: simple/simple_environmental_data.csv
2. Upload: simple/simple_genomic_samples.csv  
3. Upload: simple/simple_biodiversity_records.csv
4. Navigate through all tabs
5. Verify each tab shows real data
6. Run analysis on each data type
```

### 3. Intermediate Testing (15 minutes)
```bash
# Test larger datasets and Excel files
1. Upload: intermediate/multi_site_environmental.csv
2. Upload: intermediate/genomic_diversity_study.xlsx
3. Upload: intermediate/biodiversity_survey.csv
4. Run correlation analysis
5. Generate comprehensive report
6. Test template downloads
```

### 4. Advanced Testing (20 minutes)
```bash
# Test edge cases and missing data
1. Upload: advanced/comprehensive_environmental_study.csv
2. Upload: advanced/missing_values_test.csv
3. Verify system handles missing values gracefully
4. Run statistical analysis
5. Check error handling
```

### 5. Stress Testing (30 minutes)
```bash
# Test system limits and performance
1. Upload: stress_test/large_environmental_dataset.csv (2000+ records)
2. Upload: stress_test/massive_genomic_dataset.xlsx (1500+ samples)
3. Upload: stress_test/performance_test_biodiversity.csv
4. Monitor upload processing time
5. Test dashboard responsiveness
6. Run analysis on large datasets
7. Generate reports from large data
```

## Expected Results by Test Level

### Simple Tests ✅
- **Upload Time**: < 5 seconds
- **Dashboard Update**: Immediate
- **Charts**: Display real data points
- **Analysis**: Basic statistics work
- **Reports**: Generate successfully

### Intermediate Tests ✅
- **Upload Time**: < 15 seconds
- **Multi-location Data**: Properly categorized
- **Excel Files**: All sheets processed
- **Missing Values**: Handled gracefully
- **Complex Analysis**: Correlation matrices work

### Advanced Tests ✅
- **Large Files**: Process within 30 seconds
- **Edge Cases**: No system crashes
- **Data Validation**: Errors caught and reported
- **Performance**: Responsive under load

### Stress Tests ⚠️
- **Very Large Files**: May take 1-2 minutes
- **Memory Usage**: Monitor system resources
- **Database Performance**: Check query times
- **User Experience**: Should remain responsive

## Troubleshooting Common Issues

### Upload Failures
```bash
# Check file format
- Ensure CSV/Excel format
- Verify column headers match templates
- Check for special characters in data

# Check file size
- Large files (>10MB) may timeout
- Split very large files if needed
```

### Missing Data Display
```bash
# Verify data processing
- Check upload logs in Environmental tab
- Ensure processing status shows "Completed"
- Refresh browser if data doesn't appear
```

### Analysis Errors
```bash
# Insufficient data
- Need minimum 3 records for most analysis
- Correlation requires multiple parameters
- Check data quality and completeness
```

### Performance Issues
```bash
# Large dataset handling
- Allow extra time for processing
- Monitor browser memory usage
- Consider smaller batch uploads
```

## Test Data Characteristics

### Simple Test Files
- **Records**: 5-10 per file
- **Locations**: 1-2 sites
- **Quality**: Perfect data, no missing values
- **Purpose**: Basic functionality verification

### Intermediate Test Files
- **Records**: 50-100 per file
- **Locations**: 4-8 sites
- **Quality**: Realistic data with some gaps
- **Purpose**: Real-world scenario testing

### Advanced Test Files
- **Records**: 200-500 per file
- **Locations**: 10+ sites
- **Quality**: Complex data with edge cases
- **Purpose**: Robustness and validation testing

### Stress Test Files
- **Records**: 1000+ per file
- **Locations**: 20+ sites
- **Quality**: Large-scale realistic data
- **Purpose**: Performance and scalability testing

## Success Criteria

### ✅ Passing Tests
- All files upload successfully
- Dashboard metrics update with real data
- Charts display actual data points (not static)
- Analysis functions return real results
- Reports generate with actual content
- No system crashes or errors

### ⚠️ Warning Signs
- Upload times > 2 minutes
- Dashboard shows static/demo data after upload
- Analysis returns "No data available" errors
- Charts remain empty after data upload
- Browser becomes unresponsive

### ❌ Failing Tests
- File uploads fail or timeout
- System crashes during processing
- Data corruption or loss
- Analysis functions don't work
- Reports contain no real data

## Performance Benchmarks

### Target Performance
- **Small files** (< 1MB): < 10 seconds
- **Medium files** (1-5MB): < 30 seconds  
- **Large files** (5-20MB): < 2 minutes
- **Dashboard refresh**: < 3 seconds
- **Analysis execution**: < 15 seconds
- **Report generation**: < 30 seconds

Use these test files to thoroughly validate your EcoGenomics Suite implementation! 🧪🔬