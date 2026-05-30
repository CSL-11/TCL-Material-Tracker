# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TCL表格比对系统 (TCL Table Comparison System) - PyQt5 desktop application for comparing material shortage data between yesterday's and today's Excel files, with SQLite database storage and optional LAN server mode for multi-client data sharing.

## Commands

**强制规则：本项目必须使用Python 3.8环境**
- 原因：需要兼容Windows 7系统，Python 3.8是最后支持Windows 7的版本
- 所有操作（开发、调试、打包）都必须使用Python 3.8
- 使用方式：`py -3.8 xxx.py` 或 `D:\py\python38\python.exe xxx.py`

```bash
py -3.8 main_app.py                                    # Run desktop app
py -3.8 server.py --host 0.0.0.0 --port 5000           # Run LAN server
py -3.8 -m PyInstaller scripts\build_win7_final.spec --clean --noconfirm  # Build EXE (Win7)
py -3.8 scripts\setup_cx_freeze.py build                # Build for Windows 7 (cx_Freeze, alternative)
```

### Testing

No formal test framework (pytest/unittest) is configured. Ad-hoc test scripts exist in `tests/` directory. Run individual tests with:

```bash
py -3.8 tests\test_excel_processor_workflow.py
py -3.8 tests\test_persistence_mode.py
py -3.8 tests\test_server_responses.py
```

### Dependencies

```bash
py -3.8 -m pip install -r requirements\requirements_full.txt      # Full dependencies
py -3.8 -m pip install -r requirements\requirements_win7.txt      # Win7 compatible only
py -3.8 -m pip install -r requirements\requirements_server.txt    # Server mode only
```

## Architecture

### Core Components

| File | Lines | Role |
|------|-------|------|
| `main_app.py` | ~5300 | Monolithic entry point — `TCLApplication(QMainWindow)` handles UI, business logic, persistence, network |
| `database.py` | ~157 | `DatabaseManager` — client SQLite (`TCL表格数据库.db`) with 4 tables |
| `excel_processor.py` | ~349 | `ExcelProcessor` — stateless Excel read/write/compare/classify |
| `server.py` | ~319 | Flask REST API server (8 endpoints, CORS-enabled) |
| `server_db.py` | ~408 | `ServerDatabase` — server SQLite (`tcl_server_data.db`) with 5 tables |
| `network_manager.py` | ~359 | `NetworkManager` — HTTP client singleton for server mode, manages `network_config.json` |

### UI Pattern

Single `QMainWindow` with `QHBoxLayout`: fixed-width sidebar (`QFrame` + `QListWidget`, 80px) + `QStackedWidget`. Orange accent theme `#F97316`. Sidebar nav's `currentRowChanged` → `stacked_widget.setCurrentIndex`.

**Tab order in sidebar** (differs from setup order): 表格比对 → 数据查询导出 → 数据库 → 出货管理 → 序号导入 → 分类导出 → 还需交货统计.

### Dual-Mode Persistence

Data persistence has two modes, controlled by the sidebar network toggle:

- **Local mode**: JSON cache files in `data/` directory (`db_cache.json`, `batch_import_cache.json`, `output_dir_config.json`)
- **Server mode**: HTTP REST API to Flask server, with automatic fallback to local on failure

The `save_*_with_mode()` / `load_*_with_mode()` methods in `main_app.py` check `network_manager.is_server_mode` and delegate accordingly.

### Key Match Pattern

Compound match key `物料号|销售订单|销售订单行号|内需单号` built by `make_match_key()`. Used across all comparison operations. Field name normalization handles alternates: `物料号`/`物料编码`, `销售订单`/`销售订单号`.

### Comparison Flow (`compare_and_export()`)

1. Read yesterday Excel → `read_excel()`, today Excel → `read_excel_with_color()` (preserves cell fgColor)
2. Optionally read shipment Excel → build `shipment_dict` keyed by compound match key
3. `excel_processor.compare_and_get_diff()` — computes `昨天总缺料`, `今天总缺料`, `变化量`
4. Attach `本次送货数量` to diff rows (subtraction from 总缺料 is **commented out**)
5. Sort by `(red_flag, -change_value)` where `red_flag = (变化量 != 今天总缺料)`
6. Export to timestamped Excel with color preservation and conditional formatting
7. Classify materials and `insert_or_update_level1()` to SQLite

### Batch Import Flow (Tab 5)

`batch_import_excel()` supports multi-file selection with append/replace dialog. Adds `订单名称` column (from filename). `filter_batch_data()` does fuzzy material number search with comma-separated keywords. Shipment matching highlights matched rows in red.

### Shipment Match/Delete Flow (Tab 2)

