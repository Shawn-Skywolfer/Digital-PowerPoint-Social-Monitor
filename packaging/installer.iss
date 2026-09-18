; ============================================================
; 社媒监测洞察系统 · Windows 安装包脚本（Inno Setup 6）
; 编译："%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" installer.iss
; 产物：输出\社媒监测洞察系统-Setup-0.4.0.exe
; ============================================================
#define AppName "社媒监测洞察系统"
#define AppVersion "0.4.0"
#define AppPublisher "华为数字能源 Marketing"
#define AppExe "社媒监测洞察系统.exe"

[Setup]
; 固定 AppId：升级安装/卸载靠它识别，不要随意改
AppId={{B7E21A54-3C86-4F29-9D15-6E8A0C52F1D3}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
; 免管理员：装到当前用户目录，exe 旁边的 data/ 也可写
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=输出
OutputBaseFilename=社媒监测洞察系统-Setup-{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=110
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}
CloseApplications=force

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: checkedonce

[Files]
Source: "dist\社媒监测洞察系统\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "使用说明.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\使用说明"; Filename: "{app}\使用说明.txt"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "立即启动 {#AppName}"; Flags: postinstall nowait skipifsilent unchecked
