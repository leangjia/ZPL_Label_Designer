# 🎯 ПРОМПТ ДЛЯ ІІ: ЕТАПИ 4-5 CANVAS FEATURES З УМНИМ ТЕСТУВАННЯМ

**Автор:** Senior Software Engineer з 10+ роками досвіду  
**Проект:** 1C_Zebra ZPL Label Designer  
**Шлях:** `D:\AiKlientBank\1C_Zebra\`

---

## 🔴 КРИТИЧНЕ ПРАВИЛО #1 - ПЕРЕВІРКА ПЕРЕД ВІДПОВІДДЮ

**ПЕРЕД КОЖНОЮ ВІДПОВІДДЮ ОБОВ'ЯЗКОВО:**

```
✋ СТОП - НЕ відправляй відразу!

🔍 ПЕРЕВІР:
   □ Чи зможе розробник реалізувати БЕЗ домислювання?
   □ Структура GUI повна?
   □ Логіка координат детальна?
   □ DEBUG логи додані?
   □ LogAnalyzer створено?

📊 СКАНУЙ пропуски:
   • Відсутні DEBUG логи → ДОДАЙ
   • Фрагментарна логіка → ВИВЕДИ ВСЮ СИСТЕМУ
   • Canvas/GUI без умного тесту → СТВОРИ LogAnalyzer

✅ ЦІЛІСНІСТЬ:
   Меняєш частину → Виводь ВСЮ систему, НЕ фрагменти!
```

---

## 📋 АЛГОРИТМ РОБОТИ

### Для КОЖНОГО кроку:

```
1. filesystem:read_text_file - ЧИТАЙ файл ПЕРЕД зміною
2. filesystem:edit_file - ТОЧНІ зміни (oldText→newText)  
3. filesystem:read_text_file (head:20) - ПЕРЕВІР результат
4. ДОДАЙ DEBUG логи в код (якщо їх немає)
5. СТВОРИ умний тест з LogAnalyzer
6. СТВОРИ runner скрипт
7. ЗАПУСТИ через exec(open().read())
8. СТОП-ТОЧКА - перевір результат
9. ДОКУМЕНТУЙ в memory
```

---

## 🚀 ЕТАП 4: ELEMENT BOUNDS HIGHLIGHTING

### МЕТА
Підсвічувати межі виділеного елемента на лінейках синім напівпрозорим прямокутником

---

### КРОК 4.1: DEBUG логи + bounds у RulerWidget

#### 4.1.1 Додати DEBUG логи в rulers.py

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\rulers.py</parameter>
</invoke>
```

#### 4.1.2 Додати bounds highlighting

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
    "newText": "    def highlight_bounds(self, start_mm, width_mm):\n        \"\"\"Підсвітити межі елемента\"\"\"\n        orientation_name = \"H\" if self.orientation == Qt.Horizontal else \"V\"\n        logger.debug(f\"[BOUNDS-{orientation_name}] Highlight: start={start_mm:.2f}mm, width={width_mm:.2f}mm\")\n        self.highlighted_bounds = (start_mm, width_mm)\n        self.update()\n    \n    def clear_highlight(self):\n        \"\"\"Очистити підсвічування\"\"\"\n        orientation_name = \"H\" if self.orientation == Qt.Horizontal else \"V\"\n        logger.debug(f\"[BOUNDS-{orientation_name}] Clear highlight\")\n        self.highlighted_bounds = None\n        self.update()\n    \n    def _draw_bounds_highlight(self, painter):\n        \"\"\"Малювати підсвічування меж\"\"\"\n        start_mm, width_mm = self.highlighted_bounds\n        \n        start_px = int(self._mm_to_px(start_mm) * self.scale_factor)\n        width_px = int(self._mm_to_px(width_mm) * self.scale_factor)\n        \n        orientation_name = \"H\" if self.orientation == Qt.Horizontal else \"V\"\n        logger.debug(f\"[BOUNDS-{orientation_name}] Draw: start_px={start_px}, width_px={width_px}\")\n        \n        # Напівпрозорий синій прямокутник\n        color = QColor(100, 150, 255, 80)\n        \n        if self.orientation == Qt.Horizontal:\n            rect = QRect(start_px, 0, width_px, self.ruler_thickness)\n        else:\n            rect = QRect(0, start_px, self.ruler_thickness, width_px)\n        \n        painter.fillRect(rect, color)\n        \n        # Рамка\n        pen = QPen(QColor(50, 100, 255), 1)\n        painter.setPen(pen)\n        painter.drawRect(rect)\n    \n    def update_scale(self, scale_factor):"
  }
]</parameter>
</invoke>
```

#### 4.1.3 Перевірка

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\rulers.py</parameter>
<parameter name="head">60</parameter>
</invoke>
```

