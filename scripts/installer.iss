; ============================================
; TCL表格比对系统 - Inno Setup 安装脚本
; ============================================
; 使用方法（从项目根目录运行）:
;   1. 先运行 PyInstaller 打包生成 dist\TCL表格比对_Win7\ 目录
;   2. 将 vc_redist.x64.exe 放到 resources\ 目录（从微软官网下载）
;   3. 编译命令:
;      "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" scripts\installer.iss
;
; 输出: Output\TCL表格比对_Setup.exe
; ============================================

#define MyAppName "TCL表格比对"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TCL"
#define MyAppExeName "TCL表格比对.exe"

; PyInstaller 输出目录（相对于 scripts/ 目录）
#define MySourceDir "..\dist\TCL表格比对_Win7"

[Setup]
; 应用信息
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

; 安装目录
DefaultDirName={autopf}\{#MyAppName}
; Program Files 需要管理员权限
PrivilegesRequired=admin

; 其他设置（输出到项目根目录的 Output/）
OutputDir=..\Output
OutputBaseFilename=TCL表格比对_Setup
; 压缩
Compression=lzma2/ultra64
SolidCompression=yes
; 图标（相对于 scripts/ 目录，图标在 resources/ 目录）
SetupIconFile=..\resources\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
; 外观
WizardStyle=modern
; 语言
ShowLanguageDialog=yes
; 卸载
UninstallDisplayName={#MyAppName}
; 最小安装大小
; 系统要求
MinVersion=6.1.7601
; 架构
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; PyInstaller 打包输出的全部文件
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 安装包和快捷方式图标（图标在 resources/ 目录）
Source: "..\resources\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; VC++ Redistributable（需要提前下载到 resources/ 目录）
Source: "..\resources\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
; 给 Users 组设置安装目录的写权限，确保应用可创建/修改数据库和配置文件
Name: "{app}"; Permissions: users-modify

[Icons]
; 开始菜单快捷方式
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"
; 桌面快捷方式
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
; 安装 VC++ Redistributable（静默模式）
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "正在安装 Visual C++ 运行库..."; Flags: waituntilterminated skipifnotsilent; Check: VCRedistExists
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /passive /norestart"; StatusMsg: "正在安装 Visual C++ 运行库..."; Flags: waituntilterminated skipifsilent; Check: VCRedistExists
; 安装完成后启动应用
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除安装目录下的动态生成文件
Type: filesandordirs; Name: "{app}\__pycache__"
Type: files; Name: "{app}\*.db"
Type: files; Name: "{app}\*.log"

[Code]
function VCRedistExists: Boolean;
begin
  Result := FileExists(ExpandConstant('{tmp}\vc_redist.x64.exe'));
end;
