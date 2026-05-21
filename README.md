# 🔖 BookmarkPilot

<div align="center">

**Lightweight Terminal Bookmark Manager | 輕量級終端智能書籤管理引擎**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**BookmarkPilot** is a zero-dependency terminal bookmark manager designed for developers who want to efficiently manage browser bookmarks, code snippet links, technical documentation, and article collections without leaving the command line.

**Why BookmarkPilot?**
- 🚀 **Zero Dependencies** - Pure Python standard library, no pip install required
- 🎯 **Developer-Focused** - Built for the terminal workflow
- 📦 **Browser Compatible** - Import/export from Chrome, Firefox, Edge
- 🔍 **Powerful Search** - Full-text search with fuzzy matching
- 🖥️ **Interactive TUI** - Beautiful terminal interface
- 🏷️ **Smart Organization** - Folders, tags, and favorites

### ✨ Features

| Feature | Description |
|---------|-------------|
| 📚 **Bookmark Management** | Add, edit, delete, and organize bookmarks with ease |
| 📥 **Smart Import** | Import from Chrome/Firefox/Edge HTML, JSON, Markdown |
| 📤 **Multi-Format Export** | Export to HTML, JSON, Markdown, or plain text |
| 🔍 **Advanced Search** | Full-text search across title, URL, description, and tags |
| 🖥️ **TUI Interface** | Interactive terminal UI with keyboard navigation |
| 🏷️ **Tag System** | Organize bookmarks with custom tags |
| 📁 **Folder Support** | Hierarchical folder organization |
| ⭐ **Favorites** | Mark important bookmarks as favorites |
| 📊 **Statistics** | View bookmark analytics and usage stats |
| 🔗 **URL Validation** | Automatic URL validation and normalization |
| 🌐 **Cross-Platform** | Works on Linux, macOS, and Windows |

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/BookmarkPilot.git
cd BookmarkPilot

# Run directly (no installation needed)
python3 bookmarkpilot.py --help

# Or install globally
pip install -e .
```

#### Basic Usage

```bash
# Add a bookmark
bookmarkpilot add https://github.com "GitHub" --tags git,dev --folder Development

# List all bookmarks
bookmarkpilot list

# Search bookmarks
bookmarkpilot search "python tutorial"

# Show statistics
bookmarkpilot stats

# Launch TUI mode
bookmarkpilot tui
```

### 📖 Detailed Usage

#### Adding Bookmarks

```bash
# Simple add
bookmarkpilot add https://example.com

# With title and tags
bookmarkpilot add https://github.com "GitHub" --tags git,dev

# With folder
bookmarkpilot add https://stackoverflow.com "Stack Overflow" --folder "Dev Resources"
```

#### Importing Bookmarks

```bash
# Import from browser export (HTML)
bookmarkpilot import bookmarks.html --format html

# Import from JSON
bookmarkpilot import bookmarks.json --format json

# Import from Markdown
bookmarkpilot import links.md --format markdown
```

#### Exporting Bookmarks

```bash
# Export to HTML (Netscape format)
bookmarkpilot export bookmarks.html --format html

# Export to JSON
bookmarkpilot export bookmarks.json --format json

# Export to Markdown
bookmarkpilot export bookmarks.md --format markdown
```

#### TUI Mode Commands

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate bookmarks |
| `Enter` | Open selected bookmark |
| `/` | Search |
| `f` | Filter by folder |
| `t` | Filter by tag |
| `a` | Add new bookmark |
| `e` | Edit bookmark |
| `d` | Delete bookmark |
| `s` | Toggle favorite |
| `q` | Quit |

### 💡 Design Philosophy

BookmarkPilot follows the Unix philosophy:
- **Do one thing well** - Focus on bookmark management
- **Work with others** - Import/export in standard formats
- **Text interface** - Perfect for terminal workflows
- **Zero dependencies** - No bloat, just functionality

### 📦 Project Structure

```
bookmarkpilot/
├── bookmarkpilot.py      # Main entry point
├── core/                 # Core modules
│   ├── database.py       # SQLite operations
│   ├── bookmark.py       # Bookmark model
│   ├── importer.py       # Import functionality
│   ├── exporter.py       # Export functionality
│   └── search.py         # Search engine
├── ui/                   # User interface
│   └── tui.py            # Terminal UI
├── utils/                # Utilities
│   ├── config.py         # Configuration
│   ├── validator.py      # URL validation
│   └── formatter.py      # Output formatting
└── tests/                # Test suite
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**BookmarkPilot** 是一个零依赖的终端书签管理器，专为希望在不离开命令行的情况下高效管理浏览器书签、代码片段链接、技术文档和文章收藏的开发者设计。

