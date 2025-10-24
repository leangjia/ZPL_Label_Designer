# AI 指令：1C_ZEBRA 项目
> ZPL 标签设计器 - Zebra 打印机的可视化标签编辑器

## 🔴 每个会话开始时必须执行（关键！）

**在对代码进行任何操作之前：**

1. **执行 `memory:read_graph()`** - 读取知识图谱
2. **查找规则：** `memory:search_nodes("1C_Zebra Critical Rules")`
3. **获取相关规则：** `memory:open_nodes(["1C_Zebra Critical Rules"])` 并跟踪连接
4. **在每次** 处理代码、测试、日志时应用这些规则
5. **如果违反关键规则 = 破坏项目！**

**来自 MEMORY 的关键规则：**
- 智能测试只能通过 `exec(open('runner.py').read())` 启动
- Logger 导入只能使用 `from utils.logger import logger`
- 只能通过 `filesystem:read_text_file` 读取文件
- 不要猜测 - 读取真实代码

## 📁 项目路径
**D:\AiKlientBank\1C_Zebra\**

## 🎯 工作风格

**关键：** 不要高级别 - 只使用真实代码！
- 简洁明了
- 作为专家对待
- 立即回答，细节随后
- **100% 确定不会破坏任何东西**
- 沟通语言：中文

## 🔴 规则 #1 - 答案编译（关键！）

在发送任何关于逻辑/架构的答案之前：

1. **停止** - 不要立即发送
2. **检查：** "开发者能否无需猜测即可实现？"
3. **扫描** 遗漏：GUI 结构？ZPL 格式？逻辑？坐标？
4. **触发器：** 词语 'GUI', 'canvas', 'ZPL', 'template', 'API', '生成'
5. **禁止** 片段：没有完整逻辑的"添加了 X" = 违规
6. **完整性：** 修改部分 → 输出整个系统

**此规则高于所有其他规则！**

## 🚫 禁止猜测

**只能编写：**
- ✅ 在文件中真实看到的内容 (read_file)
- ✅ filesystem tools 真实显示的内容
- ✅ 更改的具体代码行

**禁止：**
- ❌ "启动后 GUI 将打开"
- ❌ "现在 canvas 正确绘制"
- ❌ "修复的内容：1..."
- ❌ "结果将显示..."

**宁愿"不知道"也不要撒谎！**

## 🔴 代码处理算法

### 黄金规则：读取 → 编辑 → 验证

**步骤 1：修改前读取**
```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\[文件]</parameter>
</invoke>
```

**步骤 2：精确编辑**
```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\[文件]</parameter>
<parameter name="edits">[{
  "oldText": "文件中的确切文本",
  "newText": "新文本"
}]</parameter>
</invoke>
```

**步骤 3：验证**
```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\[文件]</parameter>
<parameter name="head">20</parameter>
</invoke>
```

## 🔴 规则 #2 - 启动智能测试（关键！）

### ⚠️ 唯一正确的方法

**始终通过带有 exec() 的 python-runner 启动测试：**

```xml
<invoke name="python-runner:run_command">
<parameter name="command">exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_test_name.py').read())</parameter>
</invoke>
```

### ❌ 不起作用的方法：

```python
// ❌ 错误 - python-runner 不能用于读取文件！
with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r') as f:
    content = f.read()
// ERROR: attempted relative import with no known parent package
```

### ✅ 正确的顺序：

1. **创建测试** 通过 `filesystem:write_file`
2. **创建运行器** 通过 `filesystem:write_file`
3. **启动** 通过 `python-runner:run_command` 带 `exec(open(...))`
4. **分析退出代码** - 0 = 成功, != 0 = 失败

### 📋 运行器脚本结构

```python
// tests/run_feature_test.py
import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_feature.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"\n退出代码: {result.returncode}")
```

## 🧪 规则 #3 - 智能测试（关键！）

### ⚠️ 问题：普通测试是盲目的

```python
// ❌ 普通测试（看不到错误）：
assert element.config.x == 6.0  // 通过 ✓

// 但日志显示错误：
//   [SNAP] 6.55mm -> 6.0mm      ← snap 计算正确
//   [FINAL-POS] Before: 6.55mm
//   [FINAL-POS] After: 6.55mm   ← 未应用！
//   [FINAL-POS] Saved: 6.00mm   ← 偶然正确
```

