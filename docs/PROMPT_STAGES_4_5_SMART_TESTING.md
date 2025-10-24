# 🎯 AI提示：第4-5阶段画布功能与智能测试

**作者：** 拥有10年以上经验的资深软件工程师  
**项目：** 1C_Zebra ZPL标签设计器  
**路径：** `D:\AiKlientBank\1C_Zebra\`

---

## 🔴 关键规则 #1 - 回复前检查

**每次回复前必须：**

```
✋ 停止 - 不要立即发送！

🔍 检查：
   □ 开发者能否无需猜测即可实现？
   □ GUI结构是否完整？
   □ 坐标逻辑是否详细？
   □ 是否添加了DEBUG日志？
   □ 是否创建了LogAnalyzer？

📊 扫描遗漏：
   • 缺少DEBUG日志 → 添加
   • 逻辑碎片化 → 输出完整系统
   • Canvas/GUI没有智能测试 → 创建LogAnalyzer

✅ 完整性：
   修改部分 → 输出整个系统，不要只输出片段！
```

---

## 📋 工作算法

### 对于每个步骤：

```
1. filesystem:read_text_file - 修改前读取文件
2. filesystem:edit_file - 精确更改 (oldText→newText)  
3. filesystem:read_text_file (head:20) - 检查结果
4. 在代码中添加DEBUG日志（如果没有）
5. 创建带LogAnalyzer的智能测试
6. 创建运行器脚本
7. 通过exec(open().read())运行
8. 停止点 - 检查结果
9. 在memory中记录文档
```

---

## 🚀 阶段4：元素边界高亮

### 目标
在标尺上用蓝色半透明矩形高亮显示选中元素的边界

---

### 步骤4.1：在RulerWidget中添加DEBUG日志和边界

#### 4.1.1 在rulers.py中添加DEBUG日志

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\rulers.py</parameter>
</invoke>
```

#### 4.1.2 添加边界高亮

```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\rulers.py</parameter>
<parameter name="edits">[
  {
    "oldText": "        # Cursor tracking\n        self.cursor_pos_mm = None\n        self.show_cursor = False",
    "newText": "        # Cursor tracking\n        self.cursor_pos_mm = None\n        self.show_cursor = False\n        \n        # Element bounds highlighting\n        self.highlighted_bounds = None  # (start_mm, width_mm)"
  },
  {
    "oldText": "    def paintEvent(self, event):\n        \"\"\"Отрисовка линейки\"\"\"\n        painter = QPainter(self)\n        painter.setRenderHint(QPainter.Antialiasing)\n        \n        # Фон\n        painter.fillRect(self.rect(), self.bg_color)\n        \n        # Деления\n        self._draw_ticks(painter)\n        \n        # Малюємо cursor marker\n        if self.show_cursor and self.cursor_pos_mm is not None:\n            self._draw_cursor_marker(painter)\n        \n        painter.end()",
    "newText": "    def paintEvent(self, event):\n        \"\"\"Отрисовка линейки\"\"\"\n        painter = QPainter(self)\n        painter.setRenderHint(QPainter.Antialiasing)\n        \n        # Фон\n        painter.fillRect(self.rect(), self.bg_color)\n        \n        # Деления\n        self._draw_ticks(painter)\n        \n        # Малюємо highlighted bounds\n        if self.highlighted_bounds:\n            self._draw_bounds_highlight(painter)\n        \n        # Малюємо cursor marker\n        if self.show_cursor and self.cursor_pos_mm is not None:\n            self._draw_cursor_marker(painter)\n        \n        painter.end()"
  },
  {
    "oldText": "    def update_scale(self, scale_factor):",
    "newText": "    def highlight_bounds(self, start_mm, width_mm):\n        \"\"\"高亮显示元素边界\"\"\"\n        orientation_name = \"H\" if self.orientation == Qt.Horizontal else \"V\"\n        logger.debug(f\"[BOUNDS-{orientation_name}] 高亮: start={start_mm:.2f}mm, width={width_mm:.2f}mm\")\n        self.highlighted_bounds = (start_mm, width_mm)\n        self.update()\n    \n    def clear_highlight(self):\n        \"\"\"清除高亮\"\"\"\n        orientation_name = \"H\" if self.orientation == Qt.Horizontal else \"V\"\n        logger.debug(f\"[BOUNDS-{orientation_name}] 清除高亮\")\n        self.highlighted_bounds = None\n        self.update()\n    \n    def _draw_bounds_highlight(self, painter):\n        \"\"\"绘制边界高亮\"\"\"\n        start_mm, width_mm = self.highlighted_bounds\n        \n        start_px = int(self._mm_to_px(start_mm) * self.scale_factor)\n        width_px = int(self._mm_to_px(width_mm) * self.scale_factor)\n        \n        orientation_name = \"H\" if self.orientation == Qt.Horizontal else \"V\"\n        logger.debug(f\"[BOUNDS-{orientation_name}] 绘制: start_px={start_px}, width_px={width_px}\")\n        \n        # 半透明蓝色矩形\n        color = QColor(100, 150, 255, 80)\n        \n        if self.orientation == Qt.Horizontal:\n            rect = QRect(start_px, 0, width_px, self.ruler_thickness)\n        else:\n            rect = QRect(0, start_px, self.ruler_thickness, width_px)\n        \n        painter.fillRect(rect, color)\n        \n        # 边框\n        pen = QPen(QColor(50, 100, 255), 1)\n        painter.setPen(pen)\n        painter.drawRect(rect)\n    \n    def update_scale(self, scale_factor):"
  }
]</parameter>
</invoke>
```

