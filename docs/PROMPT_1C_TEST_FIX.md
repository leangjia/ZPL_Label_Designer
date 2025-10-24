# 提示：完善1C集成测试

## 🎯 任务

按照工作测试 `test_cursor_tracking_smart.py` 的示例，完善智能测试 `test_1c_integration_smart.py`。

## 🔴 关键问题

**测试在启动前没有创建 `temp_1c_test.json` 文件！**

```python
# ❌ 错误 (当前代码):
temp_json = project_root / "temp_1c_test.json"
print(f"[TEST] Test JSON: {temp_json}")

# 用不存在的文件启动 MainWindow！
window = MainWindow(template_file=str(temp_json))  # ← FileNotFoundError!
```

**结果：** `_load_template_from_file()` 崩溃并报错，`[1C-IMPORT]` 日志不出现，测试失败。

---

## 📖 上下文

### 1C 加载的工作原理：

**1. MainWindow.__init__(template_file=...)**
```python
def __init__(self, template_file=None):
    # ... UI 初始化 ...
    
    # 保存文件路径
    self._template_file_to_load = template_file
    
    # ... 创建元素 ...
    
    # 在 __init__ 结束时调用加载：
    if self._template_file_to_load:
        self._load_template_from_file(self._template_file_to_load)
```

**2. TemplateMixin._load_template_from_file(filepath)**
```python
def _load_template_from_file(self, filepath):
    """从文件加载模板 (用于1C集成)"""
    try:
        logger.info(f"[1C-IMPORT] 正在从文件加载模板: {filepath}")
        
        # 读取 JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        logger.info(f"[1C-IMPORT] JSON 已加载: {json_data.get('name', 'unnamed')}")
        
        # 检查结构
        if 'zpl' not in json_data:
            logger.warning("[1C-IMPORT] JSON 中没有 ZPL 代码")
            QMessageBox.warning(self, "导入", "JSON 中没有 ZPL 代码")
            return
        
        # 显示带 ZPL 的对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("来自 1C 的模板")
        # ... 创建对话框 ...
        dialog.exec()
        
        logger.info("[1C-IMPORT] 模板显示成功")
        
    except Exception as e:
        logger.error(f"[1C-IMPORT] 加载失败: {e}", exc_info=True)
        QMessageBox.critical(self, "导入错误", f"加载错误:\n{e}")
```

**3. LogAnalyzer 寻找的日志：**
```python
@staticmethod
def parse_1c_logs(log_content):
    """提取 [1C-IMPORT] 日志"""
    logs = {
        'loading': [],   # [1C-IMPORT] 正在从文件加载模板: {filepath}
        'loaded': [],    # [1C-IMPORT] JSON 已加载: {name}
        'displayed': []  # [1C-IMPORT] 模板显示成功
    }
    # ... 正则解析 ...
    return logs
```

---

## ✅ 工作示例 (test_cursor_tracking_smart.py)

### 工作测试结构：

```python
def test_cursor_smart():
    """光标跟踪智能测试与日志分析"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 1. 测试前的日志文件大小
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. 模拟操作：创建 QMouseEvent 并直接调用
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent, QPoint
    
    mouse_event = QMouseEvent(
        QEvent.MouseMove,
        QPointF(x, y),
        Qt.NoButton,
        Qt.NoButton,
        Qt.NoModifier
    )
    window.canvas.mouseMoveEvent(mouse_event)  # ← 直接调用！
    app.processEvents()
    
    # 3. 读取新日志 (通过 seek!)
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)  # ← 关键：不删除文件！
        new_logs = f.read()
    
    # 4. 日志分析
    analyzer = CursorLogAnalyzer()
    cursor_logs = analyzer.parse_cursor_logs(new_logs)
    ruler_logs = analyzer.parse_ruler_logs(new_logs)
    issues = analyzer.detect_issues(cursor_logs, ruler_logs)
    
    # 5. 带数字的详细输出
    print("=" * 60)
    print("[阶段 1] 光标跟踪 - 日志分析")
    print("=" * 60)
    print(f"\n[光标] 信号: {len(cursor_logs)}")
    print(f"[标尺-H] 更新: {len(ruler_logs['h_update'])}")
    
    if cursor_logs:
        last = cursor_logs[-1]
        print(f"最后光标位置: {last[0]:.2f}mm, {last[1]:.2f}mm")
    
    if issues:
        print(f"\n检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[失败] 光标跟踪存在问题")
        return 1
    
    print("\n[成功] 光标跟踪工作正常")
    return 0
```

