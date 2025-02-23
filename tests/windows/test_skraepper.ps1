# GUI test for Skraepper on Windows 11.
#
# IMPORTANT: DO NOT RUN ON DESKTOP.
# ONLY RUN IN VM (Runs fine in Windows Sandbox).
#
# Run script with:
# powershell -ExecutionPolicy Bypass
# or from src:
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force; irm https://raw.githubusercontent.com/tania-andersen/Skraepper/main/tests/windows/test_skraepper.ps1 | iex

# Step 1: Check if the OS is Windows 11
$osInfo = Get-ComputerInfo | Select-Object -ExpandProperty OsName
if (-Not ($osInfo -match "Windows 11")) {
    Write-Host "This test is designed to run on Windows 11 only. Exiting..."
    exit 1
}

# Step 2: Set the target directory
$targetDir = "$env:USERPROFILE\Documents\Skraepper"
Write-Host "Setting up the project in: $targetDir"

# Create the target directory if it doesn't exist
if (-Not (Test-Path -Path $targetDir)) {
    Write-Host "Creating directory: $targetDir"
    New-Item -ItemType Directory -Path $targetDir
}

# Change to the target directory
Set-Location -Path $targetDir

# Step 3: Download and install Python 3.13.2
Write-Host "Downloading Python 3.13.2..."
$pythonUrl = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe"
$pythonInstaller = "$targetDir\python-installer.exe"
Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller

Write-Host "Installing Python..."
Start-Process -Wait -FilePath $pythonInstaller -ArgumentList "/passive", "InstallAllUsers=1", "PrependPath=1"

# Step 4: Search for python.exe
Write-Host "Searching for python.exe..."
$pythonPath = Get-ChildItem -Path "C:\Users", "C:\Program Files", "C:\Program Files (x86)" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName

if (-Not $pythonPath) {
    Write-Host "Python installation failed or could not be located. Exiting..."
    exit 1
}
Write-Host "Python found at: $pythonPath"

# Step 5: Verify pip installation
Write-Host "Verifying pip installation..."
try {
    $pipVersion = & $pythonPath -m pip --version
    Write-Host "Pip version: $pipVersion"
} catch {
    Write-Host "Failed to verify pip installation. Exiting..."
    exit 1
}

# Step 6: Download the GitHub repository as a ZIP file
Write-Host "Downloading the GitHub repository as a ZIP file..."
$repoUrl = "https://github.com/tania-andersen/Skraepper/archive/refs/heads/main.zip"
$zipFile = "$targetDir\Skraepper.zip"
Invoke-WebRequest -Uri $repoUrl -OutFile $zipFile

# Step 7: Extract the ZIP file
Write-Host "Extracting the ZIP file..."
Expand-Archive -Path $zipFile -DestinationPath $targetDir -Force
Set-Location -Path "$targetDir\Skraepper-main"

# Step 8: Create a virtual environment in .venv
Write-Host "Creating a virtual environment in .venv..."
& $pythonPath -m venv .venv

# Step 9: Activate the virtual environment
Write-Host "Activating the virtual environment..."
$venvPythonPath = "$targetDir\Skraepper-main\.venv\Scripts\python.exe"
$venvPipPath = "$targetDir\Skraepper-main\.venv\Scripts\pip.exe"

# Step 10: Set Playwright to download browsers locally
Write-Host "Configuring Playwright to download browsers locally..."
$env:PLAYWRIGHT_BROWSERS_PATH=0

# Step 11: Install required packages from requirements.txt
Write-Host "Installing required packages..."
& $venvPythonPath -m pip install -r requirements.txt

# Step 12: Install only Chromium for Playwright
Write-Host "Installing Chromium for Playwright..."
& $venvPythonPath -m playwright install chromium

# Step 13: Install pyautogui and pyperclip
Write-Host "Installing pyautogui and pyperclip..."
& $venvPythonPath -m pip install pyautogui pyperclip

# Step 14: Run test_scraper_gui.py
Write-Host "Running tests..."
$env:TEST_SKRAEPPER = "1"
& $venvPythonPath tests\test_scraper_gui.py testscript .