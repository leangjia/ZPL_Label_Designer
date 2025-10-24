# 🔴 提示：线段元素 - 双端点网格吸附 + 智能测试

**问题背景：**

项目: 1C_Zebra - ZPL标签设计器 (`D:\AiKlientBank\1C_Zebra\`)

**BUG:** 线段元素在拖拽时 end point (x2, y2) 不吸附到网格。只有 start point 吸附！

**截图：** 从 x=10mm 到 x=25mm 的线段视觉上不在网格交点上。

**问题代码：**
```python
# core/elements/shape_element.py, GraphicsLineItem.itemChange()
# Line 有更复杂的吸附逻辑 - 吸附两个端点
# 这里是简化版本 - 只吸附起点 ← 简化 = BUG！
```

---

## 🎯 目标

修复线段网格吸附，使：
1. **起点 (x, y) 吸附** ✓ (已工作)
2. **终点 (x2, y2) 吸附** ✗ (不工作 - 需要修复)
3. **属性面板显示吸附后的坐标**
4. **ZPL 生成精确** 使用吸附后的坐标

---

## 📋 分步计划 (5个阶段)

### ✅ 阶段 0: 必须 - 读取 MEMORY

**操作：**
```xml
<invoke name="memory:read_graph"/>
<invoke name="memory:search_nodes">
<parameter name="query">1C_Zebra Critical Rules Line Smart Testing Logger</parameter>
</invoke>
```

**应用关键规则：**
- Logger 只使用 `from utils.logger import logger` (不要用 logging.getLogger!)
- 使用文件系统工具读写文件
- 必须使用带 LogAnalyzer 的智能测试
- 使用 file_size_before 而不是删除日志
- 使用 exec(open('runner.py').read()) 运行测试

---

### ✅ 阶段 1: 修复吸附 - 双端点

**步骤 1.1: 修改前读取代码**

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py</parameter>
</invoke>
```

**查找：** `class GraphicsLineItem` → `def itemChange()`

**步骤 1.2: 修复 itemChange() - 吸附双端点**

**新逻辑：**
1. `ItemPositionChange`: 吸附起点 (x1, y1) 和终点 (x2, y2) 到网格
2. 重新计算线段向量 = 吸附后终点 - 吸附后起点 (相对坐标)
3. `setLine(0, 0, new_vector_x, new_vector_y)` 更新向量
4. `ItemPositionHasChanged`: 保存吸附后的坐标到 element.config

**关键代码 (用于 edit_file)：**

```python
def itemChange(self, change, value):
    """线段双端点网格吸附"""
    if change == QGraphicsItem.ItemPositionChange:
        new_pos = value
        
        # 起点毫米坐标
        x1_mm = self._px_to_mm(new_pos.x())
        y1_mm = self._px_to_mm(new_pos.y())
        
        logger.debug(f"[LINE-DRAG] 吸附前起点: ({x1_mm:.2f}, {y1_mm:.2f})mm")
        
        # 终点毫米坐标 (绝对坐标 = 起点 + 向量)
        line_vector = self.line()
        x2_mm = self._px_to_mm(new_pos.x() + line_vector.x2())
        y2_mm = self._px_to_mm(new_pos.y() + line_vector.y2())
        
        logger.debug(f"[LINE-DRAG] 吸附前终点: ({x2_mm:.2f}, {y2_mm:.2f})mm")
        
        # 发射光标位置信号
        if self.canvas:
            self.canvas.cursor_position_changed.emit(x1_mm, y1_mm)
        
        if self.snap_enabled:
            # 吸附双端点！
            snapped_x1 = self._snap_to_grid(x1_mm, 'x')
            snapped_y1 = self._snap_to_grid(y1_mm, 'y')
            snapped_x2 = self._snap_to_grid(x2_mm, 'x')
            snapped_y2 = self._snap_to_grid(y2_mm, 'y')
            
            logger.debug(f"[LINE-SNAP] 起点: ({x1_mm:.2f}, {y1_mm:.2f}) -> ({snapped_x1:.2f}, {snapped_y1:.2f})mm")
            logger.debug(f"[LINE-SNAP] 终点: ({x2_mm:.2f}, {y2_mm:.2f}) -> ({snapped_x2:.2f}, {snapped_y2:.2f})mm")
            
            # 新起点位置
            snapped_pos = QPointF(
                self._mm_to_px(snapped_x1),
                self._mm_to_px(snapped_y1)
            )
            
            # 新线段向量 RELATIVE (吸附后终点 - 吸附后起点)
            new_vector_x_px = self._mm_to_px(snapped_x2 - snapped_x1)
            new_vector_y_px = self._mm_to_px(snapped_y2 - snapped_y1)
            
            # 关键：更新线段向量！
            self.setLine(0, 0, new_vector_x_px, new_vector_y_px)
            
            logger.debug(f"[LINE-SNAP] 新向量: ({new_vector_x_px:.2f}, {new_vector_y_px:.2f})px")
            
            return snapped_pos
        
        return new_pos
    
    elif change == QGraphicsItem.ItemPositionHasChanged:
        # 保存吸附后的坐标
        line_vector = self.line()
        x1_mm = self._px_to_mm(self.pos().x())
        y1_mm = self._px_to_mm(self.pos().y())
        x2_mm = self._px_to_mm(self.pos().x() + line_vector.x2())
        y2_mm = self._px_to_mm(self.pos().y() + line_vector.y2())
        
        logger.debug(f"[LINE-FINAL] 起点: ({x1_mm:.2f}, {y1_mm:.2f})mm")
        logger.debug(f"[LINE-FINAL] 终点: ({x2_mm:.2f}, {y2_mm:.2f})mm")
        
        self.element.config.x = x1_mm
        self.element.config.y = y1_mm
        self.element.config.x2 = x2_mm
        self.element.config.y2 = y2_mm
        
        logger.debug(f"[LINE-FINAL] 已保存: 起点=({x1_mm:.2f}, {y1_mm:.2f}), 终点=({x2_mm:.2f}, {y2_mm:.2f})mm")
        
        if self.canvas and getattr(self.canvas, 'bounds_update_callback', None) and self.isSelected():
            self.canvas.bounds_update_callback(self)
    
    return super().itemChange(change, value)
```

**应用：**
```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py</parameter>
<parameter name="edits">[{
  "oldText": "[从文件中提取的确切旧代码 itemChange]",
  "newText": "[上面的新代码]"
}]</parameter>
</invoke>
```

**步骤 1.3: 验证更改**

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py</parameter>
<parameter name="head">50</parameter>
</invoke>
```

**成功标准：**
- ✅ `[LINE-DRAG] 吸附前起点` 日志
- ✅ `[LINE-DRAG] 吸附前终点` 日志
- ✅ `[LINE-SNAP] 起点: ...` 日志
- ✅ `[LINE-SNAP] 终点: ...` 日志
- ✅ `setLine(0, 0, new_vector_x, new_vector_y)` 代码
- ✅ `[LINE-FINAL] 已保存` 日志

---

### ✅ 阶段 2: 智能测试 - 线段双端点吸附

**步骤 2.1: 创建 LogAnalyzer**

**文件：** `tests/test_line_snap_both_ends_smart.py`

```python
# -*- coding: utf-8 -*-
"""线段双端点网格吸附智能测试"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent, QEvent
from gui.main_window import MainWindow
from core.elements.shape_element import LineElement, LineConfig
from utils.logger import logger
import re


class LineSnapBothEndsAnalyzer:
    """线段双端点吸附日志分析器"""
    
    @staticmethod
    def parse_line_snap_logs(log_content):
        """解析线段吸附日志"""
        
        # [LINE-DRAG] 吸附前起点: (10.45, 10.23)mm
        start_before = re.findall(
            r'\[LINE-DRAG\] 吸附前起点: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-DRAG] 吸附前终点: (25.67, 10.89)mm
        end_before = re.findall(
            r'\[LINE-DRAG\] 吸附前终点: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-SNAP] 起点: (10.45, 10.23) -> (10.00, 10.00)mm
        start_snap = re.findall(
            r'\[LINE-SNAP\] 起点: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-SNAP] 终点: (25.67, 10.89) -> (25.00, 11.00)mm
        end_snap = re.findall(
            r'\[LINE-SNAP\] 终点: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-FINAL] 起点: (10.00, 10.00)mm
        final_start = re.findall(
            r'\[LINE-FINAL\] 起点: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-FINAL] 终点: (25.00, 11.00)mm
        final_end = re.findall(
            r'\[LINE-FINAL\] 终点: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        return {
            'start_before': [(float(m[0]), float(m[1])) for m in start_before],
            'end_before': [(float(m[0]), float(m[1])) for m in end_before],
            'start_snap': [
                {'before': (float(m[0]), float(m[1])), 'after': (float(m[2]), float(m[3]))}
                for m in start_snap
            ],
            'end_snap': [
                {'before': (float(m[0]), float(m[1])), 'after': (float(m[2]), float(m[3]))}
                for m in end_snap
            ],
            'final_start': [(float(m[0]), float(m[1])) for m in final_start],
            'final_end': [(float(m[0]), float(m[1])) for m in final_end]
        }
    
    @staticmethod
    def detect_issues(logs_dict, grid_size=1.0):
        """检测5种问题类型"""
        issues = []
        
        # 1. 终点吸附未发生 (end_snap 日志为空)
        if not logs_dict['end_snap']:
            issues.append({
                'type': 'END_SNAP_NOT_APPLIED',
                'desc': f"终点吸附日志缺失 - 吸附只对起点起作用！"
            })
            return issues  # 无需继续检查
        
        # 2. 起点吸附不正确 (吸附后坐标不是 grid_size 的倍数)
        if logs_dict['start_snap']:
            start_snapped = logs_dict['start_snap'][-1]['after']
            if start_snapped[0] % grid_size > 0.01 or start_snapped[1] % grid_size > 0.01:
                issues.append({
                    'type': 'START_SNAP_NOT_ON_GRID',
                    'desc': f"起点吸附到 ({start_snapped[0]}, {start_snapped[1]}) 但不是 {grid_size}mm 的倍数"
                })
        
        # 3. 终点吸附不正确 (吸附后坐标不是 grid_size 的倍数)
        if logs_dict['end_snap']:
            end_snapped = logs_dict['end_snap'][-1]['after']
            if end_snapped[0] % grid_size > 0.01 or end_snapped[1] % grid_size > 0.01:
                issues.append({
                    'type': 'END_SNAP_NOT_ON_GRID',
                    'desc': f"终点吸附到 ({end_snapped[0]}, {end_snapped[1]}) 但不是 {grid_size}mm 的倍数"
                })
        
        # 4. 吸附结果 != 最终结果 (吸附显示一个值，最终结果是另一个)
        if logs_dict['start_snap'] and logs_dict['final_start']:
            start_snap_result = logs_dict['start_snap'][-1]['after']
            final_start_result = logs_dict['final_start'][-1]
            if abs(start_snap_result[0] - final_start_result[0]) > 0.01 or \
               abs(start_snap_result[1] - final_start_result[1]) > 0.01:
                issues.append({
                    'type': 'START_SNAP_FINAL_MISMATCH',
                    'desc': f"起点吸附={start_snap_result}, 最终={final_start_result} - 不匹配！"
                })
        
        if logs_dict['end_snap'] and logs_dict['final_end']:
            end_snap_result = logs_dict['end_snap'][-1]['after']
            final_end_result = logs_dict['final_end'][-1]
            if abs(end_snap_result[0] - final_end_result[0]) > 0.01 or \
               abs(end_snap_result[1] - final_end_result[1]) > 0.01:
                issues.append({
                    'type': 'END_SNAP_FINAL_MISMATCH',
                    'desc': f"终点吸附={end_snap_result}, 最终={final_end_result} - 不匹配！"
                })
        
        # 5. 最终结果不在网格上 (最终坐标不是 grid_size 的倍数)
        if logs_dict['final_start']:
            final_s = logs_dict['final_start'][-1]
            if final_s[0] % grid_size > 0.01 or final_s[1] % grid_size > 0.01:
                issues.append({
                    'type': 'FINAL_START_NOT_ON_GRID',
                    'desc': f"最终起点 ({final_s[0]}, {final_s[1]}) 不在 {grid_size}mm 网格上"
                })
        
        if logs_dict['final_end']:
            final_e = logs_dict['final_end'][-1]
            if final_e[0] % grid_size > 0.01 or final_e[1] % grid_size > 0.01:
                issues.append({
                    'type': 'FINAL_END_NOT_ON_GRID',
                    'desc': f"最终终点 ({final_e[0]}, {final_e[1]}) 不在 {grid_size}mm 网格上"
                })
        
        return issues


def test_line_snap_both_ends():
    """线段双端点吸附智能测试"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("=" * 60)
    print("[测试] 线段网格吸附 - 双端点")
    print("=" * 60)
    
    # 测试：创建线段并拖拽触发吸附
    print("\n[测试 1] 创建线段并拖拽触发吸附")
    
    # 创建线段元素：起点 (9.55, 9.67), 终点 (24.89, 10.23)
    config = LineConfig(x=9.55, y=9.67, x2=24.89, y2=10.23, thickness=1.0, color='black')
    line = LineElement(config)
    
    # 添加到画布
    from core.elements.shape_element import GraphicsLineItem
    graphics_line = GraphicsLineItem(line, dpi=203, canvas=window.canvas)
    window.canvas.scene.addItem(graphics_line)
    window.elements.append(line)
    window.graphics_items.append(graphics_line)
    
    app.processEvents()
    
    print(f"  拖拽前: 起点=({line.config.x:.2f}, {line.config.y:.2f}), 终点=({line.config.x2:.2f}, {line.config.y2:.2f})mm")
    
    # 通过 itemChange 模拟拖拽 (移动1px触发吸附)
    from PySide6.QtWidgets import QGraphicsItem
    new_pos = QPointF(graphics_line.pos().x() + 1.0, graphics_line.pos().y() + 1.0)
    snapped_pos = graphics_line.itemChange(QGraphicsItem.ItemPositionChange, new_pos)
    
    if snapped_pos != new_pos:
        graphics_line.setPos(snapped_pos)
        graphics_line.itemChange(QGraphicsItem.ItemPositionHasChanged, None)
    
    app.processEvents()
    
    print(f"  拖拽后: 起点=({line.config.x:.2f}, {line.config.y:.2f}), 终点=({line.config.x2:.2f}, {line.config.y2:.2f})mm")
    
    # 读取日志
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 分析
    analyzer = LineSnapBothEndsAnalyzer()
    logs = analyzer.parse_line_snap_logs(new_logs)
    issues = analyzer.detect_issues(logs, grid_size=1.0)
    
    # 结果
    print("\n" + "=" * 60)
    print("[线段双端点吸附] 日志分析")
    print("=" * 60)
    print(f"起点吸附日志: {len(logs['start_snap'])}")
    print(f"终点吸附日志: {len(logs['end_snap'])}")
    print(f"最终起点日志: {len(logs['final_start'])}")
    print(f"最终终点日志: {len(logs['final_end'])}")
    
    if issues:
        print(f"\n检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[失败] 线段吸附存在问题")
        return 1
    
    print("\n[成功] 线段双端点吸附工作正常")
    
    # 最终验证
    assert line.config.x % 1.0 < 0.01, f"起点 X {line.config.x} 应该是 1mm 的倍数"
    assert line.config.y % 1.0 < 0.01, f"起点 Y {line.config.y} 应该是 1mm 的倍数"
    assert line.config.x2 % 1.0 < 0.01, f"终点 X {line.config.x2} 应该是 1mm 的倍数"
    assert line.config.y2 % 1.0 < 0.01, f"终点 Y {line.config.y2} 应该是 1mm 的倍数"
    
    print(f"\n最终验证:")
    print(f"  起点: ({line.config.x:.2f}, {line.config.y:.2f})mm 在网格上 ✓")
    print(f"  终点: ({line.config.x2:.2f}, {line.config.y2:.2f})mm 在网格上 ✓")
    
    return 0


if __name__ == "__main__":
    exit(test_line_snap_both_ends())
```

**创建文件：**
```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\test_line_snap_both_ends_smart.py</parameter>
<parameter name="content">[上面的代码]</parameter>
</invoke>
```

**步骤 2.2: 创建运行器**

**文件：** `tests/run_line_snap_both_ends_test.py`

```python
# -*- coding: utf-8 -*-
"""test_line_snap_both_ends_smart.py 运行器"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_line_snap_both_ends_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"\n退出代码: {result.returncode}")
```

**创建：**
```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_line_snap_both_ends_test.py</parameter>
<parameter name="content">[上面的代码]</parameter>
</invoke>
```

---

### ✅ 阶段 3: 运行测试

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_line_snap_both_ends_test.py').read())
```

**成功标准：**
- ✅ 退出代码 = 0
- ✅ 终点吸附日志 > 0
- ✅ 检测到 0 个问题
- ✅ 最终坐标在网格上 (1mm 的倍数)

**如果失败：**
1. 读取 STDERR 日志 - 查看问题所在
2. 修复 itemChange() 代码
3. 重复测试

---

### ✅ 阶段 4: GUI 验证 (手动测试)

**操作：**
1. 运行 `python main.py`
2. 添加线段元素 (侧边栏 → Line)
3. 拖拽线段 - 验证双端点都吸附到网格
4. 属性面板 - 验证坐标是 1mm 的倍数

---

### ✅ 阶段 5: 文档

**更新 memory：**
```xml
<invoke name="memory:add_observations">
<parameter name="observations">[{
  "entityName": "1C_Zebra 项目",
  "contents": [
    "线段元素吸附修复完成 2025-10-06 - 退出代码 0",
    "GraphicsLineItem.itemChange() 现在吸附双端点: 起点 (x, y) 和终点 (x2, y2)",
    "吸附公式: nearest = offset + round((value-offset)/size)*size 分别应用于起点和终点",
    "吸附后重新计算线段向量: new_vector = 吸附后终点 - 吸附后起点 (相对坐标)",
    "DEBUG 日志: [LINE-DRAG], [LINE-SNAP], [LINE-FINAL] 显示所有吸附阶段",
    "智能测试 test_line_snap_both_ends_smart.py 带 LineSnapBothEndsAnalyzer - 退出代码 0",
    "LogAnalyzer 检测5种问题类型: END_SNAP_NOT_APPLIED, *_SNAP_NOT_ON_GRID, SNAP_FINAL_MISMATCH, FINAL_NOT_ON_GRID",
    "测试结果: 起点和终点都正确吸附到网格，所有坐标都是 grid_size 的倍数",
    "修改的文件: core/elements/shape_element.py (GraphicsLineItem.itemChange 方法)"
  ]
}]</parameter>
</invoke>
```

---

## 🎯 最终检查清单

- [ ] 通过 read_graph() 读取 memory
- [ ] 应用关键规则 (logger import, 文件系统工具)
- [ ] 修复 itemChange() - 吸附双端点
- [ ] 添加 DEBUG 日志: [LINE-DRAG], [LINE-SNAP], [LINE-FINAL]
- [ ] 创建带 LineSnapBothEndsAnalyzer 的智能测试
- [ ] 创建运行器
- [ ] 通过 exec() 运行测试 - 退出代码 = 0
- [ ] LogAnalyzer 未发现问题 (0 issues)
- [ ] GUI 手动测试 - 线段正确吸附
- [ ] 通过 add_observations 更新 memory
- [ ] config.py: CURRENT_LOG_LEVEL = 'DEBUG' 在测试期间

---

**关键：**
- 不要猜测 - 通过 filesystem:read_text_file 读取真实代码
- 必须使用带 LogAnalyzer 的智能测试
- 使用 file_size_before 而不是删除日志
- 在所有模块中使用 `from utils.logger import logger`