**关键特性：**
1. ✅ `file_size_before = log_file.stat().st_size` - 不删除文件！
2. ✅ `f.seek(file_size_before)` - 只读取新日志
3. ✅ 直接调用处理程序：`window.canvas.mouseMoveEvent(event)`
4. ✅ 带数字的详细输出：`{len(cursor_logs)}`, `{last[0]:.2f}mm`
5. ✅ 分析多种日志类型：cursor_logs, ruler_logs
6. ✅ 通过 `detect_issues()` 检测多种问题类型

---

## 🔧 需要修复的内容

### 1. 在测试前创建 temp_1c_test.json

**JSON 文件结构 (来自 Python 编辑器)：**
```json
{
    "name": "TEST_TEMPLATE_1C",
    "zpl": "^XA^CI28^PW223^LL223^FO7,0^A0N,20,30^FDTest Label^FS^XZ",
    "variables": {
        "{{Модель}}": "TEST_MODEL",
        "{{Штрихкод}}": "1234567890"
    }
}
```

**添加到测试中：**
```python
def test_1c_integration_smart():
    """1C 集成智能测试"""
    
    print("\n" + "="*60)
    print("智能测试: 1C 集成 - 模板加载")
    print("="*60)
    
    log_file = project_root / "logs" / "zpl_designer.log"
    log_file.parent.mkdir(exist_ok=True)
    
    # ✅ 创建测试 JSON (新代码！)
    temp_json = project_root / "temp_1c_test.json"
    test_template = {
        "name": "TEST_TEMPLATE_1C",
        "zpl": "^XA^CI28^PW223^LL223^FO7,0^A0N,20,30^FDTest Label^FS^XZ",
        "variables": {
            "{{Модель}}": "TEST_MODEL",
            "{{Штрихкод}}": "1234567890"
        }
    }
    
    import json
    with open(temp_json, 'w', encoding='utf-8') as f:
        json.dump(test_template, f, indent=2, ensure_ascii=False)
    
    print(f"[测试] 测试 JSON 已创建: {temp_json}")
    print(f"[测试] 模板名称: {test_template['name']}")
    
    # 测试前的文件大小
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    print(f"[测试] 测试前日志文件大小: {file_size_before} 字节")
    
    # ... 其余代码 ...
```

### 2. 改进结果输出 (像光标测试一样)

**替换：**
```python
# ❌ 旧代码 (简单输出):
print(f"Loading logs: {len(logs['loading'])}")
if logs['loading']:
    print(f"  Path: {logs['loading'][0]}")

print(f"Loaded logs: {len(logs['loaded'])}")
if logs['loaded']:
    print(f"  Name: {logs['loaded'][0]}")

print(f"Displayed logs: {len(logs['displayed'])}")
```

**为：**
```python
# ✅ 新代码 (详细输出):
print("\n" + "="*60)
print("[1C-导入] 日志分析")
print("="*60)

print(f"\n[1C-导入] 找到加载日志: {len(logs['loading'])}")
if logs['loading']:
    print(f"  文件路径: {logs['loading'][0]}")
else:
    print("  [!] 没有加载日志 - 方法未调用！")

print(f"\n[1C-导入] 找到已加载日志: {len(logs['loaded'])}")
if logs['loaded']:
    print(f"  模板名称: {logs['loaded'][0]}")
else:
    print("  [!] 没有已加载日志 - JSON 解析失败！")

print(f"\n[1C-导入] 找到显示日志: {len(logs['displayed'])}")
if logs['displayed']:
    print(f"  对话框显示: 是")
else:
    print("  [!] 没有显示日志 - 对话框未显示！")

if issues:
    print(f"\n检测到 {len(issues)} 个问题:")
    for issue in issues:
        print(f"  {issue['type']}: {issue['desc']}")
    print("\n" + "="*60)
    print("[失败] 1C 集成存在问题")
    print("="*60)
    return 1

print("\n" + "="*60)
print("[成功] 1C 集成工作正常")
print("="*60)
return 0
```

### 3. 添加临时文件清理

**在测试结束时：**
```python
# 清理临时文件
if temp_json.exists():
    temp_json.unlink()
    print(f"\n[测试] 临时文件已清理: {temp_json}")
```

### 4. 改进 LogAnalyzer (可选)

