# ZPL 标签设计器日志系统

## 详细级别

在 `config.py` 中配置了 4 个日志详细级别：

### 1. MINIMAL (仅错误)
```python
CURRENT_LOG_LEVEL = 'MINIMAL'
```
- 仅记录关键错误 (ERROR)
- 建议用于生产环境

### 2. NORMAL (标准模式)
```python
CURRENT_LOG_LEVEL = 'NORMAL'  # ← 默认设置
```
- 重要信息 + 错误 (INFO, ERROR)
- ZPL 生成、API 请求、模板操作
- 建议用于日常工作

### 3. DEBUG (调试)
```python
CURRENT_LOG_LEVEL = 'DEBUG'
```
- 额外：Canvas 事件、标尺、坐标
- 开发 GUI 组件时使用

### 4. VERBOSE (最详细)
```python
CURRENT_LOG_LEVEL = 'VERBOSE'
```
- 包含所有内容，甚至元素和内部逻辑
- 仅在深度调试时使用

## 日志类别

可以在 `config.py` 中管理特定类别：

```python
LOG_CATEGORIES = {
    'canvas': True/False,     // Canvas 事件 (坐标、光标)
    'rulers': True/False,     // 标尺 (绘制、光标标记)
    'elements': True/False,   // 元素 (创建、更改)
    'zpl': True,              // ZPL 生成 (始终启用)
    'api': True,              // API 请求 (始终启用)
    'template': True          // 模板操作 (始终启用)
}
```

## 输出格式

### 控制台 (简洁)
```
[INFO] zpl.generator: 为 28x28mm 标签生成 ZPL
[DEBUG] canvas_view: 鼠标位置 x=12.5mm, y=8.3mm
[ERROR] api.server: 连接失败
```

### 文件 (详细)
```
2025-10-04 15:30:45 - zpl.generator - INFO - 为 28x28mm 标签生成 ZPL
2025-10-04 15:30:46 - canvas_view - DEBUG - 鼠标位置 x=12.5mm, y=8.3mm
2025-10-04 15:30:47 - api.server - ERROR - 连接失败
```

## 快速切换

**正常工作：**
```python
CURRENT_LOG_LEVEL = 'NORMAL'
```

**有问题？启用调试：**
```python
CURRENT_LOG_LEVEL = 'DEBUG'
```

**需要最大详细程度：**
```python
CURRENT_LOG_LEVEL = 'VERBOSE'
```

**生产环境 (最少日志)：**
```python
CURRENT_LOG_LEVEL = 'MINIMAL'
```

## 日志文件

所有日志保存在：`D:\AiKlientBank\1C_Zebra\logs\`

- `app.log` - 主日志文件
- 轮转：最大 5MB，3 个备份文件