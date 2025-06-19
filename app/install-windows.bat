@echo off
echo Installing EcoGenomics Suite on Windows...
echo.

echo Step 1: Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
echo.

echo Step 2: Installing core packages first...
pip install Django==4.2.7
pip install python-dotenv==1.0.0
pip install whitenoise==6.5.0
echo.

echo Step 3: Installing data processing packages...
pip install pandas
pip install openpyxl
echo.

echo Step 4: Attempting to install scientific packages...
echo (These might fail on some Windows systems - that's OK for basic functionality)
pip install numpy || echo "NumPy installation failed - you can try installing it manually later"
pip install scipy || echo "SciPy installation failed - statistical analysis will be limited"
pip install scikit-learn || echo "Scikit-learn installation failed - advanced analysis will be limited"
pip install matplotlib || echo "Matplotlib installation failed - some visualizations will be limited"
pip install seaborn || echo "Seaborn installation failed - statistical plots will be limited"
pip install plotly || echo "Plotly installation failed - interactive charts will be limited"
echo.

echo Step 5: Installing remaining packages...
pip install Pillow || echo "Pillow installation failed - image processing will be limited"
echo.

echo Installation complete!
echo.
echo If some packages failed to install, you can:
echo 1. Try installing them individually: pip install package-name
echo 2. Use conda instead: conda install package-name
echo 3. Download pre-compiled wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/
echo.
echo The basic Django application should work even if some scientific packages failed.
pause