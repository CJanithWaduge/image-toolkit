@echo off
REM Build script for ZedgeMetaGenerator single-directory .exe
REM Run from project root:  .\build_exe.bat

setlocal enabledelayedexpansion

echo ============================================
echo  Building ZedgeMetaGenerator .exe
echo ============================================
echo.

REM Verify we're in the project root
if not exist "main.py" (
    echo ERROR: Run this from the project root (where main.py is).
    exit /b 1
)

REM Clean previous build
if exist "dist\ZedgeMetaGenerator" rmdir /s /q "dist\ZedgeMetaGenerator"
if exist "build" rmdir /s /q "build"

REM Run PyInstaller
echo ^> pyinstaller build_exe.spec --clean --noconfirm
call pyinstaller build_exe.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo BUILD FAILED ^(exit code %errorlevel%^)
    exit /b %errorlevel%
)

echo.
echo ============================================
echo  Build complete!
echo  Output: dist\ZedgeMetaGenerator\ZedgeMetaGenerator.exe
echo ============================================
echo.
echo NOTES:
echo  - First run will download BLIP model ^(~944 MB^) from HuggingFace
echo  - Qwen GGUF model ^(~1 GB^) is bundled
echo  - Upscayl models ^(~195 MB^) are bundled
echo  - Internet required on first run for BLIP download
echo.
echo To make fully offline, pre-download BLIP and copy cache:
echo   python -c "from transformers import BlipProcessor, BlipForConditionalGeneration; BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')"