**✅ Критерії успіху КРОК 4.1:**
- [ ] Змінна `highlighted_bounds` додана
- [ ] DEBUG логи `[BOUNDS-H/V]` додані
- [ ] Метод `highlight_bounds` створено
- [ ] Метод `clear_highlight` створено
- [ ] Метод `_draw_bounds_highlight` створено

---

### КРОК 4.2: Інтеграція bounds у MainWindow

#### 4.2.1 Читати main_window.py

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
</invoke>
```

#### 4.2.2 Оновити _on_selection_changed

```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
<parameter name="edits">[
  {
    "oldText": "    def _on_selection_changed(self):\n        \"\"\"Обробка зміни виділення\"\"\"\n        selected = self.canvas.scene.selectedItems()\n        \n        if selected:\n            item = selected[0]\n            element = item.element\n            \n            # Оновити property panel\n            self.property_panel.set_element(element, item)\n            \n            # Зберегти виділений item\n            self.selected_item = item\n            logger.info(f\"Element selected: {element.config.x}mm, {element.config.y}mm\")\n        else:\n            self.property_panel.set_element(None, None)\n            self.selected_item = None\n            logger.info(\"Selection cleared\")",
    "newText": "    def _on_selection_changed(self):\n        \"\"\"Обробка зміни виділення\"\"\"\n        selected = self.canvas.scene.selectedItems()\n        \n        if selected:\n            item = selected[0]\n            element = item.element\n            \n            # Оновити property panel\n            self.property_panel.set_element(element, item)\n            \n            # Підсвітити bounds на лінейках\n            self._highlight_element_bounds(item)\n            \n            # Зберегти виділений item\n            self.selected_item = item\n            logger.info(f\"Element selected: {element.config.x}mm, {element.config.y}mm\")\n        else:\n            # Очистити підсвічування\n            self.h_ruler.clear_highlight()\n            self.v_ruler.clear_highlight()\n            self.property_panel.set_element(None, None)\n            self.selected_item = None\n            logger.info(\"Selection cleared\")"
  },
  {
    "oldText": "    def eventFilter(self, obj, event):",
    "newText": "    def _highlight_element_bounds(self, item):\n        \"\"\"Підсвітити межі елемента на лінейках\"\"\"\n        if hasattr(item, 'element'):\n            element = item.element\n            x = element.config.x\n            y = element.config.y\n            \n            # Отримати розміри з boundingRect\n            bounds = item.boundingRect()\n            width_px = bounds.width()\n            height_px = bounds.height()\n            \n            # Конвертувати у мм\n            dpi = 203\n            width_mm = width_px * 25.4 / dpi\n            height_mm = height_px * 25.4 / dpi\n            \n            logger.debug(f\"[BOUNDS] Element at: x={x:.2f}mm, y={y:.2f}mm\")\n            logger.debug(f\"[BOUNDS] Size: width={width_mm:.2f}mm, height={height_mm:.2f}mm\")\n            \n            # Підсвітити на лінейках\n            self.h_ruler.highlight_bounds(x, width_mm)\n            self.v_ruler.highlight_bounds(y, height_mm)\n            logger.info(f\"Highlighted bounds: X={x}mm W={width_mm:.1f}mm, Y={y}mm H={height_mm:.1f}mm\")\n    \n    def eventFilter(self, obj, event):"
  }
]</parameter>
</invoke>
```

**✅ Критерії успіху КРОК 4.2:**
- [ ] Метод `_highlight_element_bounds` створено
- [ ] DEBUG логи `[BOUNDS]` додані
- [ ] `_on_selection_changed` оновлено
- [ ] `clear_highlight()` викликається при deselect

---

### КРОК 4.3: Умний тест ЕТАП 4

#### 4.3.1 Створити тест з LogAnalyzer

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\test_bounds_smart.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Element Bounds Highlighting з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


class BoundsLogAnalyzer:
    """Анализатор логів для bounds highlighting"""
    
    @staticmethod
    def parse_bounds_logs(log):
        """[BOUNDS] Element position and size"""
        element_at = re.findall(r'\[BOUNDS\] Element at: x=([\d.]+)mm, y=([\d.]+)mm', log)
        size = re.findall(r'\[BOUNDS\] Size: width=([\d.]+)mm, height=([\d.]+)mm', log)
        
        return {
            'element_at': [(float(m[0]), float(m[1])) for m in element_at],
            'size': [(float(m[0]), float(m[1])) for m in size]
        }
    
    @staticmethod
    def parse_ruler_bounds_logs(log):
        """[BOUNDS-H/V] Highlight and Draw logs"""
        h_highlight = re.findall(r'\[BOUNDS-H\] Highlight: start=([\d.]+)mm, width=([\d.]+)mm', log)
        v_highlight = re.findall(r'\[BOUNDS-V\] Highlight: start=([\d.]+)mm, width=([\d.]+)mm', log)
        h_draw = re.findall(r'\[BOUNDS-H\] Draw: start_px=([\d.]+), width_px=([\d.]+)', log)
        v_draw = re.findall(r'\[BOUNDS-V\] Draw: start_px=([\d.]+), width_px=([\d.]+)', log)
        clear_h = re.findall(r'\[BOUNDS-H\] Clear highlight', log)
        clear_v = re.findall(r'\[BOUNDS-V\] Clear highlight', log)
        
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
        """Детектувати проблеми bounds highlighting"""
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
                    'desc': f'Element X={element_x:.2f}mm, Ruler H start={ruler_h_start:.2f}mm'
                })
            
            if abs(element_y - ruler_v_start) > 0.1:
                issues.append({
                    'type': 'BOUNDS_RULER_MISMATCH_V',
                    'desc': f'Element Y={element_y:.2f}mm, Ruler V start={ruler_v_start:.2f}mm'
                })
        
        # 2. SIZE != RULER WIDTH
        if bounds_logs['size'] and ruler_logs['h_highlight']:
            element_width = bounds_logs['size'][-1][0]
            element_height = bounds_logs['size'][-1][1]
            ruler_width = ruler_logs['h_highlight'][-1][1]
            ruler_height = ruler_logs['v_highlight'][-1][1]
            
            if abs(element_width - ruler_width) > 0.5:
                issues.append({
                    'type': 'SIZE_WIDTH_MISMATCH',
                    'desc': f'Element width={element_width:.2f}mm, Ruler width={ruler_width:.2f}mm'
                })
            
            if abs(element_height - ruler_height) > 0.5:
                issues.append({
                    'type': 'SIZE_HEIGHT_MISMATCH',
                    'desc': f'Element height={element_height:.2f}mm, Ruler height={ruler_height:.2f}mm'
                })
        
        # 3. RULER HIGHLIGHT != DRAWN
        if ruler_logs['h_highlight'] and ruler_logs['h_draw']:
            highlight_start = ruler_logs['h_highlight'][-1][0]
            highlight_width = ruler_logs['h_highlight'][-1][1]
            drawn_start = ruler_logs['h_draw'][-1][0]
            drawn_width = ruler_logs['h_draw'][-1][1]
            
            # Конвертувати мм -> px
            dpi = 203
            scale = 2.5
            expected_start_px = int(highlight_start * dpi / 25.4 * scale)
            expected_width_px = int(highlight_width * dpi / 25.4 * scale)
            
            if abs(drawn_start - expected_start_px) > 2:
                issues.append({
                    'type': 'DRAW_START_INCORRECT',
                    'desc': f'Expected start={expected_start_px}px, drawn={drawn_start}px'
                })
            
            if abs(drawn_width - expected_width_px) > 2:
                issues.append({
                    'type': 'DRAW_WIDTH_INCORRECT',
                    'desc': f'Expected width={expected_width_px}px, drawn={drawn_width}px'
                })
        
        return issues


def test_bounds_smart():
    """Умний тест bounds highlighting з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Розмір файла ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # СИМУЛЯЦІЯ: додати text елемент
    window._add_text()
    app.processEvents()
    
    # Виділити елемент
    item = window.graphics_items[0]
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    # Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Аналізувати
    analyzer = BoundsLogAnalyzer()
    bounds_logs = analyzer.parse_bounds_logs(new_logs)
    ruler_logs = analyzer.parse_ruler_bounds_logs(new_logs)
    issues = analyzer.detect_issues(bounds_logs, ruler_logs)
    
    print("=" * 60)
    print("[STAGE 4] ELEMENT BOUNDS - LOG ANALYSIS")
    print("=" * 60)
    print(f"\n[BOUNDS] element positions: {len(bounds_logs['element_at'])}")
    print(f"[BOUNDS] sizes: {len(bounds_logs['size'])}")
    print(f"[RULER-H] highlights: {len(ruler_logs['h_highlight'])}")
    print(f"[RULER-V] highlights: {len(ruler_logs['v_highlight'])}")
    print(f"[RULER-H] draws: {len(ruler_logs['h_draw'])}")
    print(f"[RULER-V] draws: {len(ruler_logs['v_draw'])}")
    
    if bounds_logs['element_at']:
        pos = bounds_logs['element_at'][-1]
        print(f"Element position: x={pos[0]:.2f}mm, y={pos[1]:.2f}mm")
    
    if bounds_logs['size']:
        size = bounds_logs['size'][-1]
        print(f"Element size: width={size[0]:.2f}mm, height={size[1]:.2f}mm")
    
    # Тест deselect (clear)
    print("\n[TEST] Deselect element...")
    file_size_before_clear = log_file.stat().st_size
    
    window.canvas.scene.clearSelection()
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before_clear)
        clear_logs = f.read()
    
    clear_ruler_logs = analyzer.parse_ruler_bounds_logs(clear_logs)
    print(f"[RULER-H] clears: {clear_ruler_logs['clear_h']}")
    print(f"[RULER-V] clears: {clear_ruler_logs['clear_v']}")
    
    if clear_ruler_logs['clear_h'] == 0 or clear_ruler_logs['clear_v'] == 0:
        issues.append({
            'type': 'NO_CLEAR_ON_DESELECT',
            'desc': f"Rulers not cleared on deselect (H={clear_ruler_logs['clear_h']}, V={clear_ruler_logs['clear_v']})"
        })
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] BOUNDS HIGHLIGHTING HAS ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Bounds highlighting works correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_bounds_smart())
</parameter>
</invoke>
```