**结论：** 最终结果正确，但**逻辑已损坏**！

### ✅ 解决方案：带 LogAnalyzer 的智能测试

## 📋 创建智能测试的算法

### 步骤 1：在代码中添加 DEBUG 日志（必须！）

**规则：** 没有日志的智能测试 = 普通盲目测试！

#### 1.1 日志命名模式

```python
// 格式：[功能] 操作: 数据
logger.debug(f"[光标] 信号发射: {x_mm:.2f}mm, {y_mm:.2f}mm")
logger.debug(f"[缩放] 之前: scale={scale:.2f}, cursor_pos=({x:.1f}, {y:.1f})")
logger.debug(f"[吸附] {x_old:.2f}mm -> {x_new:.1f}mm")
logger.debug(f"[最终位置] 吸附后: {x:.2f}mm, {y:.2f}mm")
logger.debug(f"[标尺-H] 更新位置: {mm:.2f}mm")
logger.debug(f"[标尺-H] 绘制位置: {px}px")
```

#### 1.2 在哪里添加日志

```python
// gui/canvas_view.py
def mouseMoveEvent(self, event):
    x_mm = self._px_to_mm(scene_pos.x())
    y_mm = self._px_to_mm(scene_pos.y())
    logger.debug(f"[光标] 信号发射: {x_mm:.2f}mm, {y_mm:.2f}mm")
    self.cursor_position_changed.emit(x_mm, y_mm)

def wheelEvent(self, event):
    old_pos = self.mapToScene(event.position().toPoint())
    logger.debug(f"[缩放] 之前: scale={self.current_scale:.2f}, cursor_pos=({old_pos.x():.1f}, {old_pos.y():.1f})")
    // ... 缩放逻辑 ...
    new_pos = self.mapToScene(event.position().toPoint())
    logger.debug(f"[缩放] 之后: scale={self.current_scale:.2f}, cursor_pos=({new_pos.x():.1f}, {new_pos.y():.1f})")

// gui/rulers.py
def update_cursor_position(self, mm):
    logger.debug(f"[标尺-{'H' if self.orientation==Qt.Horizontal else 'V'}] 更新位置: {mm:.2f}mm")

def _draw_cursor_marker(self, painter):
    pos_px = int(self._mm_to_px(self.cursor_pos_mm) * self.scale_factor)
    logger.debug(f"[标尺-{'H' if self.orientation==Qt.Horizontal else 'V'}] 绘制位置: {pos_px}px")
```

### 步骤 2：创建 LogAnalyzer 类

```python
class LogAnalyzer:
    """日志分析器 - 解析并检测问题"""
    
    @staticmethod
    def parse_feature_logs(log_content):
        """提取特定功能的日志"""
        pattern = r'\[功能\] 模式_这里'
        return [parsed_data for m in re.findall(pattern, log_content)]
    
    @staticmethod
    def detect_issues(logs_dict):
        """检测 2-3 种问题类型"""
        issues = []
        
        // 检查 1：阶段 A != 阶段 B
        if logs_dict['stage_a'] != logs_dict['stage_b']:
            issues.append({
                'type': '阶段不匹配',
                'desc': f'阶段 A = {logs_dict["stage_a"]}, 阶段 B = {logs_dict["stage_b"]}'
            })
        
        // 检查 2：逻辑未生效
        // 检查 3：最终结果 != 预期
        
        return issues
```

### 步骤 3：创建智能测试

**关键：** 不要删除日志文件！使用 `file_size_before`！

```python
def test_feature_smart():
    """带日志分析的智能测试"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    // 1. 测试前的日志文件大小
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    // 2. 模拟：直接调用处理程序（不通过 QTest！）
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent
    
    event = QMouseEvent(QEvent.MouseMove, QPointF(x, y), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
    window.canvas.mouseMoveEvent(event)  // ← 直接调用！
    app.processEvents()
    
    // 3. 读取新日志
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)  // ← 关键：seek，不删除文件！
        new_logs = f.read()
    
    // 4. 分析
    analyzer = LogAnalyzer()
    logs = analyzer.parse_feature_logs(new_logs)
    issues = analyzer.detect_issues(logs)
    
    // 5. 输出
    print("=" * 60)
    print("[功能] 日志分析")
    print("=" * 60)
    print(f"找到日志: {len(logs)}")
    
    if issues:
        print(f"\n检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[失败] 功能存在问题")
        return 1
    
    print("\n[成功] 功能工作正常")
    return 0
```

