; MemDoc Inno Setup Installer Script
; Builds a proper Windows installer with shortcuts, uninstaller, and German UI
;
; Usage: iscc installer.iss /DMyAppVersion=1.2.0
; The version can be passed from CI or defaults to 0.0.0

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

#define MyAppName "MemDoc"
#define MyAppPublisher "MemDoc"
#define MyAppExeName "MemDoc.exe"
#define MyAppURL "https://github.com/swahed/memdoc"
#define MyAppMutex "MemDocAppMutex"

[Setup]
AppId={{B5F7E8A2-3C4D-4E6F-9A1B-2D3E4F5A6B7C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=MemDoc-Setup
OutputDir=dist
Compression=lzma2
SolidCompression=yes
SetupIconFile=static\images\memdoc.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=admin
CloseApplications=yes
CloseApplicationsFilter=*.exe
RestartApplications=yes
AppMutex={#MyAppMutex}
VersionInfoVersion={#MyAppVersion}.0

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Files]
Source: "dist\MemDoc.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} starten"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill"; Parameters: "/IM {#MyAppExeName} /F"; Flags: runhidden waituntilterminated; RunOnceId: "KillMemDoc"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssInstall then
  begin
    Exec('taskkill', '/IM MemDoc.exe /F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