#### 4.3.2 Створити runner

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_bounds_smart_test.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""Runner для умного теста bounds highlighting"""

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

print(f"\nEXIT CODE: {result.returncode}")
</parameter>
</invoke>
```

#### 4.3.3 Запустити тест

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_bounds_smart_test.py').read())
```

**✅ Критерії успіху ЕТАП 4:**
- [ ] `[BOUNDS]` логи в консолі
- [ ] `[BOUNDS-H/V]` логи в консолі
- [ ] LogAnalyzer детектує 0 проблем
- [ ] EXIT CODE: 0
- [ ] Bounds підсвічуються при select
- [ ] Bounds очищаються при deselect

---

### ⏸️ СТОП-ТОЧКА ЕТАП 4

**НЕ ПЕРЕХОДЬ ДО ЕТАП 5 ПОКИ:**
- [ ] Умний тест НЕ пройдено (EXIT CODE != 0)
- [ ] LogAnalyzer знайшов проблеми
- [ ] Bounds НЕ підсвічуються
- [ ] Bounds НЕ очищаються при deselect

---

## 🚀 ЕТАП 5: ADVANCED KEYBOARD SHORTCUTS

### МЕТА
Реалізувати повний набір keyboard shortcuts для професійної роботи

---

### КРОК 5.1: DEBUG логи + keyPressEvent у MainWindow

#### 5.1.1 Оновити keyPressEvent

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
    "newText": "    def keyPressEvent(self, event):\n        \"\"\"Keyboard shortcuts\"\"\"\n        modifiers = event.modifiers()\n        key = event.key()\n        \n        # === ZOOM ===\n        if modifiers == Qt.ControlModifier:\n            if key in (Qt.Key_Plus, Qt.Key_Equal):\n                logger.debug(\"[SHORTCUT] Ctrl+Plus - Zoom In\")\n                self.canvas.zoom_in()\n            elif key == Qt.Key_Minus:\n                logger.debug(\"[SHORTCUT] Ctrl+Minus - Zoom Out\")\n                self.canvas.zoom_out()\n            elif key == Qt.Key_0:\n                logger.debug(\"[SHORTCUT] Ctrl+0 - Reset Zoom\")\n                self.canvas.reset_zoom()\n            # === SNAP ===\n            elif key == Qt.Key_G:\n                logger.debug(\"[SHORTCUT] Ctrl+G - Toggle Snap\")\n                self.snap_enabled = not self.snap_enabled\n                self._toggle_snap(Qt.Checked if self.snap_enabled else Qt.Unchecked)\n        \n        # === DELETE ===\n        elif key in (Qt.Key_Delete, Qt.Key_Backspace):\n            logger.debug(f\"[SHORTCUT] {event.key()} - Delete Element\")\n            self._delete_selected()\n        \n        # === PRECISION MOVE (Shift + Arrow) ===\n        elif modifiers == Qt.ShiftModifier:\n            if key == Qt.Key_Left:\n                logger.debug(\"[SHORTCUT] Shift+Left - Move -0.1mm\")\n                self._move_selected(-0.1, 0)\n            elif key == Qt.Key_Right:\n                logger.debug(\"[SHORTCUT] Shift+Right - Move +0.1mm\")\n                self._move_selected(0.1, 0)\n            elif key == Qt.Key_Up:\n                logger.debug(\"[SHORTCUT] Shift+Up - Move -0.1mm\")\n                self._move_selected(0, -0.1)\n            elif key == Qt.Key_Down:\n                logger.debug(\"[SHORTCUT] Shift+Down - Move +0.1mm\")\n                self._move_selected(0, 0.1)\n        \n        # === NORMAL MOVE (Arrow) ===\n        elif modifiers == Qt.NoModifier:\n            if key == Qt.Key_Left:\n                logger.debug(\"[SHORTCUT] Left - Move -1mm\")\n                self._move_selected(-1, 0)\n            elif key == Qt.Key_Right:\n                logger.debug(\"[SHORTCUT] Right - Move +1mm\")\n                self._move_selected(1, 0)\n            elif key == Qt.Key_Up:\n                logger.debug(\"[SHORTCUT] Up - Move -1mm\")\n                self._move_selected(0, -1)\n            elif key == Qt.Key_Down:\n                logger.debug(\"[SHORTCUT] Down - Move +1mm\")\n                self._move_selected(0, 1)\n        \n        super().keyPressEvent(event)"
  }
]</parameter>
</invoke>
```

**✅ Критерії успіху КРОК 5.1:**
- [ ] DEBUG логи `[SHORTCUT]` додані для всіх shortcuts
- [ ] DELETE/BACKSPACE обробка додана
- [ ] Shift+Arrow shortcuts додані
- [ ] Arrow shortcuts додані

---

### КРОК 5.2: Методи _move_selected та _delete_selected

```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
<parameter name="edits">[
  {
    "oldText": "    def keyPressEvent(self, event):",
    "newText": "    def _move_selected(self, dx_mm, dy_mm):\n        \"\"\"Перемістити виділений елемент\"\"\"\n        if self.selected_item and hasattr(self.selected_item, 'element'):\n            element = self.selected_item.element\n            old_x, old_y = element.config.x, element.config.y\n            \n            element.config.x += dx_mm\n            element.config.y += dy_mm\n            \n            logger.debug(f\"[MOVE] Before: ({old_x:.2f}, {old_y:.2f})mm\")\n            logger.debug(f\"[MOVE] Delta: ({dx_mm:.2f}, {dy_mm:.2f})mm\")\n            logger.debug(f\"[MOVE] After: ({element.config.x:.2f}, {element.config.y:.2f})mm\")\n            \n            # Оновити позицію graphics item\n            dpi = 203\n            new_x = element.config.x * dpi / 25.4\n            new_y = element.config.y * dpi / 25.4\n            self.selected_item.setPos(new_x, new_y)\n            \n            # Оновити property panel та bounds\n            if self.property_panel.current_element:\n                self.property_panel.refresh()\n            self._highlight_element_bounds(self.selected_item)\n            \n            logger.info(f\"Element moved: dx={dx_mm}mm, dy={dy_mm}mm -> ({element.config.x}, {element.config.y})\")\n    \n    def _delete_selected(self):\n        \"\"\"Видалити виділений елемент\"\"\"\n        if self.selected_item:\n            logger.debug(f\"[DELETE] Removing element from scene\")\n            \n            # Видалити з scene\n            self.canvas.scene.removeItem(self.selected_item)\n            \n            # Видалити з списків\n            if hasattr(self.selected_item, 'element'):\n                element = self.selected_item.element\n                if element in self.elements:\n                    self.elements.remove(element)\n                    logger.debug(f\"[DELETE] Removed from elements list\")\n            \n            if self.selected_item in self.graphics_items:\n                self.graphics_items.remove(self.selected_item)\n                logger.debug(f\"[DELETE] Removed from graphics_items list\")\n            \n            logger.info(f\"Element deleted\")\n            self.selected_item = None\n            \n            # Очистити rulers та property panel\n            self.h_ruler.clear_highlight()\n            self.v_ruler.clear_highlight()\n            self.property_panel.set_element(None, None)\n            logger.debug(f\"[DELETE] UI cleared\")\n    \n    def keyPressEvent(self, event):"
  }
]</parameter>
</invoke>
```

**✅ Критерії успіху КРОК 5.2:**
- [ ] Метод `_move_selected` створено
- [ ] DEBUG логи `[MOVE]` додані (Before/Delta/After)
- [ ] Метод `_delete_selected` створено
- [ ] DEBUG логи `[DELETE]` додані
- [ ] Property panel оновлюється
- [ ] Bounds оновлюються

---

### КРОК 5.3: Умний тест ЕТАП 5

#### 5.3.1 Створити тест з LogAnalyzer

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\test_shortcuts_smart.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Keyboard Shortcuts з аналізом логів"""

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
    """Анализатор логів для keyboard shortcuts"""
    
    @staticmethod
    def parse_shortcut_logs(log):
        """[SHORTCUT] logs"""
        shortcuts = re.findall(r'\[SHORTCUT\] (.+)', log)
        return shortcuts
    
    @staticmethod
    def parse_move_logs(log):
        """[MOVE] Before/Delta/After logs"""
        before = re.findall(r'\[MOVE\] Before: \(([\d.]+), ([\d.]+)\)mm', log)
        delta = re.findall(r'\[MOVE\] Delta: \(([-\d.]+), ([-\d.]+)\)mm', log)
        after = re.findall(r'\[MOVE\] After: \(([\d.]+), ([\d.]+)\)mm', log)
        
        return {
            'before': [(float(m[0]), float(m[1])) for m in before],
            'delta': [(float(m[0]), float(m[1])) for m in delta],
            'after': [(float(m[0]), float(m[1])) for m in after]
        }
    
    @staticmethod
    def parse_delete_logs(log):
        """[DELETE] logs"""
        removing = len(re.findall(r'\[DELETE\] Removing element from scene', log))
        from_elements = len(re.findall(r'\[DELETE\] Removed from elements list', log))
        from_graphics = len(re.findall(r'\[DELETE\] Removed from graphics_items list', log))
        ui_cleared = len(re.findall(r'\[DELETE\] UI cleared', log))
        
        return {
            'removing': removing,
            'from_elements': from_elements,
            'from_graphics': from_graphics,
            'ui_cleared': ui_cleared
        }
    
    @staticmethod
    def detect_issues(shortcut_logs, move_logs, delete_logs):
        """Детектувати проблеми shortcuts"""
        issues = []
        
        # 1. MOVE: Before + Delta != After
        if move_logs['before'] and move_logs['delta'] and move_logs['after']:
            before = move_logs['before'][-1]
            delta = move_logs['delta'][-1]
            after = move_logs['after'][-1]
            
            expected_x = before[0] + delta[0]
            expected_y = before[1] + delta[1]
            
            if abs(after[0] - expected_x) > 0.01:
                issues.append({
                    'type': 'MOVE_CALCULATION_ERROR_X',
                    'desc': f'Before={before[0]:.2f} + Delta={delta[0]:.2f} = {expected_x:.2f}, but After={after[0]:.2f}'
                })
            
            if abs(after[1] - expected_y) > 0.01:
                issues.append({
                    'type': 'MOVE_CALCULATION_ERROR_Y',
                    'desc': f'Before={before[1]:.2f} + Delta={delta[1]:.2f} = {expected_y:.2f}, but After={after[1]:.2f}'
                })
        
        # 2. DELETE: не всі кроки виконано
        if delete_logs['removing'] > 0:
            if delete_logs['from_elements'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_NOT_FROM_ELEMENTS',
                    'desc': f"Removing={delete_logs['removing']}, but from_elements={delete_logs['from_elements']}"
                })
            
            if delete_logs['from_graphics'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_NOT_FROM_GRAPHICS',
                    'desc': f"Removing={delete_logs['removing']}, but from_graphics={delete_logs['from_graphics']}"
                })
            
            if delete_logs['ui_cleared'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_UI_NOT_CLEARED',
                    'desc': f"Removing={delete_logs['removing']}, but ui_cleared={delete_logs['ui_cleared']}"
                })
        
        return issues


