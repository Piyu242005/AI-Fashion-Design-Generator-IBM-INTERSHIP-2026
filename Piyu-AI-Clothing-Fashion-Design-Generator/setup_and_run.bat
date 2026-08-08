@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo  Piyu AI Clothing Fashion Design Generator - Setup Script
echo ============================================================
echo.

:: ── Step 1: Check if Python 3.11 is already available ──────────────────
echo [1/6] Checking for Python 3.11...

py -3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ✓ Python 3.11 found via py launcher.
    set PYTHON_CMD=py -3.11
    goto :found_python
)

python3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ✓ Python 3.11 found as python3.11.
    set PYTHON_CMD=python3.11
    goto :found_python
)

:: Check common install locations
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    echo   ✓ Python 3.11 found in AppData.
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
    goto :found_python
)

if exist "C:\Python311\python.exe" (
    echo   ✓ Python 3.11 found at C:\Python311.
    set PYTHON_CMD=C:\Python311\python.exe
    goto :found_python
)

:: ── Python 3.11 not found — install it ─────────────────────────────────
echo   ! Python 3.11 not found. Installing via winget...
echo.
winget install --id Python.Python.3.11 --source winget --accept-source-agreements --accept-package-agreements --silent
if %ERRORLEVEL% NEQ 0 (
    echo   ✗ winget install failed. Please install Python 3.11 manually from:
    echo     https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

:: Refresh PATH
call refreshenv >nul 2>&1

:: Try again after install
py -3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3.11
    goto :found_python
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
    goto :found_python
)

echo   ✗ Could not locate Python 3.11 after install.
echo     Please restart this script or add Python 3.11 to PATH manually.
pause
exit /b 1

:found_python
echo   Python command: %PYTHON_CMD%
echo.

:: ── Step 2: Create virtual environment ─────────────────────────────────
echo [2/6] Creating virtual environment '.venv311'...

if exist ".venv311\Scripts\activate.bat" (
    echo   ✓ Virtual environment already exists. Skipping creation.
) else (
    %PYTHON_CMD% -m venv .venv311
    if %ERRORLEVEL% NEQ 0 (
        echo   ✗ Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   ✓ Virtual environment created.
)
echo.

:: ── Step 3: Activate venv ───────────────────────────────────────────────
echo [3/6] Activating virtual environment...
call .venv311\Scripts\activate.bat
echo   ✓ Activated.
echo.

:: ── Step 4: Upgrade pip ─────────────────────────────────────────────────
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet
echo   ✓ pip upgraded.
echo.

:: ── Step 5: Install dependencies ───────────────────────────────────────
echo [5/6] Installing dependencies...
echo   Installing PyTorch 2.1.0 with CUDA 11.8 (GPU) ...
pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118 --quiet
if %ERRORLEVEL% NEQ 0 (
    echo   ! GPU install failed, trying CPU-only PyTorch...
    pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu --quiet
)
echo   Installing remaining requirements...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo   ! Some packages failed. Trying with --no-deps for known problematic ones...
    pip install basicsr==1.4.2 --no-deps --quiet
    pip install realesrgan==0.3.0 --no-deps --quiet
)
echo   ✓ Dependencies installed.
echo.

:: ── Step 6: Run Streamlit ───────────────────────────────────────────────
echo [6/6] Starting Streamlit app...
echo   URL: http://localhost:8501
echo.
streamlit run app.py
endlocal