### 步骤 4：创建运行器

```python
// tests/run_feature_smart_test.py
import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_feature_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
print(f"\n退出代码: {result.returncode}")
```

### 步骤 5：启动

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_feature_smart_test.py').read())
```

## 🔬 不同功能的 LogAnalyzer 类型

### 1. 光标跟踪

```python
class CursorLogAnalyzer:
    @staticmethod
    def parse_cursor_logs(log):
        pattern = r'\[光标\] 信号发射: ([\d.]+)mm, ([\d.]+)mm'
        return [(float(m[0]), float(m[1])) for m in re.findall(pattern, log)]
    
    @staticmethod
    def parse_ruler_logs(log):
        h_update = re.findall(r'\[标尺-H\] 更新位置: ([\d.]+)mm', log)
        v_update = re.findall(r'\[标尺-V\] 更新位置: ([\d.]+)mm', log)
        h_draw = re.findall(r'\[标尺-H\] 绘制位置: ([\d.]+)px', log)
        return {'h_update': [float(x) for x in h_update], 'h_draw': [float(x) for x in h_draw], ...}
    
    @staticmethod
    def detect_issues(cursor_logs, ruler_logs):
        issues = []
        
        // 1. 光标 != 标尺更新
        if abs(cursor_logs[-1][0] - ruler_logs['h_update'][-1]) > 0.1:
            issues.append({'type': '光标标尺不匹配-H', 'desc': '...'})
        
        // 2. 标尺更新 != 绘制位置
        mm_value = ruler_logs['h_update'][-1]
        px_drawn = ruler_logs['h_draw'][-1]
        expected_px = mm_value * 203 / 25.4 * 2.5
        if abs(px_drawn - expected_px) > 2:
            issues.append({'type': '标尺绘制不正确', 'desc': '...'})
        
        return issues
```

### 2. 点缩放

```python
class ZoomLogAnalyzer:
    @staticmethod
    def parse_zoom_logs(log):
        before = re.findall(r'\[缩放\] 之前: scale=([\d.]+), cursor_pos=\(([\d.]+), ([\d.]+)\)', log)
        after = re.findall(r'\[缩放\] 之后: scale=([\d.]+), cursor_pos=\(([\d.]+), ([\d.]+)\)', log)
        return {
            'before': [(float(m[0]), float(m[1]), float(m[2])) for m in before],
            'after': [(float(m[0]), float(m[1]), float(m[2])) for m in after]
        }
    
    @staticmethod
    def detect_issues(zoom_logs, ruler_scales):
        issues = []
        
        // 1. 缩放未到光标 (cursor_pos 改变)
        before_cursor = (zoom_logs['before'][-1][1], zoom_logs['before'][-1][2])
        after_cursor = (zoom_logs['after'][-1][1], zoom_logs['after'][-1][2])
        if abs(before_cursor[0] - after_cursor[0]) > 5.0:  // 5px 容差
            issues.append({'type': '缩放未到光标', 'desc': '...'})
        
        // 2. 标尺缩放 != 画布缩放
        
        return issues
```

### 3. 网格吸附

```python
class SnapLogAnalyzer:
    @staticmethod
    def parse_snap_logs(log):
        pattern = r'\[吸附\] ([\d.]+)mm, ([\d.]+)mm -> ([\d.]+)mm, ([\d.]+)mm'
        return [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) 
                for m in re.findall(pattern, log)]
    
    @staticmethod
    def parse_final_pos_logs(log):
        before = re.findall(r'\[最终位置\] 吸附前: ([\d.]+)mm, ([\d.]+)mm', log)
        after = re.findall(r'\[最终位置\] 吸附后: ([\d.]+)mm, ([\d.]+)mm', log)
        saved = re.findall(r'\[最终位置\] 保存到元素: \(([\d.]+), ([\d.]+)\)', log)
        return {
            'before': [(float(m[0]), float(m[1])) for m in before],
            'after': [(float(m[0]), float(m[1])) for m in after],
            'saved': [(float(m[0]), float(m[1])) for m in saved]
        }
    
    @staticmethod
    def detect_issues(snap_logs, final_logs):
        issues = []
        
        // 1. 吸附显示一个值，最终显示另一个
        if snap_logs[-1][2] != final_logs['after'][-1][0]:
            issues.append({'type': '吸附最终不匹配', 'desc': '...'})
        
        // 2. 吸附未生效 (之前 == 之后)
        if final_logs['before'][-1] == final_logs['after'][-1]:
            if final_logs['before'][-1][0] % 2.0 != 0:  // 不在网格上
                issues.append({'type': '最终无吸附', 'desc': '...'})
        
        // 3. 最终 != 保存
        
        return issues