#### 4.1.3 验证

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\rulers.py</parameter>
<parameter name="head">60</parameter>
</invoke>
```

**✅ 步骤4.1成功标准：**
- [ ] 添加了变量 `highlighted_bounds`
- [ ] 添加了DEBUG日志 `[BOUNDS-H/V]`
- [ ] 创建了方法 `highlight_bounds`
- [ ] 创建了方法 `clear_highlight`
- [ ] 创建了方法 `_draw_bounds_highlight`

---

### 步骤4.2：在MainWindow中集成边界

#### 4.2.1 读取main_window.py

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
</invoke>
```

#### 4.2.2 更新_on_selection_changed

```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
<parameter name="edits">[
  {
    "oldText": "    def _on_selection_changed(self):\n        \"\"\"Обробка зміни виділення\"\"\"\n        selected = self.canvas.scene.selectedItems()\n        \n        if selected:\n            item = selected[0]\n            element = item.element\n            \n            # Оновити property panel\n            self.property_panel.set_element(element, item)\n            \n            # Зберегти виділений item\n            self.selected_item = item\n            logger.info(f\"Element selected: {element.config.x}mm, {element.config.y}mm\")\n        else:\n            self.property_panel.set_element(None, None)\n            self.selected_item = None\n            logger.info(\"Selection cleared\")",
    "newText": "    def _on_selection_changed(self):\n        \"\"\"处理选择变化\"\"\"\n        selected = self.canvas.scene.selectedItems()\n        \n        if selected:\n            item = selected[0]\n            element = item.element\n            \n            # 更新属性面板\n            self.property_panel.set_element(element, item)\n            \n            # 在标尺上高亮边界\n            self._highlight_element_bounds(item)\n            \n            # 保存选中的item\n            self.selected_item = item\n            logger.info(f\"Element selected: {element.config.x}mm, {element.config.y}mm\")\n        else:\n            # 清除高亮\n            self.h_ruler.clear_highlight()\n            self.v_ruler.clear_highlight()\n            self.property_panel.set_element(None, None)\n            self.selected_item = None\n            logger.info(\"Selection cleared\")"
  },
  {
    "oldText": "    def eventFilter(self, obj, event):",
    "newText": "    def _highlight_element_bounds(self, item):\n        \"\"\"在标尺上高亮显示元素边界\"\"\"\n        if hasattr(item, 'element'):\n            element = item.element\n            x = element.config.x\n            y = element.config.y\n            \n            # 从boundingRect获取尺寸\n            bounds = item.boundingRect()\n            width_px = bounds.width()\n            height_px = bounds.height()\n            \n            # 转换为毫米\n            dpi = 203\n            width_mm = width_px * 25.4 / dpi\n            height_mm = height_px * 25.4 / dpi\n            \n            logger.debug(f\"[BOUNDS] 元素位置: x={x:.2f}mm, y={y:.2f}mm\")\n            logger.debug(f\"[BOUNDS] 尺寸: width={width_mm:.2f}mm, height={height_mm:.2f}mm\")\n            \n            # 在标尺上高亮显示\n            self.h_ruler.highlight_bounds(x, width_mm)\n            self.v_ruler.highlight_bounds(y, height_mm)\n            logger.info(f\"高亮边界: X={x}mm W={width_mm:.1f}mm, Y={y}mm H={height_mm:.1f}mm\")\n    \n    def eventFilter(self, obj, event):"
  }
]</parameter>
</invoke>
```

**✅ 步骤4.2成功标准：**
- [ ] 创建了方法 `_highlight_element_bounds`
- [ ] 添加了DEBUG日志 `[BOUNDS]`
- [ ] 更新了 `_on_selection_changed`
- [ ] 取消选择时调用 `clear_highlight()`

---

### 步骤4.3：阶段4的智能测试

#### 4.3.1 创建带LogAnalyzer的测试

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\test_bounds_smart.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""智能测试：元素边界高亮与日志分析"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


