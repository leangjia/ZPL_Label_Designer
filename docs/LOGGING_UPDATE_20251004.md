# 日志系统更新 - 2025年10月4日

## ✅ 已完成内容

### 1. 扩展了 config.py
添加了灵活的日志级别管理系统：

```python
# 4个详细级别
LOG_LEVELS = {
    'MINIMAL': 'ERROR',      # 仅错误
    'NORMAL': 'INFO',        # 重要信息  
    'DEBUG': 'DEBUG',        # 调试信息
    'VERBOSE': 'DEBUG'       # 最详细
}

# 一个变量控制所有
CURRENT_LOG_LEVEL = 'NORMAL'  # ← 在此更改！

# 类别 (可单独禁用)
LOG_CATEGORIES = {
    'canvas': CURRENT_LOG_LEVEL in ['DEBUG', 'VERBOSE'],
    'rulers': CURRENT_LOG_LEVEL in ['DEBUG', 'VERBOSE'],
    'elements': CURRENT_LOG_LEVEL in ['VERBOSE'],
    'zpl': True,      # 始终启用
    'api': True,      # 始终启用
    'template': True  # 始终启用
}
```

### 2. 更新了 DEVELOPMENT_PROMPT.md
添加了规则 #7 "日志记录 - 通过级别测试"：

**工作算法：**
- 编写新功能 → 设置为 `DEBUG` 或 `VERBOSE`
- 通过日志测试 → 查看工作详情
- 功能正常工作 → 返回 `NORMAL`
- 生产环境 → `MINIMAL`

### 3. 创建了文档

#### docs/LOGGING.md (详细)
- 所有4个级别的描述
- 日志类别
- 输出格式 (控制台 + 文件)
- 快速切换

#### docs/LOGGING_QUICK.md (速查表)
- 级别表格
- 工作循环示例
- 黄金规则
- 类别示例

### 4. 清理了调试日志
从 GUI 模块中删除了多余的 `logger.debug()`：
- `gui/rulers.py` - 清理了 paintEvent 和其他方法

### 5. 更新了过时文档
`docs/LOGGING_SYSTEM.md` 标记为过时，并链接到最新文件

## 📚 文档结构

```
docs/
├── LOGGING_QUICK.md       # ← 从此开始 (快速速查表)
├── LOGGING.md             # ← 详细信息
├── LOGGING_SYSTEM.md      # ⚠️ 过时 (存档)
└── DEBUG_GUIDE.md         # 调试指南 (先前)
```

## 🎯 如何使用

### 日常工作
```python
// config.py
CURRENT_LOG_LEVEL = 'NORMAL'
```

### 开发新功能
```python
// config.py
CURRENT_LOG_LEVEL = 'DEBUG'    // 用于 GUI
// 或
CURRENT_LOG_LEVEL = 'VERBOSE'  // 用于深度调试
```

### 生产环境
```python
// config.py  
CURRENT_LOG_LEVEL = 'MINIMAL'  // 仅错误
```

## 🔍 工作循环示例

```python
// 1. 开发 Image Element
CURRENT_LOG_LEVEL = 'DEBUG'

// 2. 坐标错误？
CURRENT_LOG_LEVEL = 'VERBOSE'

// 3. 正常工作！
CURRENT_LOG_LEVEL = 'NORMAL'

// 4. 发布版本
CURRENT_LOG_LEVEL = 'MINIMAL'
```

## 📊 新系统的优势

✅ **一个变量** 控制所有日志记录  
✅ **类别** - 禁用不需要的  
✅ **不同格式** 用于控制台和文件  
✅ **自动详细程度** 根据级别  
✅ **快速切换** 无需更改代码

## 🔗 项目集成

使用规则描述在：
- `DEVELOPMENT_PROMPT.md` - 规则 #7
- `docs/LOGGING_QUICK.md` - 快速入门
- `config.py` - 集中配置

## 📝 Knowledge Graph

更新了实体 "1C_Zebra 日志系统"：
- 添加了关于规则 #7 的信息
- 工作循环原则
- 文档链接
- 级别切换算法

---

**作者:** Claude AI  
**日期:** 2025年10月4日  
**版本:** 2.0