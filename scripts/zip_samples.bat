@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" (
    echo Usage: %~nx0 sample_list samples_directory [output_directory] [seven_zip_executable]
    exit /b 1
)
if "%~2"=="" (
    echo Usage: %~nx0 sample_list samples_directory [output_directory] [seven_zip_executable]
    exit /b 1
)
set "sampleList=%~f1"
set "sampleDir=%~f2"
set "outputDir=%~dp0..\agent\compressed\batch"
set "sevenZipPath=C:\Program Files\7-Zip\7z.exe"
if not "%~3"=="" set "outputDir=%~f3"
if not "%~4"=="" set "sevenZipPath=%~f4"

if not exist "%sampleList%" (
    echo Sample list not found: "%sampleList%"
    exit /b 1
)
if not exist "%sampleDir%\" (
    echo Sample directory not found: "%sampleDir%"
    exit /b 1
)
if not exist "%sevenZipPath%" (
    echo 7-Zip executable not found: "%sevenZipPath%"
    exit /b 1
)
if not exist "%outputDir%\" mkdir "%outputDir%"
if errorlevel 1 exit /b 1

set "hadErrors=0"
set "processed=0"
for /f "usebackq delims= eol=|" %%A in ("%sampleList%") do (
    set "processed=1"
    if exist "%sampleDir%\%%A.exe" (
        echo Compressing: "%sampleDir%\%%A.exe"
        "%sevenZipPath%" a -tzip -y "%outputDir%\%%A.zip" "%sampleDir%\%%A.exe"
        if errorlevel 1 (
            echo Compression failed for: "%%A.exe"
            set "hadErrors=1"
        )
    ) else (
        echo Sample not found: "%%A.exe"
        set "hadErrors=1"
    )
)
if "%processed%"=="0" (
    echo Sample list is empty.
    exit /b 1
)
exit /b %hadErrors%