**添加更详细的解析：**
```python
@staticmethod
def parse_1c_logs(log_content):
    """提取 [1C-IMPORT] 日志"""
    logs = {
        'loading': [],
        'loaded': [],
        'displayed': [],
        'errors': []  # ← 新增：错误
    }
    
    for line in log_content.split('\n'):
        if '[1C-IMPORT] 正在从文件加载模板:' in line:
            match = re.search(r'从文件加载模板: (.+)$', line)
            if match:
                logs['loading'].append(match.group(1))
        
        if '[1C-IMPORT] JSON 已加载:' in line:
            match = re.search(r'已加载: (.+)$', line)
            if match:
                logs['loaded'].append(match.group(1))
        
        if '[1C-IMPORT] 模板显示成功' in line:
            logs['displayed'].append(True)
        
        # ← 新增：捕获错误
        if '[1C-IMPORT] 加载失败:' in line:
            match = re.search(r'失败: (.+)$', line)
            if match:
                logs['errors'].append(match.group(1))
    
    return logs
```

---

## 📋 完整修复代码

```python
# -*- coding: utf-8 -*-
"""智能测试：从 1C JSON 加载模板"""

import sys
import re
import json
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger


class Load1CLogAnalyzer:
    """1C 加载日志分析器"""
    
    @staticmethod
    def parse_1c_logs(log_content):
        """提取 [1C-导入] 日志"""
        logs = {
            'loading': [],
            'loaded': [],
            'displayed': [],
            'errors': []
        }
        
        for line in log_content.split('\n'):
            if '[1C-导入] 正在从文件加载模板:' in line:
                match = re.search(r'从文件加载模板: (.+)$', line)
                if match:
                    logs['loading'].append(match.group(1))
            
            if '[1C-导入] JSON 已加载:' in line:
                match = re.search(r'已加载: (.+)$', line)
                if match:
                    logs['loaded'].append(match.group(1))
            
            if '[1C-导入] 模板显示成功' in line:
                logs['displayed'].append(True)
            
            if '[1C-导入] 加载失败:' in line:
                match = re.search(r'失败: (.+)$', line)
                if match:
                    logs['errors'].append(match.group(1))
        
        return logs
    
    @staticmethod
    def detect_issues(logs):
        """检测问题"""
        issues = []
        
        # 问题 1: JSON 未加载
        if not logs['loading']:
            issues.append({
                'type': '没有加载日志',
                'desc': '未找到加载日志 - 方法未调用或文件未找到'
            })
        
        # 问题 2: 名称未识别
        if not logs['loaded']:
            issues.append({
                'type': 'JSON 未解析',
                'desc': '未找到 JSON 加载日志 - 解析失败'
            })
        
        # 问题 3: 对话框未显示
        if not logs['displayed']:
            issues.append({
                'type': '对话框未显示',
                'desc': '未找到模板显示日志 - 对话框未显示'
            })
        
        # 问题 4: 日志中有错误
        if logs['errors']:
            issues.append({
                'type': '加载错误',
                'desc': f'发现加载错误: {logs["errors"][0]}'
            })
        
        return issues


def test_1c_integration_smart():
    """1C 集成智能测试"""
    
    print("\n" + "="*60)
    print("智能测试: 1C 集成 - 模板加载")
    print("="*60)
    
    log_file = project_root / "logs" / "zpl_designer.log"
    log_file.parent.mkdir(exist_ok=True)
    
    # ✅ 创建测试 JSON
    temp_json = project_root / "temp_1c_test.json"
    test_template = {
        "name": "TEST_TEMPLATE_1C",
        "zpl": "^XA^CI28^PW223^LL223^FO7,0^A0N,20,30^FDTest Label^FS^XZ",
        "variables": {
            "{{Модель}}": "TEST_MODEL",
            "{{Штрихкод}}": "1234567890"
        }
    }
    
    with open(temp_json, 'w', encoding='utf-8') as f:
        json.dump(test_template, f, indent=2, ensure_ascii=False)
    
    print(f"[测试] 测试 JSON 已创建: {temp_json}")
    print(f"[测试] 模板名称: {test_template['name']}")
    print(f"[测试] ZPL 长度: {len(test_template['zpl'])} 字符")
    
    # 测试前的文件大小
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    print(f"[测试] 测试前日志文件大小: {file_size_before} 字节")
    
    # 启动应用程序
    app = QApplication.instance() or QApplication(sys.argv)
    
    print(f"\n[测试] 使用 template_file={temp_json} 启动 MainWindow")
    window = MainWindow(template_file=str(temp_json))
    window.show()
    
    # 关键：给事件处理时间
    for _ in range(5):
        app.processEvents()
    
    print("[测试] MainWindow 已显示，事件已处理")
    
    # 关闭窗口，不使用 event loop
    window.close()
    app.processEvents()
    
    print("[测试] 窗口已关闭")
    
    # 读取新日志
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    print(f"\n[测试] 新日志大小: {len(new_logs)} 字符")
    
    # 分析
    analyzer = Load1CLogAnalyzer()
    logs = analyzer.parse_1c_logs(new_logs)
    issues = analyzer.detect_issues(logs)
    
    # 输出
    print("\n" + "="*60)
    print("[1C-导入] 日志分析")
    print("="*60)
    
    print(f"\n[1C-导入] 找到加载日志: {len(logs['loading'])}")
    if logs['loading']:
        print(f"  文件路径: {logs['loading'][0]}")
    else:
        print("  [!] 没有加载日志 - 方法未调用！")
    
    print(f"\n[1C-导入] 找到已加载日志: {len(logs['loaded'])}")
    if logs['loaded']:
        print(f"  模板名称: {logs['loaded'][0]}")
    else:
        print("  [!] 没有已加载日志 - JSON 解析失败！")
    
    print(f"\n[1C-导入] 找到显示日志: {len(logs['displayed'])}")
    if logs['displayed']:
        print(f"  对话框显示: 是")
    else:
        print("  [!] 没有显示日志 - 对话框未显示！")
    
    if logs['errors']:
        print(f"\n[1C-导入] 发现错误: {len(logs['errors'])}")
        for error in logs['errors']:
            print(f"  错误: {error}")
    
    # 清理临时文件
    if temp_json.exists():
        temp_json.unlink()
        print(f"\n[测试] 临时文件已清理: {temp_json}")
    
    if issues:
        print(f"\n检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "="*60)
        print("[失败] 1C 集成存在问题")
        print("="*60)
        return 1
    
    print("\n" + "="*60)
    print("[成功] 1C 集成工作正常")
    print("="*60)
    return 0


if __name__ == '__main__':
    exit_code = test_1c_integration_smart()
    sys.exit(exit_code)
```