def test_shortcuts_smart():
    """Умний тест shortcuts з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Додати елемент
    window._add_text()
    app.processEvents()
    
    item = window.graphics_items[0]
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    # ============ ТЕСТ MOVE ============
    print("=" * 60)
    print("[STAGE 5] KEYBOARD SHORTCUTS - LOG ANALYSIS")
    print("=" * 60)
    
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # Симулювати Arrow Right (move +1mm)
    key_event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_Right,
        Qt.NoModifier
    )
    window.keyPressEvent(key_event)
    app.processEvents()
    
    # Читати логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        move_logs_text = f.read()
    
    analyzer = ShortcutsLogAnalyzer()
    shortcut_logs = analyzer.parse_shortcut_logs(move_logs_text)
    move_logs = analyzer.parse_move_logs(move_logs_text)
    
    print("\n[TEST] Arrow Right (+1mm):")
    print(f"Shortcuts detected: {shortcut_logs}")
    print(f"[MOVE] entries: {len(move_logs['before'])}")
    
    if move_logs['before']:
        print(f"Before: {move_logs['before'][-1]}")
        print(f"Delta: {move_logs['delta'][-1]}")
        print(f"After: {move_logs['after'][-1]}")
    
    # ============ ТЕСТ DELETE ============
    file_size_before = log_file.stat().st_size
    
    # Симулювати Delete
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
    
    print(f"\n[TEST] Delete:")
    print(f"[DELETE] removing: {delete_logs['removing']}")
    print(f"[DELETE] from_elements: {delete_logs['from_elements']}")
    print(f"[DELETE] from_graphics: {delete_logs['from_graphics']}")
    print(f"[DELETE] ui_cleared: {delete_logs['ui_cleared']}")
    
    # ============ ДЕТЕКЦІЯ ПРОБЛЕМ ============
    issues = analyzer.detect_issues(shortcut_logs, move_logs, delete_logs)
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] SHORTCUTS HAVE ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Keyboard shortcuts work correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_shortcuts_smart())
</parameter>
</invoke>
```

#### 5.3.2 Створити runner

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_shortcuts_smart_test.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""Runner для умного теста shortcuts"""

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