```

## 🚀 主运行器

为所有智能测试创建运行器：

```python
// tests/run_all_smart_tests.py
import subprocess

tests = [
    ("光标跟踪", r'tests\test_cursor_tracking_smart.py'),
    ("点缩放", r'tests\test_zoom_smart.py'),
    ("网格吸附", r'tests\test_snap_smart.py'),
]

results = []

for stage_name, test_path in tests:
    print(f"\n{'=' * 60}\n {stage_name}\n{'=' * 60}")
    
    result = subprocess.run(
        [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', test_path],
        cwd=r'D:\AiKlientBank\1C_Zebra',
        capture_output=True, text=True
    )
    
    print(result.stdout)
    results.append({'stage': stage_name, 'exit_code': result.returncode})

// 最终报告
print(f"\n{'=' * 60}\n 最终结果\n{'=' * 60}")
for r in results:
    status = "[成功]" if r['exit_code'] == 0 else "[失败]"
    print(f"{status} {r['stage']} - 退出代码: {r['exit_code']}")
```

## 📊 日志管理

```python
// config.py

// 开发和测试时
CURRENT_LOG_LEVEL = 'DEBUG'    // ← 智能测试必须！

// 测试后
CURRENT_LOG_LEVEL = 'NORMAL'

// 生产环境
CURRENT_LOG_LEVEL = 'MINIMAL'
```

## ⚠️ 关键错误

### ❌ 禁止操作：

1. **删除日志文件：**
   ```python
   // ❌ 错误：
   if log_file.exists():
       log_file.unlink()
   ```
   **✅ 正确：** `file_size_before = log_file.stat().st_size`

2. **使用 QTest 进行模拟：**
   ```python
   // ❌ 错误：
   QTest.mouseMove(window.canvas, pos)
   ```
   **✅ 正确：** 直接调用处理程序：
   ```python
   event = QMouseEvent(...)
   window.canvas.mouseMoveEvent(event)
   ```

3. **仅检查最终结果：**
   ```python
   // ❌ 错误：
   assert element.config.x == 6.0
   ```
   **✅ 正确：** 分析日志 + 检查最终结果

4. **没有日志就说"工作正常"：**
   ```python
   // ❌ 错误：
   print("[成功] 功能工作正常")  // 没有日志分析！
   ```
   **✅ 正确：**
   ```python
   issues = analyzer.detect_issues(logs)
   if not issues:
       print("[成功] 功能工作正常")
   ```

## 🎯 何时使用智能测试

### ✅ 必须用于：
- 网格吸附
- 缩放
- 拖放
- 坐标转换
- 光标跟踪
- 标尺同步
- 任何具有中间状态的 Canvas/GUI 逻辑

### ❌ 不需要用于：
- 简单数学计算
- 无逻辑的 getter/setter
- 静态方法
- 字符串解析

## 🔑 黄金规则

1. **测试前的 DEBUG 日志** - 必须！
2. **每个功能的 LogAnalyzer** - 自己的类
3. **file_size_before，不删除日志**
4. **直接调用处理程序** - 不通过 QTest
5. **检测 2-3 种问题类型** - 最少
6. **所有测试的主运行器** - 方便
7. **没有日志分析 = 不工作** - 主要规则！

## 🏗️ 架构

```
D:\AiKlientBank\1C_Zebra\
├── gui/                    // PySide6 GUI
│   ├── canvas_view.py     // DEBUG 日志：[光标], [缩放]
│   └── rulers.py          // DEBUG 日志：[标尺-H/V]
├── core/elements/          // DEBUG 日志：[吸附], [最终位置]
├── tests/
│   ├── test_*_smart.py    // 带 LogAnalyzer 的智能测试
│   ├── run_*_test.py      // 每个的运行器
│   └── run_all_smart_tests.py  // 主运行器
├── docs/
│   ├── SMART_TESTING_QUICK.md
│   └── SMART_TESTING.md
├── config.py              // CURRENT_LOG_LEVEL
└── logs/
    └── zpl_designer.log
```

## 🚫 关键禁令

### 代码中的 Unicode
**❌ 禁止：** ✓, ✗, ✅, ❌, ⚠️
**✅ 使用：** `[成功]`, `[失败]`, `[!]`, `[错误]`

### 极简主义
- ❌ 没有理由不更改 GUI 逻辑
- ❌ 不优化工作代码

**如果工作 → 不要动！**

### Logger 导入（关键！）

**⚠️ 问题：** 使用 `logging.getLogger(__name__)` 创建未配置的 logger，不会输出日志！

```python
// ❌ 绝对禁止：
import logging
logger = logging.getLogger(__name__)  // ← 未配置，日志不会输出！
```

**✅ 唯一正确的方法：**
```python
// ✅ 始终且仅以此方式：
from utils.logger import logger  // ← 全局配置的 logger
```

**为什么这很关键：**
- `utils/logger.py` 包含唯一配置的 logger，名称为 `"ZPL_Designer"`
- 此 logger 配置了正确的 handlers（文件 + 控制台）
- 此 logger 配置了正确的级别（DEBUG/INFO）
- `logging.getLogger(__name__)` 创建单独的未配置 logger！

**真实错误示例（阶段 8）：**
```python
// core/undo_commands.py 使用了：
logger = logging.getLogger(__name__)  // ← __name__ = "core.undo_commands"

// 结果：DEBUG 日志未输出！
// [UNDO-CMD] AddElementCommand created  ← 空
// [UNDO] REDO AddElement                ← 空

// 修复为：
from utils.logger import logger

// 结果：所有日志工作正常！
// [UNDO-CMD] AddElementCommand created  ← ✓
// [UNDO] REDO AddElement                ← ✓
```

**规则：** 检查每个新文件！如果看到 `import logging` → 替换为 `from utils.logger import logger`！

## 📖 文档

- `docs/SMART_TESTING_QUICK.md` - 复制粘贴速查表
- `docs/SMART_TESTING.md` - 详细文档
- `docs/LOGGING_QUICK.md` - 日志记录

---

**路径：** `D:\AiKlientBank\1C_Zebra\`  
**Python：** 3.11+ | **GUI：** PySide6  
**日志记录：** 测试时 `CURRENT_LOG_LEVEL = 'DEBUG'`

---

## 🔧 MCP TOOLS - 关键经验（关键！）

### ⚠️ 问题：python-runner 不是标准的 MCP！

**事实：** 此项目中的 `python-runner` 是 **自定义 Node.js 服务器**，而不是标准的 MCP Python 服务器！

```json
// claude_desktop_config.json
"python-runner": {
  "command": "C:\\Users\\Lit\\AppData\\Roaming\\Claude\\node-wrapper.bat",
  "args": ["D:/Program Files/Python/python-runner/index.js"]  // ← Node.js！
}
```

**这意味着：**
- 它在 `subprocess.run()` / `exec()` 模式下执行 Python 代码
- 当 `open()` 带有相对导入的文件时（`from .canvas_view`）- **Python 崩溃**！
- 这不是 REPL，只是运行脚本

### ❌ 不起作用的方法：

```python
// ❌ 错误 - 会因 ImportError 崩溃！
with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r') as f:
    content = f.read()
// ERROR: attempted relative import with no known parent package
```

**为什么：** Python 在读取文件时尝试执行导入：
```python
from .canvas_view import CanvasView  // ← 相对导入！
```

### ✅ 使用什么：

**始终使用 filesystem tools 读取文件！**

```xml
<!-- ✅ 正确 -->
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
</invoke>
```

**替代方案：** 使用 windows-cli 进行搜索

```xml
<invoke name="windows-cli:execute_command">
<parameter name="command">Select-String -Path "D:\AiKlientBank\1C_Zebra\gui\main_window.py" -Pattern "def _toggle_snap"</parameter>
<parameter name="shell">powershell</parameter>
</invoke>
```

### 🔑 MCP TOOLS 黄金规则：

**python-runner 仅用于：**
- ✅ 执行独立脚本 (subprocess.run)
- ✅ 通过运行器启动测试
- ✅ exec(open('runner.py').read())

**filesystem tools 用于：**
- ✅ 读取代码文件
- ✅ 编辑文件 (edit_file)
- ✅ 在文件中搜索 (search_files)
- ✅ 分析项目结构

**windows-cli 用于：**
- ✅ PowerShell 命令
- ✅ Select-String 搜索
- ✅ Git 操作

---

## 🎓 实践经验：阶段 4-5

### 经验 1：Qt Events 中的竞态条件

**问题：** `removeItem()` 调用 `selectionChanged` 重置 `selected_item`！

```python
// ❌ 错误：
def _delete_selected(self):
    if self.selected_item:
        self.canvas.scene.removeItem(self.selected_item)  // ← 调用 selectionChanged！
        
        // 现在 self.selected_item = None（在 _on_selection_changed 中重置）！
        if self.selected_item in self.graphics_items:  // ← 不会执行！
            self.graphics_items.remove(self.selected_item)
```

**✅ 正确：** 在 removeItem 之前保存 item：

```python
def _delete_selected(self):
    if self.selected_item:
        // 在 removeItem 之前保存！
        item_to_delete = self.selected_item
        element_to_delete = item_to_delete.element if hasattr(item_to_delete, 'element') else None
        
        // removeItem 调用 selectionChanged → self.selected_item = None
        self.canvas.scene.removeItem(item_to_delete)
        
        // 使用保存的变量！
        if element_to_delete in self.elements:
            self.elements.remove(element_to_delete)
        if item_to_delete in self.graphics_items:
            self.graphics_items.remove(item_to_delete)
```

**经验：** 在 Qt 中 events 调用其他 events → 始终在操作之前保存数据！

### 经验 2：PropertyPanel 的方法

**问题：** PropertyPanel 没有 `refresh()` 方法！

```python
// ❌ 错误：
if self.property_panel.current_element:
    self.property_panel.refresh()  // ← AttributeError！
```

**✅ 正确：** 在使用前阅读代码！

```python
// 首先 filesystem:read_text_file property_panel.py
// 找到方法 update_position(x_mm, y_mm)

if self.property_panel.current_element:
    self.property_panel.update_position(element.config.x, element.config.y)
```

**经验：** 不要猜测 API！通过 filesystem tools 阅读真实代码！

### 经验 3：LogAnalyzer 发现隐藏错误

**阶段 4 的真实示例：**

```
[边界] 元素位置: x=10.00mm, y=10.00mm  ← 正确
[边界-H] 高亮: start=10.00mm        ← 正确  
[边界-H] 绘制: start_px=197              ← 检查？

预期: 10mm * 203dpi / 25.4 * 2.5 = 200px
实际: 197px
差异: 3px - 可接受 ✓
```

智能测试**检查了中间阶段**，普通测试只会看到最终结果！

**阶段 5 的真实示例：**

```
[移动] 之前: (10.00, 10.00)mm
[移动] 增量: (1.00, 0.00)mm
[移动] 之后: (11.00, 10.00)mm

// LogAnalyzer 检查：
expected_x = 10.00 + 1.00 = 11.00
actual_x = 11.00
✓ 移动计算正确！
```

没有日志我们看不到 Before + Delta = After！

### 经验 4：使用 file_size_before 而不是删除

**问题：** 删除日志会丢失历史！

```python
// ❌ 错误：
if log_file.exists():
    log_file.unlink()  // ← 丢失所有上下文！
```

**✅ 正确：**

```python
// 只读取新日志
file_size_before = log_file.stat().st_size if log_file.exists() else 0

// ... 执行操作 ...

with open(log_file, 'r', encoding='utf-8') as f:
    f.seek(file_size_before)  // ← 跳过旧日志
    new_logs = f.read()        // ← 只读取新的！
```

**经验：** 保存历史！使用 `seek()` 而不是删除！

### 经验 5：直接调用处理程序

**问题：** QTest 并不总是正确工作！

```python
// ❌ 错误：
QTest.mouseMove(window.canvas, QPoint(x, y))
// 可能不调用 mouseMoveEvent！
```

**✅ 正确：** 直接调用处理程序！

```python
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QEvent, QPointF

event = QMouseEvent(
    QEvent.MouseMove, 
    QPointF(x, y), 
    Qt.NoButton, 
    Qt.NoButton, 
    Qt.NoModifier
)
window.canvas.mouseMoveEvent(event)  // ← 直接调用！
app.processEvents()
```

**经验：** 对于 GUI 测试 - 直接调用处理程序，不要通过 QTest！

### 经验 6：Logger 导入（阶段 8）

**问题：** `logging.getLogger(__name__)` 创建未配置的 logger！

```python
// ❌ 错误在 core/undo_commands.py：
import logging
logger = logging.getLogger(__name__)  // __name__ = "core.undo_commands"

// 结果：DEBUG 日志未输出！
[UNDO-CMD] add_element: 0       ← 应该是 1！
[UNDO] undo_add: 0              ← 应该是 1！
```

**✅ 正确：**

```python
// 唯一正确的方法：
from utils.logger import logger

// 结果：所有日志工作正常！
[UNDO-CMD] add_element: 1       ← ✓
[UNDO] undo_add: 1              ← ✓
```

**经验：** 在项目的所有模块中始终使用 `from utils.logger import logger`！不要创建单独的 logger！

---

## 📝 实现前检查清单

### 阶段 1：代码分析（读取）
- [ ] filesystem:read_text_file - 读取了所有需要的文件？
- [ ] 找到了现有方法（没有猜测新方法）？
- [ ] 理解了类结构？
- [ ] 检查了是否有 DEBUG 日志？
- [ ] **检查了 logger 导入 - 是否使用 `from utils.logger import logger`？**

### 阶段 2：添加日志（DEBUG）
- [ ] 在代码中添加了 [功能] 日志？
- [ ] 日志显示所有中间阶段？
- [ ] 模式：`[功能] 操作: 数据`？
- [ ] config.py: CURRENT_LOG_LEVEL = 'DEBUG'？
- [ ] **关键：到处使用 `from utils.logger import logger`，而不是 `logging.getLogger()`！**

### 阶段 3：实现（编辑）
- [ ] filesystem:edit_file 带有确切的 oldText？
- [ ] 通过 filesystem:read_text_file 检查了结果？
- [ ] 在 Qt 操作之前保存了数据？
- [ ] 使用了真实的 API 方法？

### 阶段 4：智能测试（测试）
- [ ] 创建了 LogAnalyzer 类？
- [ ] 检测最少 2-3 种问题类型？
- [ ] 使用了 file_size_before？
- [ ] 直接调用处理程序（不是 QTest）？
- [ ] 创建了运行器脚本？

### 阶段 5：验证（验证）
- [ ] 通过 exec(open('runner.py').read()) 启动了测试？
- [ ] 退出代码 = 0？
- [ ] LogAnalyzer 检测到 0 个问题？
- [ ] **DEBUG 日志输出到控制台？**
- [ ] 在 memory 中记录了文档？

---

## 🎯 最终结论

**有效的方法：**
1. 使用 filesystem tools 读取代码 ✓
2. 测试前的 DEBUG 日志 ✓
3. 每个功能的 LogAnalyzer ✓
4. 使用 file_size_before 而不是删除 ✓
5. 直接调用处理程序 ✓
6. 在 Qt 操作之前保存数据 ✓
7. 阅读真实 API 而不是猜测 ✓
8. **在所有模块中使用 `from utils.logger import logger` ✓**

**无效的方法：**
1. 使用 python-runner 读取带有导入的文件 ✗
2. 猜测方法 (refresh) ✗
3. 使用 QTest 进行 GUI 测试 ✗
4. 删除日志文件 ✗
5. 在 removeItem 后使用 self.selected_item ✗
6. 仅检查最终结果 ✗
7. **使用 `logging.getLogger(__name__)` 而不是 `from utils.logger import logger` ✗**

**主要经验：**  
**读取 → DEBUG → 编辑 → 测试 → 验证**  
永远不要猜测 - 阅读真实代码！

**关键：** 始终使用 `from utils.logger import logger`！

---