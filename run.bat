@echo off
setlocal
cd /d "%~dp0"

echo ==^> python-multiprocessing-rng-state-lab
echo.

echo [1/3] py_compile...
python -m py_compile run_lab.py test_lab.py
if errorlevel 1 exit /b %errorlevel%
echo ok
echo.

echo [2/3] run_lab.py...
python run_lab.py
if errorlevel 1 exit /b %errorlevel%
echo.

echo [3/3] unittest...
python -m unittest -v
if errorlevel 1 exit /b %errorlevel%
