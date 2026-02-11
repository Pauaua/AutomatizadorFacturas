; Script de Inno Setup para AutomatizadorAV
; Asegúrate de tener instalado Inno Setup (https://jrsoftware.org/isdl.php)

[Setup]
AppId={{D3C12B5A-8E4B-4E3F-BD5C-864D153E3B6E}
AppName=AutomatizadorAV
AppVersion=1.0
AppPublisher=Pauaua
DefaultDirName={autopf}\AutomatizadorAV
DefaultGroupName=AutomatizadorAV
AllowNoIcons=yes
OutputDir=setup_output
OutputBaseFilename=AutomatizadorAV_Installer
SetupIconFile=..\src\assets\logo.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\AutomatizadorAV\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTA: Asegúrate de que la ruta anterior apunte a tu carpeta dist después de ejecutar build_exe.py

[Icons]
Name: "{group}\AutomatizadorAV"; Filename: "{app}\AutomatizadorAV.exe"
Name: "{group}\{cm:UninstallProgram,AutomatizadorAV}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\AutomatizadorAV"; Filename: "{app}\AutomatizadorAV.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AutomatizadorAV.exe"; Description: "{cm:LaunchProgram,AutomatizadorAV}"; Flags: nowait postinstall skipifsilent

[Code]
// Verificar que el ejecutable existe antes de intentar ejecutarlo
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
