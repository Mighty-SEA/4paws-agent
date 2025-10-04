; 4Paws Agent NSIS Installer Script
; Includes portable Node.js and MariaDB

;--------------------------------
; Includes

!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; General

; Name and file
Name "4Paws Agent"
OutFile "..\dist\4PawsAgent-Setup.exe"

; Default installation folder
InstallDir "$PROGRAMFILES64\4PawsAgent"

; Get installation folder from registry if available
InstallDirRegKey HKLM "Software\4PawsAgent" "InstallDir"

; Request admin privileges
RequestExecutionLevel admin

; Compression
SetCompressor /SOLID lzma
SetCompressorDictSize 64

;--------------------------------
; Variables

Var StartMenuFolder

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

;--------------------------------
; Pages

!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY

; Start Menu Folder Page Configuration
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM" 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\4PawsAgent" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"

!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

!insertmacro MUI_PAGE_INSTFILES

; Finish page options
!define MUI_FINISHPAGE_RUN "$INSTDIR\4PawsAgent.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch 4Paws Agent"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Show README"

!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "4Paws Agent"
VIAddVersionKey "CompanyName" "4Paws"
VIAddVersionKey "FileDescription" "4Paws Deployment Agent Installer"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIAddVersionKey "ProductVersion" "1.0.0.0"
VIAddVersionKey "LegalCopyright" "© 2025 4Paws"

;--------------------------------
; Installer Sections

Section "4Paws Agent" SecMain

  SetOutPath "$INSTDIR"
  
  ; Display installing message
  DetailPrint "Installing 4Paws Agent..."
  
  ; Copy main executable
  File "..\dist\4PawsAgent.exe"
  File "README.txt"
  File "LICENSE.txt"
  
  ; Create folders
  CreateDirectory "$INSTDIR\tools"
  CreateDirectory "$INSTDIR\tools\node"
  CreateDirectory "$INSTDIR\tools\mariadb"
  CreateDirectory "$INSTDIR\apps"
  CreateDirectory "$INSTDIR\data"
  CreateDirectory "$INSTDIR\logs"
  
  ; Copy ZIP files temporarily
  File "/oname=node-temp.zip" "node-temp.zip"
  File "/oname=mariadb-temp.zip" "mariadb-temp.zip"
  
  ; Extract Node.js using PowerShell
  DetailPrint "Extracting Node.js portable (this may take a minute)..."
  nsExec::ExecToLog 'powershell -Command "Expand-Archive -Path \"$INSTDIR\\node-temp.zip\" -DestinationPath \"$INSTDIR\\tools\" -Force"'
  Pop $0
  DetailPrint "Node.js extraction completed"
  
  ; Move node files from nested folder to tools/node
  Rename "$INSTDIR\tools\node-v22.20.0-win-x64" "$INSTDIR\tools\node"
  
  ; Extract MariaDB using PowerShell
  DetailPrint "Extracting MariaDB portable (this may take 2-3 minutes)..."
  nsExec::ExecToLog 'powershell -Command "Expand-Archive -Path \"$INSTDIR\\mariadb-temp.zip\" -DestinationPath \"$INSTDIR\\tools\" -Force"'
  Pop $0
  DetailPrint "MariaDB extraction completed"
  
  ; Move mariadb files from nested folder to tools/mariadb
  Rename "$INSTDIR\tools\mariadb-12.0.2-winx64" "$INSTDIR\tools\mariadb"
  
  ; Clean up temp files
  Delete "$INSTDIR\node-temp.zip"
  Delete "$INSTDIR\mariadb-temp.zip"
  
  ; Initialize MariaDB
  DetailPrint "Initializing MariaDB database..."
  CreateDirectory "$INSTDIR\data\mariadb"
  nsExec::ExecToLog '"$INSTDIR\tools\mariadb\bin\mariadb-install-db.exe" --datadir="$INSTDIR\data\mariadb"'
  
  ; Store installation folder
  WriteRegStr HKLM "Software\4PawsAgent" "InstallDir" $INSTDIR
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                   "DisplayName" "4Paws Agent"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                   "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                   "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                   "DisplayIcon" "$INSTDIR\4PawsAgent.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                   "Publisher" "4Paws"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                   "DisplayVersion" "1.0.0"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                     "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent" \
                     "NoRepair" 1
  
  ; Create Start Menu shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\4Paws Agent.lnk" "$INSTDIR\4PawsAgent.exe"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\README.lnk" "$INSTDIR\README.txt"
    
  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

;--------------------------------
; Uninstaller Section

Section "Uninstall"

  ; Stop any running services
  DetailPrint "Stopping services..."
  nsExec::ExecToLog 'taskkill /F /IM 4PawsAgent.exe'
  nsExec::ExecToLog 'taskkill /F /IM node.exe'
  nsExec::ExecToLog 'taskkill /F /IM mysqld.exe'
  Sleep 2000
  
  ; Delete files
  Delete "$INSTDIR\4PawsAgent.exe"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Delete folders
  RMDir /r "$INSTDIR\tools"
  RMDir /r "$INSTDIR\apps"
  RMDir /r "$INSTDIR\logs"
  
  ; Ask before deleting database
  MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to delete the database files? (This will remove all your data)" IDYES DeleteDB IDNO KeepDB
  DeleteDB:
    RMDir /r "$INSTDIR\data"
  KeepDB:
  
  ; Try to delete install directory
  RMDir "$INSTDIR"
  
  ; Remove Start Menu shortcuts
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$SMPROGRAMS\$StartMenuFolder\4Paws Agent.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\README.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\4PawsAgent"
  DeleteRegKey HKLM "Software\4PawsAgent"

SectionEnd

;--------------------------------
; Installer Functions

Function .onInit
  
  ; Check if already installed
  ReadRegStr $0 HKLM "Software\4PawsAgent" "InstallDir"
  StrCmp $0 "" NotInstalled
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
      "4Paws Agent is already installed at $0.$\n$\nClick OK to uninstall the previous version or Cancel to exit." \
      IDOK Uninstall
    Abort
  Uninstall:
    ExecWait '"$0\Uninstall.exe" /S _?=$0'
    Sleep 2000
  NotInstalled:
  
FunctionEnd