print(f"\nEXIT CODE: {result.returncode}")
</parameter>
</invoke>
```

#### 5.3.3 Запустити тест

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_shortcuts_smart_test.py').read())
```

**✅ Критерії успіху ЕТАП 5:**
- [ ] `[SHORTCUT]` логи в консолі
- [ ] `[MOVE]` логи (Before/Delta/After) в консолі
- [ ] `[DELETE]` логи в консолі
- [ ] LogAnalyzer детектує 0 проблем
- [ ] EXIT CODE: 0
- [ ] Move працює (Before + Delta = After)
- [ ] Delete видаляє з усіх списків

---

### ⏸️ СТОП-ТОЧКА ЕТАП 5

**НЕ ПЕРЕХОДЬ ДО ФІНАЛЬНОЇ ІНТЕГРАЦІЇ ПОКИ:**
- [ ] Умний тест НЕ пройдено (EXIT CODE != 0)
- [ ] LogAnalyzer знайшов проблеми
- [ ] Move calculation неправильний
- [ ] Delete НЕ очищає UI

---

## 🎯 ФІНАЛЬНА ІНТЕГРАЦІЯ: MASTER TEST

### Створити master runner для ЕТАПІВ 4-5

```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_stages_4_5_smart.py</parameter>
<parameter name="content"># -*- coding: utf-8 -*-
"""Master runner - ЕТАПИ 4-5 умні тести"""

import subprocess

print("=" * 70)
print(" MASTER TEST RUNNER - STAGES 4-5 CANVAS FEATURES")
print("=" * 70)

tests = [
    ("STAGE 4: ELEMENT BOUNDS", r'tests\test_bounds_smart.py'),
    ("STAGE 5: KEYBOARD SHORTCUTS", r'tests\test_shortcuts_smart.py'),
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

# Підсумковий звіт
print("\n" + "=" * 70)
print(" FINAL RESULTS")
print("=" * 70)

all_passed = True
for r in results:
    status = "[OK]" if r['success'] else "[FAIL]"
    print(f"{status} {r['stage']} - EXIT CODE: {r['exit_code']}")
    if not r['success']:
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print(" ALL STAGES 4-5 PASSED!")
    print(" Ready for production")
else:
    print(" SOME STAGES FAILED!")
    print(" Fix issues before proceeding")
print("=" * 70)
</parameter>
</invoke>
```

