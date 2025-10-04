# Auto-download portable tools for 4Paws Agent
# Run this script in PowerShell

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  4Paws Agent - Auto Download Tools" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$ProgressPreference = 'SilentlyContinue'  # Faster downloads

# Directories
$toolsDir = "tools"
$nodeDir = "$toolsDir\node"
$mariadbDir = "$toolsDir\mariadb"

# Node.js Configuration
$nodeVersion = "v20.11.0"
$nodeUrl = "https://nodejs.org/dist/$nodeVersion/node-$nodeVersion-win-x64.zip"
$nodeZip = "node-portable.zip"

# MariaDB Configuration
$mariadbVersion = "11.4.2"
$mariadbUrl = "https://archive.mariadb.org/mariadb-$mariadbVersion/winx64-packages/mariadb-$mariadbVersion-winx64.zip"
$mariadbZip = "mariadb-portable.zip"

# ========================================
# Function: Download File
# ========================================
function Download-File {
    param(
        [string]$Url,
        [string]$Output
    )
    
    Write-Host "📥 Downloading: $Url" -ForegroundColor Yellow
    Write-Host "   Saving to: $Output" -ForegroundColor Gray
    
    try {
        Invoke-WebRequest -Uri $Url -OutFile $Output -UseBasicParsing
        Write-Host "✅ Download completed!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Download failed: $_" -ForegroundColor Red
        return $false
    }
}

# ========================================
# Function: Extract ZIP
# ========================================
function Extract-Archive {
    param(
        [string]$ZipFile,
        [string]$Destination
    )
    
    Write-Host "📂 Extracting: $ZipFile" -ForegroundColor Yellow
    Write-Host "   To: $Destination" -ForegroundColor Gray
    
    try {
        $tempDir = "$Destination-temp"
        Expand-Archive -Path $ZipFile -DestinationPath $tempDir -Force
        
        # Find the extracted folder
        $extractedFolder = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1
        
        # Move contents to destination
        if ($extractedFolder) {
            Move-Item -Path "$($extractedFolder.FullName)\*" -Destination $Destination -Force
            Remove-Item -Path $tempDir -Recurse -Force
        }
        
        Write-Host "✅ Extraction completed!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Extraction failed: $_" -ForegroundColor Red
        return $false
    }
}

# ========================================
# Download Node.js
# ========================================
Write-Host ""
Write-Host "1️⃣  Downloading Node.js $nodeVersion..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray

if (Test-Path "$nodeDir\node.exe") {
    Write-Host "✅ Node.js already exists, skipping..." -ForegroundColor Green
} else {
    if (Download-File -Url $nodeUrl -Output $nodeZip) {
        Extract-Archive -ZipFile $nodeZip -Destination $nodeDir
        Remove-Item -Path $nodeZip -Force
        
        if (Test-Path "$nodeDir\node.exe") {
            Write-Host "✅ Node.js installed successfully!" -ForegroundColor Green
            
            # Test Node.js
            $nodeVersion = & "$nodeDir\node.exe" --version
            Write-Host "   Version: $nodeVersion" -ForegroundColor Gray
        } else {
            Write-Host "❌ Node.js installation failed!" -ForegroundColor Red
        }
    }
}

# ========================================
# Download MariaDB
# ========================================
Write-Host ""
Write-Host "2️⃣  Downloading MariaDB $mariadbVersion..." -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray

if (Test-Path "$mariadbDir\bin\mysqld.exe") {
    Write-Host "✅ MariaDB already exists, skipping..." -ForegroundColor Green
} else {
    Write-Host "⚠️  MariaDB auto-download not available" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Manual download required:" -ForegroundColor Yellow
    Write-Host "   1. Visit: https://mariadb.org/download/" -ForegroundColor Gray
    Write-Host "   2. Select: Windows 64-bit ZIP" -ForegroundColor Gray
    Write-Host "   3. Version: 11.4 LTS" -ForegroundColor Gray
    Write-Host "   4. Extract to: $mariadbDir" -ForegroundColor Gray
    Write-Host ""
}

# ========================================
# Summary
# ========================================
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Installation Summary" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Node.js:" -ForegroundColor White
if (Test-Path "$nodeDir\node.exe") {
    Write-Host "  ✅ Installed at: $nodeDir\node.exe" -ForegroundColor Green
} else {
    Write-Host "  ❌ Not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "MariaDB:" -ForegroundColor White
if (Test-Path "$mariadbDir\bin\mysqld.exe") {
    Write-Host "  ✅ Installed at: $mariadbDir\bin\mysqld.exe" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Manual installation required" -ForegroundColor Yellow
    Write-Host "     Download: https://mariadb.org/download/" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. If MariaDB not installed, download manually" -ForegroundColor Gray
Write-Host "   2. Run: python agent.py setup" -ForegroundColor Gray
Write-Host "   3. Run: python agent.py install all" -ForegroundColor Gray
Write-Host "   4. Run: python agent.py start" -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$ProgressPreference = 'Continue'