**为什么选择 BookmarkPilot？**
- 🚀 **零依赖** - 纯 Python 标准库，无需 pip 安装
- 🎯 **开发者优先** - 为终端工作流打造
- 📦 **浏览器兼容** - 支持从 Chrome、Firefox、Edge 导入/导出
- 🔍 **强大的搜索** - 全文搜索，支持模糊匹配
- 🖥️ **交互式 TUI** - 美观的终端界面
- 🏷️ **智能组织** - 文件夹、标签和收藏

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📚 **书签管理** | 轻松添加、编辑、删除和组织书签 |
| 📥 **智能导入** | 从 Chrome/Firefox/Edge HTML、JSON、Markdown 导入 |
| 📤 **多格式导出** | 导出为 HTML、JSON、Markdown 或纯文本 |
| 🔍 **高级搜索** | 在标题、URL、描述和标签中进行全文搜索 |
| 🖥️ **TUI 界面** | 带键盘导航的交互式终端界面 |
| 🏷️ **标签系统** | 使用自定义标签组织书签 |
| 📁 **文件夹支持** | 层级文件夹组织 |
| ⭐ **收藏夹** | 将重要书签标记为收藏 |
| 📊 **统计信息** | 查看书签分析和使用统计 |
| 🔗 **URL 验证** | 自动 URL 验证和规范化 |
| 🌐 **跨平台** | 支持 Linux、macOS 和 Windows |

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/BookmarkPilot.git
cd BookmarkPilot

# 直接运行（无需安装）
python3 bookmarkpilot.py --help

# 或全局安装
pip install -e .
```

#### 基本用法

```bash
# 添加书签
bookmarkpilot add https://github.com "GitHub" --tags git,dev --folder Development

# 列出所有书签
bookmarkpilot list

# 搜索书签
bookmarkpilot search "python tutorial"

# 显示统计信息
bookmarkpilot stats

# 启动 TUI 模式
bookmarkpilot tui
```

### 📖 详细使用指南

#### 添加书签

```bash
# 简单添加
bookmarkpilot add https://example.com

# 带标题和标签
bookmarkpilot add https://github.com "GitHub" --tags git,dev

# 指定文件夹
bookmarkpilot add https://stackoverflow.com "Stack Overflow" --folder "Dev Resources"
```

#### 导入书签

```bash
# 从浏览器导出文件导入（HTML）
bookmarkpilot import bookmarks.html --format html

# 从 JSON 导入
bookmarkpilot import bookmarks.json --format json

# 从 Markdown 导入
bookmarkpilot import links.md --format markdown
```

#### 导出书签

```bash
# 导出为 HTML（Netscape 格式）
bookmarkpilot export bookmarks.html --format html

# 导出为 JSON
bookmarkpilot export bookmarks.json --format json

# 导出为 Markdown
bookmarkpilot export bookmarks.md --format markdown
```

#### TUI 模式快捷键

| 按键 | 操作 |
|------|------|
| `↑/↓` 或 `j/k` | 导航书签 |
| `Enter` | 打开选中的书签 |
| `/` | 搜索 |
| `f` | 按文件夹筛选 |
| `t` | 按标签筛选 |
| `a` | 添加新书签 |
| `e` | 编辑书签 |
| `d` | 删除书签 |
| `s` | 切换收藏状态 |
| `q` | 退出 |

### 💡 设计理念

BookmarkPilot 遵循 Unix 哲学：
- **做好一件事** - 专注于书签管理
- **与其他工具协作** - 标准格式的导入/导出
- **文本界面** - 完美适配终端工作流
- **零依赖** - 无臃肿，只有功能

### 📦 项目结构

```
bookmarkpilot/
├── bookmarkpilot.py      # 主入口
├── core/                 # 核心模块
│   ├── database.py       # SQLite 操作
│   ├── bookmark.py       # 书签模型
│   ├── importer.py       # 导入功能
│   ├── exporter.py       # 导出功能
│   └── search.py         # 搜索引擎
├── ui/                   # 用户界面
│   └── tui.py            # 终端界面
├── utils/                # 工具类
│   ├── config.py         # 配置管理
│   ├── validator.py      # URL 验证
│   └── formatter.py      # 输出格式化
└── tests/                # 测试套件
```

### 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 📄 开源协议

本项目基于 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<a name="繁體中文"></a>
## 🇹
<a name="繁體中文"></a>
## 🇹