class BoundsLogAnalyzer:
    """边界高亮日志分析器"""
    
    @staticmethod
    def parse_bounds_logs(log):
        """[BOUNDS] 元素位置和尺寸"""
        element_at = re.findall(r'\[BOUNDS\] 元素位置: x=([\d.]+)mm, y=([\d.]+)mm', log)
        size = re.findall(r'\[BOUNDS\] 尺寸: width=([\d.]+)mm, height=([\d.]+)mm', log)
        
        return {
            'element_at': [(float(m[0]), float(m[1])) for m in element_at],
            'size': [(float(m[0]), float(m[1])) for m in size]
        }
    
    @staticmethod
    def parse_ruler_bounds_logs(log):
        """[BOUNDS-H/V] 高亮和绘制日志"""
        h_highlight = re.findall(r'\[BOUNDS-H\] 高亮: start=([\d.]+)mm, width=([\d.]+)mm', log)
        v_highlight = re.findall(r'\[BOUNDS-V\] 高亮: start=([\d.]+)mm, width=([\d.]+)mm', log)
        h_draw = re.findall(r'\[BOUNDS-H\] 绘制: start_px=([\d.]+), width_px=([\d.]+)', log)
        v_draw = re.findall(r'\[BOUNDS-V\] 绘制: start_px=([\d.]+), width_px=([\d.]+)', log)
        clear_h = re.findall(r'\[BOUNDS-H\] 清除高亮', log)
        clear_v = re.findall(r'\[BOUNDS-V\] 清除高亮', log)
        
        return {
            'h_highlight': [(float(m[0]), float(m[1])) for m in h_highlight],
            'v_highlight': [(float(m[0]), float(m[1])) for m in v_highlight],
            'h_draw': [(int(m[0]), int(m[1])) for m in h_draw],
            'v_draw': [(int(m[0]), int(m[1])) for m in v_draw],
            'clear_h': len(clear_h),
            'clear_v': len(clear_v)
        }
    
    @staticmethod
    def detect_issues(bounds_logs, ruler_logs):
        """检测边界高亮问题"""
        issues = []
        
        # 1. BOUNDS != RULER HIGHLIGHT
        if bounds_logs['element_at'] and ruler_logs['h_highlight']:
            element_x = bounds_logs['element_at'][-1][0]
            element_y = bounds_logs['element_at'][-1][1]
            ruler_h_start = ruler_logs['h_highlight'][-1][0]
            ruler_v_start = ruler_logs['v_highlight'][-1][0]
            
            if abs(element_x - ruler_h_start) > 0.1:
                issues.append({
                    'type': 'BOUNDS_RULER_MISMATCH_H',
                    'desc': f'元素X={element_x:.2f}mm, 标尺H起点={ruler_h_start:.2f}mm'
                })
            
            if abs(element_y - ruler_v_start) > 0.1:
                issues.append({
                    'type': 'BOUNDS_RULER_MISMATCH_V',
                    'desc': f'元素Y={element_y:.2f}mm, 标尺V起点={ruler_v_start:.2f}mm'
                })
        
        # 2. 尺寸 != 标尺宽度
        if bounds_logs['size'] and ruler_logs['h_highlight']:
            element_width = bounds_logs['size'][-1][0]
            element_height = bounds_logs['size'][-1][1]
            ruler_width = ruler_logs['h_highlight'][-1][1]
            ruler_height = ruler_logs['v_highlight'][-1][1]
            
            if abs(element_width - ruler_width) > 0.5:
                issues.append({
                    'type': 'SIZE_WIDTH_MISMATCH',
                    'desc': f'元素宽度={element_width:.2f}mm, 标尺宽度={ruler_width:.2f}mm'
                })
            
            if abs(element_height - ruler_height) > 0.5:
                issues.append({
                    'type': 'SIZE_HEIGHT_MISMATCH',
                    'desc': f'元素高度={element_height:.2f}mm, 标尺高度={ruler_height:.2f}mm'
                })
        
        # 3. 标尺高亮 != 绘制
        if ruler_logs['h_highlight'] and ruler_logs['h_draw']:
            highlight_start = ruler_logs['h_highlight'][-1][0]
            highlight_width = ruler_logs['h_highlight'][-1][1]
            drawn_start = ruler_logs['h_draw'][-1][0]
            drawn_width = ruler_logs['h_draw'][-1][1]
            
            # 转换毫米 -> 像素
            dpi = 203
            scale = 2.5
            expected_start_px = int(highlight_start * dpi / 25.4 * scale)
            expected_width_px = int(highlight_width * dpi / 25.4 * scale)
            
            if abs(drawn_start - expected_start_px) > 2:
                issues.append({
                    'type': 'DRAW_START_INCORRECT',
                    'desc': f'预期起点={expected_start_px}px, 绘制起点={drawn_start}px'
                })
            
            if abs(drawn_width - expected_width_px) > 2:
                issues.append({
                    'type': 'DRAW_WIDTH_INCORRECT',
                    'desc': f'预期宽度={expected_width_px}px, 绘制宽度={drawn_width}px'
                })
        
        return issues


