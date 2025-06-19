# Windows Installation Guide

## 🚨 Windows-Specific Issues

The error you're seeing is common on Windows when trying to install scientific Python packages that need to be compiled from source.

## 🔧 Solutions (Try in Order)

### **Option 1: Use Pre-compiled Wheels (Recommended)**

```bash
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install packages individually to avoid conflicts
pip install Django==4.2.7
pip install python-dotenv==1.0.0
pip install whitenoise==6.5.0
pip install pandas
pip install openpyxl
```

### **Option 2: Use the Windows Batch Script**

```bash
# Run the automated installer
install-windows.bat
```

### **Option 3: Install Minimal Requirements**

```bash
# Install only essential packages
pip install -r requirements-windows-minimal.txt
```

### **Option 4: Use Conda (Highly Recommended for Windows)**

```bash
# Install Miniconda first: https://docs.conda.io/en/latest/miniconda.html
conda create -n ecogenomics python=3.11
conda activate ecogenomics
conda install django pandas numpy scipy scikit-learn matplotlib seaborn plotly
pip install python-dotenv whitenoise openpyxl
```

### **Option 5: Download Pre-compiled Wheels**

If packages still fail, download pre-compiled wheels from:
- https://www.lfd.uci.edu/~gohlke/pythonlibs/

Example:
```bash
# Download numpy wheel for your Python version and install
pip install numpy-1.24.3-cp311-cp311-win_amd64.whl
```

## 🎯 What You Need for Basic Functionality

### **Essential (Must Have):**
- ✅ Django
- ✅ python-dotenv
- ✅ whitenoise
- ✅ pandas
- ✅ openpyxl

### **Important (Nice to Have):**
- 📊 numpy (for numerical operations)
- 📈 matplotlib (for basic charts)
- 📋 plotly (for interactive charts)

### **Advanced (Optional):**
- 🔬 scipy (for statistical tests)
- 🤖 scikit-learn (for machine learning)
- 📊 seaborn (for statistical plots)

## 🚀 Quick Start (Minimal Setup)

```bash
# 1. Install minimal requirements
pip install Django python-dotenv whitenoise pandas openpyxl

# 2. Run migrations
cd app
python manage.py migrate

# 3. Create superuser (optional)
python manage.py createsuperuser

# 4. Start server
python manage.py runserver
```

## 🔍 Troubleshooting

### **Error: "Compiler cl cannot compile programs"**
- **Cause**: Missing Microsoft Visual C++ Build Tools
- **Solution**: Install Visual Studio Build Tools or use pre-compiled wheels

### **Error: "Microsoft Visual C++ 14.0 is required"**
- **Solution**: Install Microsoft C++ Build Tools from:
  https://visualstudio.microsoft.com/visual-cpp-build-tools/

### **Error: "Failed building wheel for [package]"**
- **Solution**: Use conda or download pre-compiled wheels

## 💡 Pro Tips for Windows

1. **Use Conda**: Much easier for scientific packages on Windows
2. **Virtual Environment**: Always use a virtual environment
3. **Update pip**: Always upgrade pip before installing packages
4. **One by one**: Install packages individually if batch install fails
5. **Check architecture**: Make sure you're using 64-bit Python for better package support

## 🧪 Test Your Installation

```python
# Test basic functionality
python -c "import django; print('Django:', django.VERSION)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)" 
```

The application will work with just Django, pandas, and openpyxl for basic file upload and processing functionality!