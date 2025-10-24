# 快速速查表：日志级别

## 开发时如何使用日志记录

### 1️⃣ 开发新功能
```python
// config.py
CURRENT_LOG_LEVEL = 'DEBUG'    // 用于 GUI 组件 (Canvas, Rulers)
// 或者
CURRENT_LOG_LEVEL = 'VERBOSE'  // 用于深度分析所有细节
```

**启动应用程序 → 在控制台和 logs/app.log 中查看详情**

### 2️⃣ 通过日志测试
- 查看功能工作的每个步骤
- 检查坐标、事件、转换
- 更快找到错误

### 3️⃣ 功能正常？关闭详细日志
```python
// config.py
CURRENT_LOG_LEVEL = 'NORMAL'   // 仅重要信息
```

### 4️⃣ 生产环境 (发布版本)
```python
// config.py
CURRENT_LOG_LEVEL = 'MINIMAL'  // 仅关键错误
```

## 快速切换

| 级别 | 使用时机 | 记录内容 |
|------|----------|----------|
| **VERBOSE** | 深度调试 | 所有内容，包括元素 |
| **DEBUG** | GUI 开发 | Canvas, Rulers, 坐标 |
| **NORMAL** | 日常工作 | ZPL, API, Templates |
| **MINIMAL** | 生产环境 | 仅错误 |

## 工作循环示例

```python
// 1. 开始制作新功能 "Add Image Element"
CURRENT_LOG_LEVEL = 'DEBUG'

// 2. 坐标错误？增加详细程度
CURRENT_LOG_LEVEL = 'VERBOSE'

// 3. 修复，测试 - 正常工作！
CURRENT_LOG_LEVEL = 'NORMAL'

// 4. 准备发布
CURRENT_LOG_LEVEL = 'MINIMAL'
```

## 类别 (可在 config.py 中单独禁用)

```python
LOG_CATEGORIES = {
    'canvas': True,    // Canvas 事件
    'rulers': True,    // 标尺和光标
    'elements': True,  // 元素 (仅 VERBOSE)
    'zpl': True,       // ZPL 生成 (始终启用)
    'api': True,       // API 请求 (始终启用)
    'template': True   // 模板 (始终启用)
}
```

## 💡 黄金规则

**测试时 = DEBUG/VERBOSE**  
**正常工作时 = NORMAL**  
**发布时 = MINIMAL**

config.py 中的一个变量控制所有日志记录！