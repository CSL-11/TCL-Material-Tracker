---
name: "TCL Publish Installer"
description: "Build and publish this TCL 表格比对 project as a Windows installer using Python 3.8, PyInstaller, and Inno Setup. Use when the user says 发布安装包, 打包安装包, build installer, release installer, or wants to create Output/TCL表格比对_Setup.exe."
---

# TCL Publish Installer

## 作用

为本项目生成 Windows 安装包：先用 Python 3.8 + PyInstaller 构建 `dist/TCL表格比对_Win7/`，再用 Inno Setup 编译 `Output/TCL表格比对_Setup.exe`。

本技能只适用于当前项目：`TCL表格比对系统`。

## 前置条件

- 必须使用 Python 3.8：`D:\py\python38\python.exe`
- Inno Setup 6：`C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
- 项目根目录存在：
  - `build_win7_final.spec`
  - `installer.iss`
  - `icon.ico`
  - `vc_redist.x64.exe`

如果缺少 `vc_redist.x64.exe`，先下载：

```powershell
curl.exe -L -o "D:\vibe_codeing\TCL-5-11\vc_redist.x64.exe" "https://aka.ms/vs/17/release/vc_redist.x64.exe"
```

## 发布流程

### 1. 确认工作目录

```powershell
Set-Location "D:\vibe_codeing\TCL-5-11"
```

### 2. 清理旧构建产物

```powershell
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist\TCL表格比对_Win7") { Remove-Item "dist\TCL表格比对_Win7" -Recurse -Force }
```

### 3. PyInstaller 构建 EXE 文件夹

```powershell
& "D:\py\python38\python.exe" -m PyInstaller build_win7_final.spec --clean --noconfirm
```

成功后应存在：

```text
dist\TCL表格比对_Win7\TCL表格比对.exe
```

### 4. Inno Setup 编译安装包

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer.iss"
```

成功后应存在：

```text
Output\TCL表格比对_Setup.exe
```

## 一键命令

在 Claude Code 中可直接运行：

```powershell
Set-Location "D:\vibe_codeing\TCL-5-11"; if (Test-Path "build") { Remove-Item "build" -Recurse -Force }; if (Test-Path "dist\TCL表格比对_Win7") { Remove-Item "dist\TCL表格比对_Win7" -Recurse -Force }; & "D:\py\python38\python.exe" -m PyInstaller build_win7_final.spec --clean --noconfirm; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer.iss"; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; $f = Get-Item "Output\TCL表格比对_Setup.exe"; Write-Output "SUCCESS: $($f.FullName) $([math]::Round($f.Length/1MB,2)) MB"
```

## 验证清单

发布完成后必须验证：

1. `Output\TCL表格比对_Setup.exe` 存在。
2. 文件大小正常，当前约 64 MB。
3. PyInstaller 日志出现：`Copying icons from ['...icon.ico']`，确认 EXE 图标已嵌入。
4. Inno Setup 日志出现：`Successful compile`。
5. 安装后桌面快捷方式、开始菜单快捷方式使用 `icon.ico`。

## 常见问题

### 安装后图标不对

检查 `build_win7_final.spec`：

```python
icon=os.path.join(work_dir, 'icon.ico')
```

检查 `installer.iss`：

```iss
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
```

修改后必须重新运行 PyInstaller 和 Inno Setup 两步。

### Inno Setup 找不到

确认路径：

```powershell
Test-Path "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

### Win7 兼容要求

不要升级 Python 版本。本项目必须使用 Python 3.8，因为 Python 3.8 是最后支持 Windows 7 的版本。
