<<<<<<< HEAD
# ZPL 标签设计器
=======
中国大陆地区加速：

pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# ZPL Label Designer
>>>>>>> 8ade440d66ae4fe06a4391a6c3698afc42aeaae8

### 开源之家友情提醒：中国大陆地区加速：

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
```

基于 PySide6 图形界面的专业 ZPL (Zebra Programming Language) 标签创建和编辑应用程序。

## 🚀 功能特性

### 主要功能
- **图形化标签编辑器**，具有直观的用户界面
- **支持多种元素：**
  - 可自定义字体和大小的文本字段
  - 条码：EAN-13、Code 128、QR 码
  - 图像和图形元素
- **ZPL 代码生成**，自动转换为斑马打印机可识别的代码
- **通过 Labelary API 预览**标签效果
- **多种测量单位**（毫米、英寸、点）
- **模板和占位符**，支持变量数据

### 画布功能
- **光标追踪** - 实时显示光标坐标位置
- **点缩放** - 以指定点为中心进行缩放
- **网格吸附** - 网格对齐，精确定位元素
- **元素边界** - 高亮显示选中元素的边界
- **键盘快捷键** - 快速操作的热键支持
- **右键菜单** - 元素操作的上下文菜单
- **智能参考线** - 智能对齐辅助线
- **撤销/重做** - 操作历史记录管理
- **多选功能** - 支持多个元素同时选择

### 技术特性
- **智能测试** - 使用 LogAnalyzer 的自动化测试
- **模块化架构** - 基于混入模式的模块化设计
- **单位转换** - 自动单位测量转换
- **模板系统** - 可复用的模板系统
- **API 集成** - 与外部 API 集成实现预览功能

## 🛠️ 技术栈

- **Python 3.13** - 主要开发语言
- **PySide6** - 图形用户界面
- **Pillow** - 图像处理
- **Requests** - HTTP 请求外部 API
- **Flask** - Web 服务器 API 端点
- **python-barcode** - 条码生成

## 📦 安装指南

### 系统要求
- Python 3.13+
- Windows 10/11

### 快速开始
```powershell
# 克隆代码库
git clone https://github.com/你的用户名/1C_Zebra.git
cd 1C_Zebra

# 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖包
pip install -r requirements.txt

# 启动应用程序
python main.py
```

## 🎯 项目结构

```
1C_Zebra/
├── main.py                 # 应用程序入口点
├── config.py              # 应用程序配置
├── requirements.txt       # Python 依赖包
├── gui/                   # 用户界面
│   ├── main_window.py     # 主窗口界面
│   └── mixins/            # 模块化组件
├── core/                  # 核心逻辑
│   ├── elements/          # 标签元素
│   └── generators/        # ZPL 代码生成器
├── utils/                 # 工具类
│   ├── logger.py          # 日志系统
│   └── unit_converter.py  # 单位转换器
├── integration/           # 外部集成
│   └── labelary_client.py # Labelary API 客户端
├── tests/                 # 测试代码
│   └── *_smart.py         # 使用 LogAnalyzer 的智能测试
└── docs/                  # 项目文档
```

## 🧪 测试

项目使用独特的 **智能测试** 系统，通过 LogAnalyzer 自动发现问题：

```powershell
# 运行所有基础画布功能测试
python tests/run_stages_1_5_smart.py

# 运行高级功能测试
python tests/run_stages_6_9_smart.py

# 运行特定功能测试
python tests/test_cursor_tracking_smart.py
python tests/test_zoom_smart.py
python tests/test_snap_smart.py
```

## 📋 使用说明

### 创建简单标签
1. 启动应用程序：`python main.py`
2. 在属性面板中设置标签尺寸
3. 通过工具栏添加文本元素
4. 根据需要添加条码
5. 使用预览功能检查效果
6. 导出 ZPL 代码用于打印

### 使用模板
- 使用占位符 `{{字段名}}` 表示变量数据
- 将常用布局保存为模板
- 从外部源导入数据

## 🤝 参与开发

### 开发新功能
1. 创建功能分支
2. 在代码中添加 DEBUG 日志
3. 创建使用 LogAnalyzer 的智能测试
4. 确保所有测试通过
5. 创建 Pull Request

### 问题报告
使用日志系统进行诊断：
- 在 `utils/logger.py` 中启用 DEBUG 级别
- 重现问题
- 将日志附加到问题报告中

## 📄 许可证

本项目为公司内部使用而开发。

## 🔗 相关链接

- [Zebra 编程语言指南](https://www.zebra.com/us/en/support-downloads/knowledge-articles/ZPL-Zebra-Programming-Language.html)
- [Labelary API 文档](http://labelary.com/service.html)
- [PySide6 文档](https://doc.qt.io/qtforpython/)

---

<<<<<<< HEAD
**作者：** 高级软件工程师  
**项目：** 1C_Zebra ZPL 标签设计器  
**版本：** 1.0.0
=======
**Автор:** Senior Software Engineer  
**Проект:** 1C_Zebra ZPL Label Designer  
**Версия:** 1.0.0
>>>>>>> 8ade440d66ae4fe06a4391a6c3698afc42aeaae8
