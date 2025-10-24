# ⚠️ 过时文档

**此文件已过时！** 日志系统已于 2025-10-04 更新。

## 📚 最新文档：

### 🚀 快速入门
**[LOGGING_QUICK.md](LOGGING_QUICK.md)** - 日常工作的快速速查表

### 📖 完整文档  
**[LOGGING.md](LOGGING.md)** - 关于日志系统的详细信息

### 🔧 项目集成
**[DEVELOPMENT_PROMPT.md](../DEVELOPMENT_PROMPT.md)** - 关于日志工作循环的规则 #7

---

## 主要变更 (2025-10-04):

### ✨ 新级别系统
```python
// config.py
CURRENT_LOG_LEVEL = 'NORMAL'  // MINIMAL | NORMAL | DEBUG | VERBOSE
```

**4个级别替代2个：**
- `MINIMAL` - 仅错误 (生产环境)
- `NORMAL` - 重要信息 (默认)
- `DEBUG` - GUI 组件调试
- `VERBOSE` - 最大详细程度

### 🎯 日志类别
现在可以禁用特定类别：
```python
LOG_CATEGORIES = {
    'canvas': True/False,
    'rulers': True/False,
    'elements': True/False,
    'zpl': True,      // 始终启用
    'api': True,      // 始终启用
    'template': True  // 始终启用
}
```

### 🔄 工作循环
**开发功能时：**
1. 设置为 `DEBUG` 或 `VERBOSE`
2. 通过日志测试
3. 功能正常 → 返回 `NORMAL`
4. 生产环境 → `MINIMAL`

---

## 🗑️ 从此文件中删除的内容：
- 过时的代码示例
- 不相关的配置结构
- 旧的日志级别 (INFO/DEBUG)

## ✅ 请改用：
1. **快速参考** → `LOGGING_QUICK.md`
2. **详细信息** → `LOGGING.md`
3. **集成指南** → `DEVELOPMENT_PROMPT.md` (规则 #7)

---

*此文件保留用于历史记录。所有新开发人员应使用更新的文档。*

**最后更新：** 2025-10-04