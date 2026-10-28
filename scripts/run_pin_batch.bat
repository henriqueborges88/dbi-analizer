@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" (
    echo Usage: %~nx0 samples_directory [pin_executable] [pintool_dll] [output_directory]
    exit /b 1
)
set "inputDir=%~f1"
set "pinPath=%~dp0..\agent\tools\pin-3.28-msvc-windows\intel64\bin\pin.exe"
set "dllPath=%~dp0..\agent\tools\pin-3.28-msvc-windows\tools\obj-intel64\calltrace.dll"
set "outputDir=%~dp0..\agent\out\pin-batch"
if not "%~2"=="" set "pinPath=%~f2"
if not "%~3"=="" set "dllPath=%~f3"
if not "%~4"=="" set "outputDir=%~f4"

if not exist "%inputDir%\" (
    echo Input directory not found: "%inputDir%"
    exit /b 1
)
if not exist "%pinPath%" (
    echo Pin executable not found: "%pinPath%"
    exit /b 1
)
if not exist "%dllPath%" (
    echo Pintool DLL not found: "%dllPath%"
    exit /b 1
)
if not exist "%outputDir%\" mkdir "%outputDir%"
if errorlevel 1 exit /b 1

set "hadErrors=0"
set "processed=0"
for %%F in ("%inputDir%\*.exe") do (
    if exist "%%~fF" if not exist "%%~fF\" (
        set "processed=1"
        echo Instrumenting: "%%~fF"
        "%pinPath%" -t "%dllPath%" -o "%outputDir%\%%~nF.txt" -- "%%~fF"
        if errorlevel 1 (
            echo Pin failed for: "%%~fF"
            set "hadErrors=1"
        )
    )
)
if "%processed%"=="0" (
    echo No .exe files found.
    exit /b 1
)
exit /b %hadErrors%
