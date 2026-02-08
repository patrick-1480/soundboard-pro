; Soundboard Pro Installer Script
; Requires Inno Setup 6: https://jrsoftware.org/isdl.php

#define MyAppName "Soundboard Pro"
#define MyAppVersion "2.1.2"
#define MyAppPublisher "Patrick M."
#define MyAppURL "https://github.com/patrick-1480/Soundboard-Pro"
#define MyAppExeName "Soundboard Pro.exe"

[Setup]
AppId={{32dc4a92-c58f-4100-b517-3de55cc274cc}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer_output
OutputBaseFilename=SoundboardPro_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "sounds\*"; DestDir: "{app}\sounds"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  VBCablePage: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  // Create custom page for VB-Audio Cable info
  VBCablePage := CreateInputOptionPage(wpWelcome,
    'VB-Audio Cable Required', 
    'This application requires VB-Audio Virtual Cable to function',
    'Soundboard Pro uses VB-Audio Cable to route audio. If you don''t have it installed:' + #13#10#13#10 +
    '1. Download from https://vb-audio.com/Cable/' + #13#10 +
    '2. Run the installer' + #13#10 +
    '3. Restart your computer' + #13#10 +
    '4. Then run Soundboard Pro' + #13#10#13#10 +
    'Do you want to continue with the installation?',
    False, False);
  VBCablePage.Add('I understand and will install VB-Audio Cable');
  VBCablePage.Add('I already have VB-Audio Cable installed');
  VBCablePage.Values[1] := True;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = VBCablePage.ID then
  begin
    if not (VBCablePage.Values[0] or VBCablePage.Values[1]) then
    begin
      MsgBox('Please select an option to continue.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  UninstallExe: String;
begin
  // Check if previous version is installed
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{12345678-1234-1234-1234-123456789ABC}_is1', 
    'UninstallString', UninstallExe) then
  begin
    if MsgBox('A previous version of Soundboard Pro is installed. Do you want to uninstall it first?', 
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(RemoveQuotes(UninstallExe), '/SILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
  Result := True;
end;