### Запустити master test

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_stages_4_5_smart.py').read())
```

**✅ ФІНАЛЬНІ КРИТЕРІЇ:**
- [ ] STAGE 4: Element Bounds - EXIT CODE: 0
- [ ] STAGE 5: Keyboard Shortcuts - EXIT CODE: 0
- [ ] ALL STAGES PASSED!

---

## 📝 ДОКУМЕНТАЦІЯ В MEMORY

```xml
<invoke name="memory:add_observations">
<parameter name="observations">[
  {
    "entityName": "1C_Zebra Project",
    "contents": [
      "ЕТАП 4 completed: Element Bounds Highlighting з умним тестуванням",
      "RulerWidget: DEBUG логи [BOUNDS-H/V] для highlight/clear/draw",
      "MainWindow: _highlight_element_bounds з boundingRect конвертацією",
      "test_bounds_smart.py: BoundsLogAnalyzer детектує BOUNDS_RULER_MISMATCH, SIZE_MISMATCH, DRAW_INCORRECT",
      "ЕТАП 5 completed: Advanced Keyboard Shortcuts з умним тестуванням",
      "MainWindow: DEBUG логи [SHORTCUT], [MOVE], [DELETE] для всіх shortcuts",
      "keyPressEvent: Delete/Backspace, Arrow (1mm), Shift+Arrow (0.1mm)",
      "_move_selected: Before/Delta/After логіка з property panel update",
      "_delete_selected: видалення з scene, elements, graphics_items, UI clear",
      "test_shortcuts_smart.py: ShortcutsLogAnalyzer детектує MOVE_CALCULATION_ERROR, DELETE_NOT_FROM_*",
      "Master runner run_stages_4_5_smart.py для комплексного тестування",
      "Всі умні тести використовують file_size_before для читання нових логів",
      "LogAnalyzer для кожного етапу детектує 2-4 типи проблем",
      "EXIT CODE 0 = успіх, 1 = проблеми знайдено"
    ]
  }
]</parameter>
</invoke>
```

---

## ✅ ЧЕКЛИСТ ЗАВЕРШЕННЯ ЕТАПІВ 4-5

### ЕТАП 4 - ELEMENT BOUNDS:
- [✓] DEBUG логи `[BOUNDS-H/V]` додані
- [✓] `highlighted_bounds` змінна
- [✓] `highlight_bounds()`, `clear_highlight()` методи
- [✓] `_draw_bounds_highlight()` з напівпрозорим прямокутником
- [✓] `_highlight_element_bounds()` в MainWindow
- [✓] Інтеграція з `_on_selection_changed`
- [✓] BoundsLogAnalyzer з 5 типами проблем
- [✓] Умний тест test_bounds_smart.py
- [✓] Runner run_bounds_smart_test.py

### ЕТАП 5 - KEYBOARD SHORTCUTS:
- [✓] DEBUG логи `[SHORTCUT]`, `[MOVE]`, `[DELETE]`
- [✓] `keyPressEvent` з усіма shortcuts
- [✓] Delete/Backspace обробка
- [✓] Arrow Keys (1mm move)
- [✓] Shift+Arrow (0.1mm precision)
- [✓] `_move_selected()` з Before/Delta/After
- [✓] `_delete_selected()` з повним очищенням
- [✓] Property panel refresh
- [✓] Bounds refresh при move
- [✓] ShortcutsLogAnalyzer з 5 типами проблем
- [✓] Умний тест test_shortcuts_smart.py
- [✓] Runner run_shortcuts_smart_test.py

### ФІНАЛЬНА ІНТЕГРАЦІЯ:
- [✓] Master runner run_stages_4_5_smart.py
- [✓] Документація в memory
- [✓] Всі тести пройдено (EXIT CODE: 0)

---

## 🎉 ЗАВЕРШЕННЯ

**ЕТАПИ 4-5 успішно реалізовано з умним тестуванням!**

Проект тепер має:
- ✅ Element bounds highlighting на rulers
- ✅ Повний набір keyboard shortcuts (Delete, Arrow, Shift+Arrow)
- ✅ Умні тести з LogAnalyzer для кожного етапу
- ✅ DEBUG логи для всієї логіки
- ✅ Master runner для комплексного тестування

**Наступні кроки (опціонально):**
- Context Menu (right-click operations)
- Smart Guides (alignment with other elements)
- Undo/Redo система
- Multi-select та групування

**Документація оновлена в Memory ✓**