def test_bounds_smart():
    """边界高亮智能测试与日志分析"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 测试前的文件大小
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 模拟：添加文本元素
    window._add_text()
    app.processEvents()
    
    # 选择元素
    item = window.graphics_items[0]
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    # 读取新日志
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 分析
    analyzer = BoundsLogAnalyzer()
    bounds_logs = analyzer.parse_bounds_logs(new_logs)
    ruler_logs = analyzer.parse_ruler_bounds_logs(new_logs)
    issues = analyzer.detect_issues(bounds_logs, ruler_logs)
    
    print("=" * 60)
    print("[阶段4] 元素边界 - 日志分析")
    print("=" * 60)
    print(f"\n[BOUNDS] 元素位置: {len(bounds_logs['element_at'])}")
    print(f"[BOUNDS] 尺寸: {len(bounds_logs['size'])}")
    print(f"[RULER-H] 高亮: {len(ruler_logs['h_highlight'])}")
    print(f"[RULER-V] 高亮: {len(ruler_logs['v_highlight'])}")
    print(f"[RULER-H] 绘制: {len(ruler_logs['h_draw'])}")
    print(f"[RULER-V] 绘制: {len(ruler_logs['v_draw'])}")
    
    if bounds_logs['element_at']:
        pos = bounds_logs['element_at'][-1]
        print(f"元素位置: x={pos[0]:.2f}mm, y={pos[1]:.2f}mm")
    
    if bounds_logs['size']:
        size = bounds_logs['size'][-1]
        print(f"元素尺寸: width={size[0]:.2f}mm, height={size[1]:.2f}mm")
    
    # 测试取消选择（清除）
    print("\n[测试] 取消选择元素...")
    file_size_before_clear = log_file.stat().st_size
    
    window.canvas.scene.clearSelection()
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before_clear)
        clear_logs = f.read()
    
    clear_ruler_logs = analyzer.parse_ruler_bounds_logs(clear_logs)
    print(f"[RULER-H] 清除: {clear_ruler_logs['clear_h']}")
    print(f"[RULER-V] 清除: {clear_ruler_logs['clear_v']}")
    
    if clear_ruler_logs['clear_h'] == 0 or clear_ruler_logs['clear_v'] == 0:
        issues.append({
            'type': 'NO_CLEAR_ON_DESELECT',
            'desc': f"取消选择时标尺未清除 (H={clear_ruler_logs['clear_h']}, V={clear_ruler_logs['clear_v']})"
        })
    
    if issues:
        print(f"\n检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[失败] 边界高亮存在问题")
        print("=" * 60)
        return 1
    
    print("\n[成功] 边界高亮工作正常")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_bounds_smart())
</parameter>
</invoke>
```

#### 4.3.2 创建运行器

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_bounds_smart_test.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""边界高亮智能测试运行器"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_bounds_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)

print(f"\n退出代码: {result.returncode}")
</parameter>
</invoke>
```

#### 4.3.3 运行测试

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_bounds_smart_test.py').read())
```

**✅ 阶段4成功标准：**
- [ ] 控制台中有 `[BOUNDS]` 日志
- [ ] 控制台中有 `[BOUNDS-H/V]` 日志
- [ ] LogAnalyzer检测到0个问题
- [ ] 退出代码: 0
- [ ] 选择时边界高亮显示
- [ ] 取消选择时边界清除

---

### ⏸️ 阶段4停止点

**在以下情况之前不要进入阶段5：**
- [ ] 智能测试未通过 (退出代码 != 0)
- [ ] LogAnalyzer发现问题
- [ ] 边界未高亮显示
- [ ] 取消选择时边界未清除

---

## 🚀 阶段5：高级键盘快捷键

### 目标
实现完整的键盘快捷键集合，支持专业工作流程

---

### 步骤5.1：在MainWindow中添加DEBUG日志和keyPressEvent

#### 5.1.1 更新keyPressEvent

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
</invoke>
```

```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
<parameter name="edits">[
  {
    "oldText": "    def keyPressEvent(self, event):\n        \"\"\"Keyboard shortcuts\"\"\"\n        modifiers = event.modifiers()\n        key = event.key()\n        \n        # === ZOOM ===\n        if modifiers == Qt.ControlModifier:\n            if key in (Qt.Key_Plus, Qt.Key_Equal):\n                self.canvas.zoom_in()\n            elif key == Qt.Key_Minus:\n                self.canvas.zoom_out()\n            elif key == Qt.Key_0:\n                self.canvas.reset_zoom()\n            # === SNAP ===\n            elif key == Qt.Key_G:\n                self.snap_enabled = not self.snap_enabled\n                self._toggle_snap(Qt.Checked if self.snap_enabled else Qt.Unchecked)\n        \n        super().keyPressEvent(event)",
    "newText": "    def keyPressEvent(self, event):\n        \"\"\"键盘快捷键\"\"\"\n        modifiers = event.modifiers()\n        key = event.key()\n        \n        # === 缩放 ===\n        if modifiers == Qt.ControlModifier:\n            if key in (Qt.Key_Plus, Qt.Key_Equal):\n                logger.debug(\"[SHORTCUT] Ctrl+Plus - 放大\")\n                self.canvas.zoom_in()\n            elif key == Qt.Key_Minus:\n                logger.debug(\"[SHORTCUT] Ctrl+Minus - 缩小\")\n                self.canvas.zoom_out()\n            elif key == Qt.Key_0:\n                logger.debug(\"[SHORTCUT] Ctrl+0 - 重置缩放\")\n                self.canvas.reset_zoom()\n            # === 吸附 ===\n            elif key == Qt.Key_G:\n                logger.debug(\"[SHORTCUT] Ctrl+G - 切换吸附\")\n                self.snap_enabled = not self.snap_enabled\n                self._toggle_snap(Qt.Checked if self.snap_enabled else Qt.Unchecked)\n        \n        # === 删除 ===\n        elif key in (Qt.Key_Delete, Qt.Key_Backspace):\n            logger.debug(f\"[SHORTCUT] {event.key()} - 删除元素\")\n            self._delete_selected()\n        \n        # === 精确移动 (Shift + 方向键) ===\n        elif modifiers == Qt.ShiftModifier:\n            if key == Qt.Key_Left:\n                logger.debug(\"[SHORTCUT] Shift+Left - 移动 -0.1mm\")\n                self._move_selected(-0.1, 0)\n            elif key == Qt.Key_Right:\n                logger.debug(\"[SHORTCUT] Shift+Right - 移动 +0.1mm\")\n                self._move_selected(0.1, 0)\n            elif key == Qt.Key_Up:\n                logger.debug(\"[SHORTCUT] Shift+Up - 移动 -0.1mm\")\n                self._move_selected(0, -0.1)\n            elif key == Qt.Key_Down:\n                logger.debug(\"[SHORTCUT] Shift+Down - 移动 +0.1mm\")\n                self._move_selected(0, 0.1)\n        \n        # === 普通移动 (方向键) ===\n        elif modifiers == Qt.NoModifier:\n            if key == Qt.Key_Left:\n                logger.debug(\"[SHORTCUT] Left - 移动 -1mm\")\n                self._move_selected(-1, 0)\n            elif key == Qt.Key_Right:\n                logger.debug(\"[SHORTCUT] Right - 移动 +1mm\")\n                self._move_selected(1, 0)\n            elif key == Qt.Key_Up:\n                logger.debug(\"[SHORTCUT] Up - 移动 -1mm\")\n                self._move_selected(0, -1)\n            elif key == Qt.Key_Down:\n                logger.debug(\"[SHORTCUT] Down - 移动 +1mm\")\n                self._move_selected(0, 1)\n        \n        super().keyPressEvent(event)"
  }
]</parameter>
</invoke>
```

**✅ 步骤5.1成功标准：**
- [ ] 为所有快捷键添加了DEBUG日志 `[SHORTCUT]`
- [ ] 添加了DELETE/BACKSPACE处理
- [ ] 添加了Shift+方向键快捷键
- [ ] 添加了方向键快捷键

---

### 步骤5.2：_move_selected和_delete_selected方法

```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
<parameter name="edits">[
  {
    "oldText": "    def keyPressEvent(self, event):",
    "newText": "    def _move_selected(self, dx_mm, dy_mm):\n        \"\"\"移动选中的元素\"\"\"\n        if self.selected_item and hasattr(self.selected_item, 'element'):\n            element = self.selected_item.element\n            old_x, old_y = element.config.x, element.config.y\n            \n            element.config.x += dx_mm\n            element.config.y += dy_mm\n            \n            logger.debug(f\"[MOVE] 之前: ({old_x:.2f}, {old_y:.2f})mm\")\n            logger.debug(f\"[MOVE] 增量: ({dx_mm:.2f}, {dy_mm:.2f})mm\")\n            logger.debug(f\"[MOVE] 之后: ({element.config.x:.2f}, {element.config.y:.2f})mm\")\n            \n            # 更新图形项位置\n            dpi = 203\n            new_x = element.config.x * dpi / 25.4\n            new_y = element.config.y * dpi / 25.4\n            self.selected_item.setPos(new_x, new_y)\n            \n            # 更新属性面板和边界\n            if self.property_panel.current_element:\n                self.property_panel.refresh()\n            self._highlight_element_bounds(self.selected_item)\n            \n            logger.info(f\"元素移动: dx={dx_mm}mm, dy={dy_mm}mm -> ({element.config.x}, {element.config.y})\")\n    \n    def _delete_selected(self):\n        \"\"\"删除选中的元素\"\"\"\n        if self.selected_item:\n            logger.debug(f\"[DELETE] 从场景中移除元素\")\n            \n            # 从场景中删除\n            self.canvas.scene.removeItem(self.selected_item)\n            \n            # 从列表中删除\n            if hasattr(self.selected_item, 'element'):\n                element = self.selected_item.element\n                if element in self.elements:\n                    self.elements.remove(element)\n                    logger.debug(f\"[DELETE] 从元素列表中移除\")\n            \n            if self.selected_item in self.graphics_items:\n                self.graphics_items.remove(self.selected_item)\n                logger.debug(f\"[DELETE] 从图形项列表中移除\")\n            \n            logger.info(f\"元素已删除\")\n            self.selected_item = None\n            \n            # 清除标尺和属性面板\n            self.h_ruler.clear_highlight()\n            self.v_ruler.clear_highlight()\n            self.property_panel.set_element(None, None)\n            logger.debug(f\"[DELETE] UI已清除\")\n    \n    def keyPressEvent(self, event):"
  }
]</parameter>
</invoke>
```

**✅ 步骤5.2成功标准：**
- [ ] 创建了方法 `_move_selected`
- [ ] 添加了DEBUG日志 `[MOVE]` (之前/增量/之后)
- [ ] 创建了方法 `_delete_selected`
- [ ] 添加了DEBUG日志 `[DELETE]`
- [ ] 属性面板已更新
- [ ] 边界已更新

---

### 步骤5.3：阶段5的智能测试

#### 5.3.1 创建带LogAnalyzer的测试

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\test_shortcuts_smart.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""智能测试：键盘快捷键与日志分析"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from gui.main_window import MainWindow


class ShortcutsLogAnalyzer:
    """键盘快捷键日志分析器"""
    
    @staticmethod
    def parse_shortcut_logs(log):
        """[SHORTCUT] 日志"""
        shortcuts = re.findall(r'\[SHORTCUT\] (.+)', log)
        return shortcuts
    
    @staticmethod
    def parse_move_logs(log):
        """[MOVE] 之前/增量/之后日志"""
        before = re.findall(r'\[MOVE\] 之前: \(([\d.]+), ([\d.]+)\)mm', log)
        delta = re.findall(r'\[MOVE\] 增量: \(([-\d.]+), ([-\d.]+)\)mm', log)
        after = re.findall(r'\[MOVE\] 之后: \(([\d.]+), ([\d.]+)\)mm', log)
        
        return {
            'before': [(float(m[0]), float(m[1])) for m in before],
            'delta': [(float(m[0]), float(m[1])) for m in delta],
            'after': [(float(m[0]), float(m[1])) for m in after]
        }
    
    @staticmethod
    def parse_delete_logs(log):
        """[DELETE] 日志"""
        removing = len(re.findall(r'\[DELETE\] 从场景中移除元素', log))
        from_elements = len(re.findall(r'\[DELETE\] 从元素列表中移除', log))
        from_graphics = len(re.findall(r'\[DELETE\] 从图形项列表中移除', log))
        ui_cleared = len(re.findall(r'\[DELETE\] UI已清除', log))
        
        return {
            'removing': removing,
            'from_elements': from_elements,
            'from_graphics': from_graphics,
            'ui_cleared': ui_cleared
        }
    
    @staticmethod
    def detect_issues(shortcut_logs, move_logs, delete_logs):
        """检测快捷键问题"""
        issues = []
        
        # 1. 移动: 之前 + 增量 != 之后
        if move_logs['before'] and move_logs['delta'] and move_logs['after']:
            before = move_logs['before'][-1]
            delta = move_logs['delta'][-1]
            after = move_logs['after'][-1]
            
            expected_x = before[0] + delta[0]
            expected_y = before[1] + delta[1]
            
            if abs(after[0] - expected_x) > 0.01:
                issues.append({
                    'type': 'MOVE_CALCULATION_ERROR_X',
                    'desc': f'之前={before[0]:.2f} + 增量={delta[0]:.2f} = {expected_x:.2f}, 但之后={after[0]:.2f}'
                })
            
            if abs(after[1] - expected_y) > 0.01:
                issues.append({
                    'type': 'MOVE_CALCULATION_ERROR_Y',
                    'desc': f'之前={before[1]:.2f} + 增量={delta[1]:.2f} = {expected_y:.2f}, 但之后={after[1]:.2f}'
                })
        
        # 2. 删除: 未执行所有步骤
        if delete_logs['removing'] > 0:
            if delete_logs['from_elements'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_NOT_FROM_ELEMENTS',
                    'desc': f\"移除={delete_logs['removing']}, 但从元素列表移除={delete_logs['from_elements']}\"
                })
            
            if delete_logs['from_graphics'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_NOT_FROM_GRAPHICS',
                    'desc': f\"移除={delete_logs['removing']}, 但从图形项列表移除={delete_logs['from_graphics']}\"
                })
            
            if delete_logs['ui_cleared'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_UI_NOT_CLEARED',
                    'desc': f\"移除={delete_logs['removing']}, 但UI清除={delete_logs['ui_cleared']}\"
                })
        
        return issues


def test_shortcuts_smart():
    """快捷键智能测试与日志分析"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 添加元素
    window._add_text()
    app.processEvents()
    
    item = window.graphics_items[0]
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    # ============ 测试移动 ============
    print("=" * 60)
    print("[阶段5] 键盘快捷键 - 日志分析")
    print("=" * 60)
    
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 模拟右方向键 (移动 +1mm)
    key_event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_Right,
        Qt.NoModifier
    )
    window.keyPressEvent(key_event)
    app.processEvents()
    
    # 读取日志
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        move_logs_text = f.read()
    
    analyzer = ShortcutsLogAnalyzer()
    shortcut_logs = analyzer.parse_shortcut_logs(move_logs_text)
    move_logs = analyzer.parse_move_logs(move_logs_text)
    
    print("\n[测试] 右方向键 (+1mm):")
    print(f"检测到的快捷键: {shortcut_logs}")
    print(f"[MOVE] 条目: {len(move_logs['before'])}")
    
    if move_logs['before']:
        print(f"之前: {move_logs['before'][-1]}")
        print(f"增量: {move_logs['delta'][-1]}")
        print(f"之后: {move_logs['after'][-1]}")
    
    # ============ 测试删除 ============
    file_size_before = log_file.stat().st_size
    
    # 模拟删除键
    key_event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_Delete,
        Qt.NoModifier
    )
    window.keyPressEvent(key_event)
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        delete_logs_text = f.read()
    
    delete_logs = analyzer.parse_delete_logs(delete_logs_text)
    
    print(f"\n[测试] 删除:")
    print(f"[DELETE] 移除: {delete_logs['removing']}")
    print(f"[DELETE] 从元素列表移除: {delete_logs['from_elements']}")
    print(f"[DELETE] 从图形项列表移除: {delete_logs['from_graphics']}")
    print(f"[DELETE] UI清除: {delete_logs['ui_cleared']}")
    
    # ============ 问题检测 ============
    issues = analyzer.detect_issues(shortcut_logs, move_logs, delete_logs)
    
    if issues:
        print(f"\n检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[失败] 快捷键存在问题")
        print("=" * 60)
        return 1
    
    print("\n[成功] 键盘快捷键工作正常")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_shortcuts_smart())