`import_shipment_to_compare()` → `display_shipment_matched()` (red highlight, pre-checked checkboxes) → `delete_shipment_matched()` removes matched rows from `db_all_data`.

### Table Widget Pattern

Both `db_table` and `batch_import_table` use checkbox-in-first-column via `setCellWidget(row, 0, QWidget containing QCheckBox)`. Data columns use `QTableWidgetItem`. Row coloring: red for shipment matches, light blue for search results.

## Material Classification (7 categories)

| Category | Keywords |
|----------|----------|
| 透明商标类 | 透明、商标、白色PET |
| 铝箔类 | 银、铝箔、电化铝箔 |
| 接线类 | 接线 |
| 能源能效类 | 能源、能效 |
| 标贴类 | 型号标贴、机型标贴、纸箱标贴、不可移铜版纸、不可移光粉纸、指示标贴 |
| 说明书类 | 说明书、合格证、保修卡、清单、附页、手册、用户、书写纸、参数页 |
| 特光类 | 特光 |

Unmatched → `其他`; null descriptions → `未分类`.

## Database Schema

```sql
一级表格: ID, 序号, 订单号, 物料号, 物料描述, 供方, 总缺料, 采购组, 采购组名称, 跟单, 供方在途量, 已承诺量, 销售订单, 销售订单行号, 内需单号, 送货日期, 分类, 创建时间
  UNIQUE(物料号, 订单号) — INSERT OR REPLACE

二级表格: ID, 一级ID, 物料号, 物料描述, 序号, 订单号, 总缺料, 分类, 下单时间

出货记录: ID, 物料号, 数量, 出货日期, 订单号, 创建时间

表头配置: ID, 表格类型, 列名, 列顺序, 显示名称
```

Server database (`tcl_server_data.db`) stores the same logical data as JSON blobs in `db_data`, `batch_import_data`, `shipment_data`, `config`, `operation_log` tables.

## File Generation Rules

**构建产物** → `dist/` 和 `build/` 目录（PyInstaller自动生成）
**安装包** → `Output/` 目录（Inno Setup生成）
**测试脚本** → `tests/` 目录
**文档和图片** → `docs/` 目录
**资源文件** → `resources/` 目录（图标、运行库、Python包）
**依赖配置** → `requirements/` 目录
**运行时数据** → `data/` 目录（配置缓存、数据库文件）
**构建脚本** → `scripts/` 目录

## Coding Guidelines

**权衡说明：** 本准则偏向谨慎而非速度。对于简单任务，请自行判断。

### 1. 思考先行
**不要假设。不要隐藏困惑。主动呈现权衡方案。**

在实现之前：
- 明确陈述你的假设。如果不确定，请提问。
- 如果存在多种解读，请逐一呈现——不要默默选择其中一种。
- 如果存在更简单的方案，请明确指出。在必要时提出反对意见。
- 如果遇到不清楚的地方，请停下来。明确指出困惑所在。主动提问。

### 2. 简洁至上
**用最少的代码解决问题。不添加任何推测性内容。**
- 不添加超出需求范围的功能。
- 不为仅使用一次的代码创建抽象层。
- 不添加未被要求的"灵活性"或"可配置性"。
- 不为不可能发生的场景添加错误处理。
- 如果你写了 200 行代码而实际上 50 行就能完成，请重写。

自问："资深工程师会觉得这过于复杂吗？"如果答案是肯定的，请简化。

### 3. 精准修改
**只触碰必须修改的部分。只清理你自己造成的遗留问题。**

在编辑现有代码时：
- 不要"改进"相邻的代码、注释或格式。
- 不要重构没有问题的部分。
- 匹配现有代码风格，即使你更倾向于不同的写法。
- 如果你注意到无关的死代码，请提及它——但不要删除它。

当你的修改产生了孤立代码时：
- 删除因你的修改而变得不再使用的导入、变量或函数。
- 除非被明确要求，否则不要删除之前就存在的死代码。

检验标准：每一行被修改的代码都应能直接追溯到用户的请求。

### 4. 目标驱动执行
**定义成功标准。循环迭代直至验证通过。**

将任务转化为可验证的目标：
- "添加验证" → "为无效输入编写测试，然后使其通过"
- "修复这个 bug" → "编写一个能复现该 bug 的测试，然后使其通过"
- "重构 X" → "确保重构前后测试均通过"

对于多步骤任务，陈述一个简要计划：
```
1. [步骤] → 验证：[检查项]
2. [步骤] → 验证：[检查项]
3. [步骤] → 验证：[检查项]
```

明确的成功标准让你能够独立循环迭代。模糊的标准（"让它能工作"）则需要不断澄清。
