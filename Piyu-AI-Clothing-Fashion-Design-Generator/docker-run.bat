@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  docker-run.bat
::  Piyu AI Clothing Fashion Design Generator — Docker Helper
::  Windows PowerShell / CMD launcher
:: ============================================================

title Piyu AI Fashion — Docker

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   Piyu AI Clothing Fashion Design Generator          ║
echo  ║   Docker Launcher                                    ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Check Docker is running ───────────────────────────────────────────────
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Docker is not running or not installed.
    echo          Please start Docker Desktop and try again.
    echo          Download: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)
echo  [✓] Docker is running.

:: ── Check .env file ───────────────────────────────────────────────────────
if not exist ".env" (
    echo.
    echo  [WARN] .env file not found. Copying from .env.example ...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo  [✓] .env created from .env.example
        echo  [!] IMPORTANT: Edit .env and set your HF_TOKEN before continuing.
        echo      Get your token at: https://huggingface.co/settings/tokens
        echo.
        pause
    ) else (
        echo  [ERROR] .env.example not found. Cannot continue.
        pause
        exit /b 1
    )
)

:: ── Check .streamlit/secrets.toml ────────────────────────────────────────
if not exist ".streamlit\secrets.toml" (
    if exist ".streamlit\secrets.toml.example" (
        copy ".streamlit\secrets.toml.example" ".streamlit\secrets.toml" >nul
        echo  [✓] .streamlit\secrets.toml created from example.
    )
)

:: ── Create output directories ─────────────────────────────────────────────
if not exist "results"           mkdir results
if not exist "reference_images"  mkdir reference_images
echo  [✓] Output directories ready.

:: ── GPU detection ─────────────────────────────────────────────────────────
set USE_GPU=0
nvidia-smi >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set USE_GPU=1
    echo  [✓] NVIDIA GPU detected — GPU mode enabled.
) else (
    echo  [!] No NVIDIA GPU detected — CPU-only mode.
    echo      Generation will be significantly slower.
)

:: ── Select action ─────────────────────────────────────────────────────────
echo.
echo  Select an action:
echo    1. Build image only
echo    2. Build and run  (recommended first time)
echo    3. Run existing image  (skip build)
echo    4. Stop running container
echo    5. View logs
echo    6. Shell into container
echo    7. Remove everything (image + volumes)
echo    8. Exit
echo.
set /p CHOICE="  Enter choice [1-8]: "

if "%CHOICE%"=="1" goto :build_only
if "%CHOICE%"=="2" goto :build_run
if "%CHOICE%"=="3" goto :run_only
if "%CHOICE%"=="4" goto :stop
if "%CHOICE%"=="5" goto :logs
if "%CHOICE%"=="6" goto :shell
if "%CHOICE%"=="7" goto :clean
if "%CHOICE%"=="8" goto :end

echo  [ERROR] Invalid choice.
pause
exit /b 1

:: ── BUILD ONLY ────────────────────────────────────────────────────────────
:build_only
echo.
echo  Building Docker image (this takes 10-20 minutes first time)...
docker build -t piyu-fashion:latest .
if %ERRORLEVEL% EQU 0 (
    echo.
    echo  [✓] Image built successfully: piyu-fashion:latest
) else (
    echo  [ERROR] Build failed. Check output above.
)
pause
goto :end

:: ── BUILD AND RUN ─────────────────────────────────────────────────────────
:build_run
echo.
echo  Building Docker image...
docker build -t piyu-fashion:latest .
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Build failed. Check output above.
    pause
    goto :end
)
echo  [✓] Image built.
goto :run_core

:: ── RUN ONLY ──────────────────────────────────────────────────────────────
:run_only
docker image inspect piyu-fashion:latest >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Image piyu-fashion:latest not found.
    echo          Run option 2 first to build the image.
    pause
    goto :end
)
goto :run_core

:: ── CORE RUN LOGIC ────────────────────────────────────────────────────────
:run_core
echo.
echo  Stopping any existing container...
docker stop piyu-fashion-gpu >nul 2>&1
docker stop piyu-fashion-cpu >nul 2>&1
docker rm   piyu-fashion-gpu >nul 2>&1
docker rm   piyu-fashion-cpu >nul 2>&1

if %USE_GPU%==1 (
    echo  Starting container with GPU support...
    docker compose --profile gpu up -d
    set CONTAINER=piyu-fashion-gpu
) else (
    echo  Starting container in CPU-only mode...
    docker compose --profile cpu up -d
    set CONTAINER=piyu-fashion-cpu
)

if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Failed to start container.
    pause
    goto :end
)

echo.
echo  [✓] Container started!
echo.
echo  ┌─────────────────────────────────────────────────────┐
echo  │  App URL : http://localhost:8501                    │
echo  │  Logs    : docker logs -f %CONTAINER%              │
echo  │  Stop    : docker stop %CONTAINER%                 │
echo  └─────────────────────────────────────────────────────┘
echo.
echo  The app will be available in ~60-120 seconds (model loading).
echo  Opening browser...
timeout /t 5 /nobreak >nul
start "" http://localhost:8501
pause
goto :end

:: ── STOP ──────────────────────────────────────────────────────────────────
:stop
echo.
docker stop piyu-fashion-gpu piyu-fashion-cpu >nul 2>&1
docker rm   piyu-fashion-gpu piyu-fashion-cpu >nul 2>&1
echo  [✓] Containers stopped and removed.
pause
goto :end

:: ── LOGS ──────────────────────────────────────────────────────────────────
:logs
echo.
echo  Showing logs (Ctrl+C to exit)...
docker logs -f piyu-fashion-gpu 2>nul || docker logs -f piyu-fashion-cpu 2>nul || (
    echo  [ERROR] No running container found.
)
pause
goto :end

:: ── SHELL ─────────────────────────────────────────────────────────────────
:shell
echo.
docker exec -it piyu-fashion-gpu /bin/bash 2>nul || docker exec -it piyu-fashion-cpu /bin/bash 2>nul || (
    echo  [ERROR] No running container found.
    echo          Start the container first (option 2 or 3).
)
pause
goto :end

:: ── CLEAN ─────────────────────────────────────────────────────────────────
:clean
echo.
echo  [WARN] This will remove:
echo    - Container: piyu-fashion-gpu and piyu-fashion-cpu
echo    - Image:     piyu-fashion:latest
echo    - Volumes:   piyu_fashion_model_weights, piyu_fashion_hf_cache
echo.
echo  Model weights will need to be re-downloaded (~40 GB).
set /p CONFIRM="  Type YES to confirm: "
if /i not "%CONFIRM%"=="YES" (
    echo  Cancelled.
    pause
    goto :end
)
docker stop piyu-fashion-gpu piyu-fashion-cpu >nul 2>&1
docker rm   piyu-fashion-gpu piyu-fashion-cpu >nul 2>&1
docker rmi  piyu-fashion:latest               >nul 2>&1
docker volume rm piyu_fashion_model_weights piyu_fashion_hf_cache >nul 2>&1
echo  [✓] Cleanup complete.
pause
goto :end

:end
endlocal