</parameter>
</invoke>
```

#### 5.3.2 创建运行器

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_shortcuts_smart_test.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""快捷键智能测试运行器"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_shortcuts_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)

print(f"\n退出代码: {result.returncode}")
</parameter>
</invoke>
```

#### 5.3.3 运行测试

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_shortcuts_smart_test.py').read())
```

**✅ 阶段5成功标准：**
- [ ] 控制台中有 `[SHORTCUT]` 日志
- [ ] 控制台中有 `[MOVE]` 日志 (之前/增量/之后)
- [ ] 控制台中有 `[DELETE]` 日志
- [ ] LogAnalyzer检测到0个问题
- [ ] 退出代码: 0
- [ ] 移动工作正常 (之前 + 增量 = 之后)
- [ ] 删除从所有列表中移除元素

---

### ⏸️ 阶段5停止点

**在以下情况之前不要进入最终集成：**
- [ ] 智能测试未通过 (退出代码 != 0)
- [ ] LogAnalyzer发现问题
- [ ] 移动计算不正确
- [ ] 删除未清除UI

---

## 🎯 最终集成：主测试

### 为阶段4-5创建主运行器

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_stages_4_5_smart.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""主运行器 - 阶段4-5智能测试"""

import subprocess

print("=" * 70)
print(" 主测试运行器 - 阶段4-5画布功能")
print("=" * 70)

tests = [
    ("阶段4: 元素边界", r'tests\test_bounds_smart.py'),
    ("阶段5: 键盘快捷键", r'tests\test_shortcuts_smart.py'),
]

results = []

for stage_name, test_path in tests:
    print(f"\n{'=' * 70}")
    print(f" {stage_name}")
    print('=' * 70)
    
    result = subprocess.run(
        [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', test_path],
        cwd=r'D:\AiKlientBank\1C_Zebra',
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    results.append({
        'stage': stage_name,
        'exit_code': result.returncode,
        'success': result.returncode == 0
    })

# 最终报告
print("\n" + "=" * 70)
print(" 最终结果")
print("=" * 70)

all_passed = True
for r in results:
    status = "[成功]" if r['success'] else "[失败]"
    print(f"{status} {r['stage']} - 退出代码: {r['exit_code']}")
    if not r['success']:
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print(" 所有阶段4-5通过!")
    print(" 准备投入生产")
else:
    print(" 部分阶段失败!")
    print(" 在继续之前修复问题")
print("=" * 70)
</parameter>
</invoke>
```

