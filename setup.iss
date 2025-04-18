[Setup]
AppName=FastAPI Server
AppVersion=1.0
DefaultDirName={commonappdata}\FastAPIServer
DefaultGroupName=FastAPI Server
UninstallDisplayIcon={app}\FastAPI.ico
OutputDir=.
OutputBaseFilename=FastAPI_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "server\*"; DestDir: "{app}"; Flags: recursesubdirs

[Run]
Filename: "{cmd}"; Parameters: "/C python -m pip install -r ""{app}\requirements.txt"""; Flags: runhidden
Filename: "{cmd}"; Parameters: "/C cd /D ""{app}"" && python -m uvicorn main:app --host 0.0.0.0 --port 8563"; Flags: runhidden

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "FastAPIServer"; ValueData: """{cmd}"" /C cd /D ""{app}"" && python -m uvicorn main:app --host 0.0.0.0 --port 8563"; Flags: uninsdeletevalue
