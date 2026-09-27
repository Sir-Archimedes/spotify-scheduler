@echo off
setlocal

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run python -m venv .venv and install requirements first.
    pause
    exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

".venv\Scripts\python.exe" -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo PyInstaller not found in .venv. Installing...
    ".venv\Scripts\python.exe" -m pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --onefile --windowed --icon "icon.ico" --name "spotify-scheduler" --add-data "icon.ico;." --version-file "version.txt" "spotifyscheduler.py"
pause