### 运行主测试

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_stages_4_5_smart.py').read())
```

**✅ 最终标准：**
- [ ] 阶段4: 元素边界 - 退出代码: 0
- [ ] 阶段5: 键盘快捷键 - 退出代码: 0
- [ ] 所有阶段通过!

---

## 📝 在MEMORY中记录文档

```xml
<invoke name="memory:add_observations">
<parameter name="observations">[
  {
    "entityName": "1C_Zebra项目",
    "contents": [
      "阶段4完成: 元素边界高亮与智能测试",
      "RulerWidget: DEBUG日志 [BOUNDS-H/V] 用于高亮/清除/绘制",
      "MainWindow: _highlight_element_bounds 带boundingRect转换",
      "test_bounds_smart.py: BoundsLogAnalyzer 检测 BOUNDS_RULER_MISMATCH, SIZE_MISMATCH, DRAW_INCORRECT",
      "阶段5完成: 高级键盘快捷键与智能测试",
      "MainWindow: DEBUG日志 [SHORTCUT], [MOVE], [DELETE] 用于所有快捷键",
      "keyPressEvent: Delete/Backspace, 方向键 (1mm), Shift+方向键 (0.1mm)",
      "_move_selected: 之前/增量/之后逻辑与属性面板更新",
      "_delete_selected: 从场景、元素、图形项中删除，UI清除",
      "test_shortcuts_smart.py: ShortcutsLogAnalyzer 检测 MOVE_CALCULATION_ERROR, DELETE_NOT_FROM_*",
      "主运行器 run_stages_4_5_smart.py 用于综合测试",
      "所有智能测试使用 file_size_before 读取新日志",
      "每个阶段的LogAnalyzer检测2-4种问题类型",
      "退出代码 0 = 成功, 1 = 发现问题"
    ]
  }
]</parameter>
</invoke>
```

---

## ✅ 阶段4-5完成检查清单

### 阶段4 - 元素边界:
- [✓] 添加了DEBUG日志 `[BOUNDS-H/V]`
- [✓] 变量 `highlighted_bounds`
- [✓] 方法 `highlight_bounds()`, `clear_highlight()`
- [✓] `_draw_bounds_highlight()` 带半透明矩形
- [✓] MainWindow中的 `_highlight_element_bounds()`
- [✓] 与 `_on_selection_changed` 集成
- [✓] BoundsLogAnalyzer带5种问题类型
- [✓] 智能测试 test_bounds_smart.py
- [✓] 运行器 run_bounds_smart_test.py

### 阶段5 - 键盘快捷键:
- [✓] DEBUG日志 `[SHORTCUT]`, `[MOVE]`, `[DELETE]`
- [✓] `keyPressEvent` 带所有快捷键
- [✓] Delete/Backspace处理
- [✓] 方向键 (1mm移动)
- [✓] Shift+方向键 (0.1mm精确移动)
- [✓] `_move_selected()` 带之前/增量/之后
- [✓] `_delete_selected()` 带完全清除
- [✓] 属性面板刷新
- [✓] 移动时边界刷新
- [✓] ShortcutsLogAnalyzer带5种问题类型
- [✓] 智能测试 test_shortcuts_smart.py
- [✓] 运行器 run_shortcuts_smart_test.py

### 最终集成:
- [✓] 主运行器 run_stages_4_5_smart.py
- [✓] 在memory中记录文档
- [✓] 所有测试通过 (退出代码: 0)

---

## 🎉 完成

**阶段4-5已成功实现智能测试！**

项目现在拥有：
- ✅ 标尺上的元素边界高亮
- ✅ 完整的键盘快捷键 (删除, 方向键, Shift+方向键)
- ✅ 每个阶段的智能测试与LogAnalyzer
- ✅ 所有逻辑的DEBUG日志
- ✅ 综合测试的主运行器

**后续步骤（可选）：**
- 上下文菜单（右键操作）
- 智能参考线（与其他元素对齐）
- 撤销/重做系统
- 多选和分组

**文档已在Memory中更新 ✓**

---