---

## 🎯 预期结果

### 成功执行时：

```
============================================================
智能测试: 1C 集成 - 模板加载
============================================================
[测试] 测试 JSON 已创建: D:\AiKlientBank\1C_Zebra\temp_1c_test.json
[测试] 模板名称: TEST_TEMPLATE_1C
[测试] ZPL 长度: 64 字符
[测试] 测试前日志文件大小: 15234 字节

[测试] 使用 template_file=D:\AiKlientBank\1C_Zebra\temp_1c_test.json 启动 MainWindow
[测试] MainWindow 已显示，事件已处理
[测试] 窗口已关闭

[测试] 新日志大小: 457 字符

============================================================
[1C-导入] 日志分析
============================================================

[1C-导入] 找到加载日志: 1
  文件路径: D:\AiKlientBank\1C_Zebra\temp_1c_test.json

[1C-导入] 找到已加载日志: 1
  模板名称: TEST_TEMPLATE_1C

[1C-导入] 找到显示日志: 1
  对话框显示: 是

[测试] 临时文件已清理: D:\AiKlientBank\1C_Zebra\temp_1c_test.json

============================================================
[成功] 1C 集成工作正常
============================================================
```

### 出错时：

```
============================================================
[1C-导入] 日志分析
============================================================

[1C-导入] 找到加载日志: 0
  [!] 没有加载日志 - 方法未调用！

[1C-导入] 找到已加载日志: 0
  [!] 没有已加载日志 - JSON 解析失败！

[1C-导入] 找到显示日志: 0
  [!] 没有显示日志 - 对话框未显示！

检测到 3 个问题:
  没有加载日志: 未找到加载日志 - 方法未调用或文件未找到
  JSON 未解析: 未找到 JSON 加载日志 - 解析失败
  对话框未显示: 未找到模板显示日志 - 对话框未显示

============================================================
[失败] 1C 集成存在问题
============================================================
```

---

## ✅ 修复检查清单

- [ ] 在测试前创建 temp_1c_test.json
- [ ] 添加带 name, zpl, variables 的 JSON 结构
- [ ] 改进结果输出 (像光标测试一样详细)
- [ ] 在 LogAnalyzer 中添加错误解析
- [ ] 在结束时添加临时文件清理
- [ ] 保留 file_size_before 逻辑 (不删除文件！)
- [ ] 添加带数字和状态的详细 print
- [ ] 验证 [1C-导入] 日志出现

---

## 🔑 关键原则

1. **始终创建测试文件** - 不要依赖现有文件
2. **使用 file_size_before，不删除日志** - 保留历史
3. **带数字的详细输出** - 不只是 len()，而是带描述的 `{len(logs)}`
4. **LogAnalyzer 检测多个问题** - 最少 3-4 种类型
5. **清理自己的文件** - 删除临时文件

---

**版本：** 1.0  
**日期：** 2025-01-08  
**作者：** 资深 AI 助手  
**语言：** 中文 (userPreferences 规则)