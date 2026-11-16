@echo off
setlocal enabledelayedexpansion
title Stealth Stream Auto-Clipper

set "PYTHON_EXE=C:\Users\Vrushubh\AppData\Local\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at %PYTHON_EXE%
    pause
    exit /b 1
)

cd /d "%~dp0"

if "%~1"=="" (
    echo ============================================================
    echo       STEALTH STREAM AUTO-CLIPPER (100%% FREE ^& LOCAL)
    echo ============================================================
    echo.
    set /p PLATFORM="Enter platform (twitch / youtube) [default: twitch]: "
    if "!PLATFORM!"=="" set "PLATFORM=twitch"
    
    set /p TARGET="Enter streamer channel or handle (e.g., kaicenat or @IShowSpeed): "
    if "!TARGET!"=="" (
        echo [!] Channel cannot be empty.
        pause
        exit /b 1
    )
    
    set /p VERT="Convert to 9:16 Vertical for Reels/Shorts? (y/n) [default: y]: "
    if "!VERT!"=="" set "VERT=y"
    
    set "EXTRA_FLAGS="
    if /i "!VERT!"=="y" set "EXTRA_FLAGS=--vertical"

    echo.
    echo [*] Starting Auto-Clipper for !TARGET! on !PLATFORM!...
    echo.
    "%PYTHON_EXE%" clipper.py --platform !PLATFORM! --target "!TARGET!" !EXTRA_FLAGS!
) else (
    set "PLATFORM=%~1"
    set "TARGET=%~2"
    shift
    shift
    "%PYTHON_EXE%" clipper.py --platform %PLATFORM% --target "%TARGET%" %*
)

pause
