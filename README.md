# TCL表格比对系统

TCL表格比对系统是一个基于 PyQt5 的桌面应用，用于比对昨天与今天的缺料 Excel 数据，并将结果写入本地 SQLite 数据库；同时支持可选的局域网服务器模式，供多客户端共享数据。

## 功能概览

- 比对昨天与今天的缺料表
- 保留 Excel 单元格颜色并导出结果
- 按规则自动分类物料
- 管理数据库数据并支持查询导出
- 导入出货数据并匹配删除已处理记录
- 支持序号批量导入与模糊检索
- 支持局域网服务器模式与本地模式切换
- 支持 Windows 7 兼容打包

## 运行环境

**本项目必须使用 Python 3.8。**

原因：需要兼容 Windows 7，Python 3.8 是最后支持 Windows 7 的版本。

建议使用以下任一方式运行：

```bash
py -3.8 xxx.py
```

或：

```bash
D:\py\python38\python.exe xxx.py
```

## 依赖说明

核心依赖：

- PyQt5==5.15.9
- openpyxl==3.0.10

可选依赖：

- Flask==2.3.3
- flask-cors==4.0.0
- requests==2.31.0

说明：

- 局域网模式需要 Flask、flask-cors、requests
- 打包时需要 PyInstaller
- 部分功能存在对 pandas 的内联导入，默认未纳入主要依赖清单

安装完整依赖：

```bash
py -3.8 -m pip install -r requirements/requirements_full.txt
```

仅安装 Win7 兼容依赖：

```bash
py -3.8 -m pip install -r requirements/requirements_win7.txt
```

## 快速开始

### 1. 启动桌面程序

```bash
py -3.8 main_app.py
```

### 2. 启动局域网服务器

```bash
py -3.8 server.py --host 0.0.0.0 --port 5000
```

### 3. Windows 批处理脚本

启动桌面程序：

```bash
scripts\启动.bat
```

启动服务器：

```bash
scripts\start_server.bat
```

## 打包

### PyInstaller

```bash
py -3.8 -m PyInstaller scripts\build_win7_final.spec --clean --noconfirm
```

### cx_Freeze

```bash
py -3.8 scripts\setup_cx_freeze.py build
```

### Inno Setup

安装包脚本位于：

```text
scripts\installer.iss
```

生成位置约定：

- `dist/`：PyInstaller 输出
- `build/`：PyInstaller 构建缓存
- `Output/`：安装包输出目录

## 项目结构

```text
TCL_Material_Tracker/
├── main_app.py              # 主程序入口
├── database.py              # 本地数据库模块
├── excel_processor.py       # Excel 处理模块
├── network_manager.py       # 网络管理模块
├── server.py                # Flask 服务器入口
├── server_db.py             # 服务器数据库模块
├── version.py               # 版本信息
├── scripts/                 # 启动、打包、兼容脚本
├── tests/                   # 测试脚本
├── docs/                    # 文档与图片
├── resources/               # 图标、运行库、嵌入式 Python 等资源
├── requirements/            # 依赖清单
├── data/                    # 运行时数据，不提交 git
├── build/                   # 构建缓存
├── dist/                    # 构建输出
└── Output/                  # 安装包输出
```

## 主要模块

### main_app.py

桌面主程序入口，核心窗口类为 `TCLApplication(QMainWindow)`，集中处理：

- UI 界面
- 业务逻辑
- 本地持久化
- 服务器模式切换

### excel_processor.py

负责 Excel 读取、颜色保留、差异比对、分类等核心表格逻辑。

### database.py

本地 SQLite 数据库管理模块。

### server.py

基于 Flask 的 REST API 服务端，供局域网模式下的多个客户端共享数据。

### server_db.py

服务器端 SQLite 数据库管理模块。

### network_manager.py

客户端网络访问管理模块，负责服务器模式配置和 HTTP 请求。

## 核心业务说明

### 表格比对逻辑

系统会对昨天和今天的缺料表进行比对，生成：

- 昨天总缺料
- 今天总缺料
- 变化量
- 本次送货数量

比对过程中使用复合匹配键：

```text
物料号|销售订单|销售订单行号|内需单号
```

并兼容部分字段别名，例如：

- `物料号` / `物料编码`
- `销售订单` / `销售订单号`

### 持久化模式

系统支持两种持久化模式：

1. 本地模式
   - 数据保存在 `data/` 下的 SQLite 与 JSON 缓存文件中
2. 服务器模式
   - 数据通过 HTTP 请求写入 Flask 服务端
   - 服务异常时可回退到本地模式

### 物料分类

当前内置 7 类物料分类规则：

- 透明商标类
- 铝箔类
- 接线类
- 能源能效类
- 标贴类
- 说明书类
- 特光类

未命中规则的数据归类为 `其他`，空描述数据归类为 `未分类`。

## 数据文件

运行时数据默认位于 `data/` 目录，包括但不限于：

- SQLite 数据库文件
- `db_cache.json`
- `batch_import_cache.json`
- `output_dir_config.json`
- 网络配置缓存

这些文件属于运行时数据，不应提交到 git。

## 测试说明

项目当前没有正式的 pytest / unittest 测试体系，仓库中保留了若干脚本式测试文件：

- `tests/test_excel_processor_workflow.py`
- `tests/test_persistence_mode.py`
- `tests/test_server_responses.py`

如需执行，请显式使用 Python 3.8。

## 文档

- 用户操作指南：`docs/用户操作指南.md`
- 数据流示意图：`docs/数据流.png`

## 版本

当前版本：`1.0.0`

版本来源：`version.py`

## 适用场景

- 每日缺料数据对比
- 出货匹配与剔除
- 物料分类统计
- 局域网内共享同一套业务数据

## 注意事项

- 必须使用 Python 3.8
- 项目主要面向 Windows 环境
- Windows 7 打包兼容是当前约束之一
- 若启用局域网模式，请先启动服务器端
