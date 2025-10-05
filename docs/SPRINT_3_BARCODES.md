### СПРИНТ 3: Штрихкоди (7 кроків)

---

## ШАГ 3.1: Базовий клас BarcodeElement

**СТВОРИТИ: core/elements/barcode_element.py**

```python
# -*- coding: utf-8 -*-
"""Базовий клас для штрихкодів"""

from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPen, QBrush, QColor
from .base import BaseElement, ElementConfig


class BarcodeElement(BaseElement):
    """Базовий клас для штрихкодів"""
    
    BARCODE_TYPES = {
        'EAN13': 'EAN-13',
        'CODE128': 'Code 128',
        'QRCODE': 'QR Code'
    }
    
    def __init__(self, config: ElementConfig, barcode_type: str, data: str, 
                 width: int = 50, height: int = 30):
        """
        Args:
            config: Конфігурація позиції
            barcode_type: Тип штрихкоду ('EAN13', 'CODE128', 'QRCODE')
            data: Дані для кодування
            width: Ширина у мм
            height: Висота у мм
        """
        super().__init__(config)
        self.barcode_type = barcode_type
        self.data = data
        self.width = width
        self.height = height
        self.data_field = None  # Placeholder {{FIELD}}
        self.show_text = True   # Показувати текст під штрихкодом
    
    def to_dict(self):
        return {
            'type': 'barcode',
            'barcode_type': self.barcode_type,
            'x': self.config.x,
            'y': self.config.y,
            'data': self.data,
            'width': self.width,
            'height': self.height,
            'data_field': self.data_field,
            'show_text': self.show_text
        }
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            barcode_type=data['barcode_type'],
            data=data['data'],
            width=data.get('width', 50),
            height=data.get('height', 30)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element
    
    def to_zpl(self, dpi):
        """Генерація ZPL коду - реалізується у підкласах"""
        raise NotImplementedError
    
    def _get_barcode_data(self):
        """Отримати дані для штрихкоду (placeholder або реальні)"""
        return self.data_field if self.data_field else self.data


class GraphicsBarcodeItem(QGraphicsRectItem):
    """Графічний елемент штрихкоду з drag-and-drop"""
    
    position_changed = Signal(float, float)  # x, y в мм
    
    def __init__(self, element: BarcodeElement, dpi=203):
        # Конвертація мм → пікселі
        width_px = int(element.width * dpi / 25.4)
        height_px = int(element.height * dpi / 25.4)
        
        super().__init__(0, 0, width_px, height_px)
        
        self.element = element
        self.dpi = dpi
        
        # Настройки
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        
        # Стиль прямокутника (placeholder для штрихкоду)
        pen = QPen(QColor(0, 0, 255), 2, Qt.DashLine)
        brush = QBrush(QColor(200, 220, 255, 100))
        self.setPen(pen)
        self.setBrush(brush)
        
        # Установити позицію
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)
    
    def _mm_to_px(self, mm):
        return int(mm * self.dpi / 25.4)
    
    def _px_to_mm(self, px):
        return px * 25.4 / self.dpi
    
    def itemChange(self, change, value):
        """Відслідковування зміни позиції"""
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            # Оновити елемент
            self.element.config.x = self._px_to_mm(self.pos().x())
            self.element.config.y = self._px_to_mm(self.pos().y())
            
            # Сигнал про зміну
            self.position_changed.emit(
                self.element.config.x, 
                self.element.config.y
            )
        
        return super().itemChange(change, value)
    
    def update_size(self, width, height):
        """Оновити розмір"""
        self.element.width = width
        self.element.height = height
        
        width_px = self._mm_to_px(width)
        height_px = self._mm_to_px(height)
        self.setRect(0, 0, width_px, height_px)
```

**ТЕСТ:**
```python
# Створити test у tests/test_barcode_base.py
from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
from core.elements.base import ElementConfig

config = ElementConfig(x=10, y=10)
barcode = BarcodeElement(config, 'EAN13', '1234567890123', width=50, height=30)

print(f"[OK] BarcodeElement created: {barcode.barcode_type}")
print(f"[OK] Data: {barcode.data}")
print(f"[OK] Size: {barcode.width}x{barcode.height}mm")
```

---

## ШАГ 3.2: EAN-13 Штрихкод

**ОНОВИТИ: core/elements/barcode_element.py** (додати клас)

```python
class EAN13BarcodeElement(BarcodeElement):
    """EAN-13 штрихкод"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 width: int = 50, height: int = 30):
        super().__init__(config, 'EAN13', data, width, height)
    
    def to_zpl(self, dpi):
        """Генерація ZPL для EAN-13"""
        # Конвертація мм → dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)
        
        # Використати placeholder або дані
        barcode_data = self._get_barcode_data()
        
        # ZPL команда для EAN-13
        # ^BY - ширина бару
        # ^BC - тип Barcode (Code 128 за замовчуванням, але використаємо ^B3 для Code 39/128)
        # Для EAN використовуємо ^BE
        
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY2")  # Ширина бару
        zpl_lines.append(f"^BEN,{height_dots},Y,N")  # EAN-13, висота, показ тексту
        zpl_lines.append(f"^FD{barcode_data}^FS")
        
        return "\n".join(zpl_lines)
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            width=data.get('width', 50),
            height=data.get('height', 30)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element
```

**ТЕСТ:**
```python
ean13 = EAN13BarcodeElement(
    ElementConfig(x=10, y=10),
    data='1234567890123',
    width=50,
    height=30
)

zpl = ean13.to_zpl(dpi=203)
print("[INFO] EAN-13 ZPL:")
print(zpl)

# Очікуваний вивід:
# ^FO80,80
# ^BY2
# ^BEN,236,Y,N
# ^FD1234567890123^FS
```

---

## ШАГ 3.3: Code128 Штрихкод

**ОНОВИТИ: core/elements/barcode_element.py** (додати клас)

```python
class Code128BarcodeElement(BarcodeElement):
    """Code 128 штрихкод"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 width: int = 60, height: int = 30):
        super().__init__(config, 'CODE128', data, width, height)
    
    def to_zpl(self, dpi):
        """Генерація ZPL для Code 128"""
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)
        
        barcode_data = self._get_barcode_data()
        
        # ZPL для Code 128
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY2")
        zpl_lines.append(f"^BCN,{height_dots},Y,N,N")  # Code 128, висота, текст
        zpl_lines.append(f"^FD{barcode_data}^FS")
        
        return "\n".join(zpl_lines)
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            width=data.get('width', 60),
            height=data.get('height', 30)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element
```

---

## ШАГ 3.4: QR Code

**ОНОВИТИ: core/elements/barcode_element.py** (додати клас)

```python
class QRCodeElement(BarcodeElement):
    """QR Code"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 size: int = 25):
        # QR код квадратний, тому width = height = size
        super().__init__(config, 'QRCODE', data, width=size, height=size)
        self.size = size
        self.magnification = 3  # Збільшення (1-10)
    
    def to_zpl(self, dpi):
        """Генерація ZPL для QR Code"""
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        
        barcode_data = self._get_barcode_data()
        
        # ZPL для QR Code
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BQN,2,{self.magnification}")  # QR, модель 2, magnification
        zpl_lines.append(f"^FD{barcode_data}^FS")
        
        return "\n".join(zpl_lines)
    
    def to_dict(self):
        data = super().to_dict()
        data['size'] = self.size
        data['magnification'] = self.magnification
        return data
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            size=data.get('size', 25)
        )
        element.data_field = data.get('data_field')
        element.magnification = data.get('magnification', 3)
        return element
```

---

## ШАГ 3.5: Інтеграція у GUI - Toolbar

**ОНОВИТИ: gui/toolbar.py**

```python
# Додати після Add Text:

self.addSeparator()

# Add Barcode menu
self.barcode_menu_action = QAction("Add Barcode", self)
self.barcode_menu_action.setToolTip("Додати штрихкод")

# Створити підменю
from PySide6.QtWidgets import QMenu
self.barcode_menu = QMenu(self)

self.add_ean13_action = QAction("EAN-13", self)
self.add_ean13_action.setToolTip("Додати EAN-13 штрихкод")
self.barcode_menu.addAction(self.add_ean13_action)

self.add_code128_action = QAction("Code 128", self)
self.add_code128_action.setToolTip("Додати Code 128 штрихкод")
self.barcode_menu.addAction(self.add_code128_action)

self.add_qrcode_action = QAction("QR Code", self)
self.add_qrcode_action.setToolTip("Додати QR код")
self.barcode_menu.addAction(self.add_qrcode_action)

self.barcode_menu_action.setMenu(self.barcode_menu)

# Додати до toolbar
self.addAction(self.barcode_menu_action)
```

**ОНОВИТИ: gui/main_window.py** (підключити сигнали)

```python
# У __init__ після підключення add_text_action:

self.toolbar.add_ean13_action.triggered.connect(self._add_ean13)
self.toolbar.add_code128_action.triggered.connect(self._add_code128)
self.toolbar.add_qrcode_action.triggered.connect(self._add_qrcode)
```

**ДОДАТИ методи у MainWindow:**

```python
def _add_ean13(self):
    """Додати EAN-13 штрихкод"""
    from core.elements.barcode_element import EAN13BarcodeElement, GraphicsBarcodeItem
    
    # Створити елемент
    config = ElementConfig(x=10, y=10)
    element = EAN13BarcodeElement(config, data='1234567890123', width=50, height=30)
    
    # Створити графічний елемент
    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    self.canvas.scene.addItem(graphics_item)
    
    # Зберегти
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
    
    logger.info(f"EAN-13 barcode added at ({element.config.x}, {element.config.y})")

def _add_code128(self):
    """Додати Code 128 штрихкод"""
    from core.elements.barcode_element import Code128BarcodeElement, GraphicsBarcodeItem
    
    config = ElementConfig(x=10, y=10)
    element = Code128BarcodeElement(config, data='SAMPLE128', width=60, height=30)
    
    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    self.canvas.scene.addItem(graphics_item)
    
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
    
    logger.info(f"Code 128 barcode added at ({element.config.x}, {element.config.y})")

def _add_qrcode(self):
    """Додати QR Code"""
    from core.elements.barcode_element import QRCodeElement, GraphicsBarcodeItem
    
    config = ElementConfig(x=10, y=10)
    element = QRCodeElement(config, data='https://example.com', size=25)
    
    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    self.canvas.scene.addItem(graphics_item)
    
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
    
    logger.info(f"QR Code added at ({element.config.x}, {element.config.y})")
```

---

## ШАГ 3.6: Property Panel для штрихкодів

**ОНОВИТИ: gui/property_panel.py**

Додати після Text Properties Group:

```python
# === Barcode Properties Group ===
self.barcode_group = QGroupBox("Barcode Properties")
barcode_form = QFormLayout()

self.barcode_type_label = QLabel()
barcode_form.addRow("Type:", self.barcode_type_label)

self.barcode_data_input = QLineEdit()
self.barcode_data_input.textChanged.connect(
    lambda v: self._on_property_change('barcode_data', v)
)
barcode_form.addRow("Data:", self.barcode_data_input)

self.barcode_width_input = QSpinBox()
self.barcode_width_input.setRange(20, 100)
self.barcode_width_input.setSuffix(" mm")
self.barcode_width_input.valueChanged.connect(
    lambda v: self._on_property_change('barcode_width', v)
)
barcode_form.addRow("Width:", self.barcode_width_input)

self.barcode_height_input = QSpinBox()
self.barcode_height_input.setRange(10, 100)
self.barcode_height_input.setSuffix(" mm")
self.barcode_height_input.valueChanged.connect(
    lambda v: self._on_property_change('barcode_height', v)
)
barcode_form.addRow("Height:", self.barcode_height_input)

self.barcode_placeholder_input = QLineEdit()
self.barcode_placeholder_input.setPlaceholderText("{{FIELD_NAME}}")
self.barcode_placeholder_input.textChanged.connect(
    lambda v: self._on_property_change('barcode_data_field', v if v else None)
)
barcode_form.addRow("Placeholder:", self.barcode_placeholder_input)

self.barcode_group.setLayout(barcode_form)
self.barcode_group.setVisible(False)  # Приховати за замовчуванням

# Додати до layout
layout.addWidget(text_group)
layout.addWidget(self.barcode_group)  # <-- Додати ТУТ
layout.addStretch()
```

**ОНОВИТИ метод set_element:**

```python
def set_element(self, element, graphics_item):
    """Відобразити властивості елемента"""
    self.current_element = element
    self.current_graphics_item = graphics_item
    
    if element:
        self.setEnabled(True)
        self.blockSignals(True)
        
        # Загальні властивості
        self.x_input.setValue(int(element.config.x))
        self.y_input.setValue(int(element.config.y))
        
        # Визначити тип елемента
        from core.elements.text_element import TextElement
        from core.elements.barcode_element import BarcodeElement
        
        if isinstance(element, TextElement):
            # Показати тільки Text Properties
            self.text_group.setVisible(True)
            self.barcode_group.setVisible(False)
            
            self.text_input.setText(element.text)
            self.font_size_input.setValue(element.font_size)
            self.placeholder_input.setText(
                element.data_field if element.data_field else ""
            )
        
        elif isinstance(element, BarcodeElement):
            # Показати тільки Barcode Properties
            self.text_group.setVisible(False)
            self.barcode_group.setVisible(True)
            
            self.barcode_type_label.setText(element.barcode_type)
            self.barcode_data_input.setText(element.data)
            self.barcode_width_input.setValue(int(element.width))
            self.barcode_height_input.setValue(int(element.height))
            self.barcode_placeholder_input.setText(
                element.data_field if element.data_field else ""
            )
        
        self.blockSignals(False)
    else:
        self.setEnabled(False)
```

**ОНОВИТИ метод _on_property_change:**

```python
# Додати обробку barcode properties:

elif prop_name == 'barcode_data':
    self.current_element.data = value

elif prop_name == 'barcode_width':
    self.current_element.width = value
    if self.current_graphics_item:
        self.current_graphics_item.update_size(value, self.current_element.height)

elif prop_name == 'barcode_height':
    self.current_element.height = value
    if self.current_graphics_item:
        self.current_graphics_item.update_size(self.current_element.width, value)

elif prop_name == 'barcode_data_field':
    self.current_element.data_field = value
```

---

## ШАГ 3.7: Оновити Template Manager

**ОНОВИТИ: core/template_manager.py**

У методі `_element_from_dict`:

```python
def _element_from_dict(self, data: Dict[str, Any]) -> Optional[BaseElement]:
    """Конвертувати dict → BaseElement"""
    elem_type = data.get('type')
    
    if elem_type == 'text':
        from .elements.text_element import TextElement
        return TextElement.from_dict(data)
    
    elif elem_type == 'barcode':
        from .elements.barcode_element import (
            EAN13BarcodeElement, 
            Code128BarcodeElement, 
            QRCodeElement
        )
        
        barcode_type = data.get('barcode_type')
        
        if barcode_type == 'EAN13':
            return EAN13BarcodeElement.from_dict(data)
        elif barcode_type == 'CODE128':
            return Code128BarcodeElement.from_dict(data)
        elif barcode_type == 'QRCODE':
            return QRCodeElement.from_dict(data)
    
    print(f"[WARNING] Unknown element type: {elem_type}")
    return None
```

**ОНОВИТИ: gui/main_window.py** у `_load_template`:

```python
# Додати елементи на canvas
for element in template_data['elements']:
    from core.elements.text_element import TextElement
    from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
    
    # Створити графічний елемент
    if isinstance(element, TextElement):
        graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi)
    elif isinstance(element, BarcodeElement):
        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    else:
        continue
    
    self.canvas.scene.addItem(graphics_item)
    
    # Зберегти
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
```

---

## ШАГ 3.8: Тести

**СТВОРИТИ: tests/test_barcodes.py**

```python
# -*- coding: utf-8 -*-
"""Тест штрихкодів"""

import sys
sys.path.insert(0, r'D:\AiKlientBank\1C_Zebra')

from core.elements.barcode_element import (
    EAN13BarcodeElement,
    Code128BarcodeElement,
    QRCodeElement
)
from core.elements.base import ElementConfig
from zpl.generator import ZPLGenerator


def test_barcodes():
    """Тест створення та генерації ZPL для штрихкодів"""
    
    results = []
    
    # EAN-13
    results.append("\n[TEST 1] EAN-13 Barcode")
    config1 = ElementConfig(x=10, y=10)
    ean13 = EAN13BarcodeElement(config1, data='1234567890123', width=50, height=30)
    
    results.append(f"[+] Created EAN-13: {ean13.data}")
    results.append(f"[+] Size: {ean13.width}x{ean13.height}mm")
    
    zpl1 = ean13.to_zpl(dpi=203)
    results.append("[INFO] EAN-13 ZPL:")
    results.append(zpl1)
    
    # Code 128
    results.append("\n[TEST 2] Code 128 Barcode")
    config2 = ElementConfig(x=10, y=50)
    code128 = Code128BarcodeElement(config2, data='SAMPLE128', width=60, height=30)
    
    results.append(f"[+] Created Code 128: {code128.data}")
    
    zpl2 = code128.to_zpl(dpi=203)
    results.append("[INFO] Code 128 ZPL:")
    results.append(zpl2)
    
    # QR Code
    results.append("\n[TEST 3] QR Code")
    config3 = ElementConfig(x=70, y=10)
    qr = QRCodeElement(config3, data='https://example.com', size=25)
    
    results.append(f"[+] Created QR Code: {qr.data}")
    results.append(f"[+] Size: {qr.size}x{qr.size}mm")
    
    zpl3 = qr.to_zpl(dpi=203)
    results.append("[INFO] QR Code ZPL:")
    results.append(zpl3)
    
    # Повний ZPL з усіма штрихкодами
    results.append("\n[TEST 4] Complete ZPL with all barcodes")
    
    label_config = {
        'width': 100,
        'height': 100,
        'dpi': 203
    }
    
    generator = ZPLGenerator(dpi=203)
    elements = [ean13, code128, qr]
    
    full_zpl = generator.generate(elements, label_config)
    results.append("[INFO] Complete ZPL:")
    results.append(full_zpl)
    
    results.append("\n[SUCCESS] All barcode tests passed!")
    
    # Зберегти результат
    output = '\n'.join(results)
    with open('tests/test_barcodes_result.txt', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(output)
    return True


if __name__ == '__main__':
    try:
        success = test_barcodes()
        sys.exit(0 if success else 1)
    except Exception as e:
        with open('tests/test_barcodes_result.txt', 'w', encoding='utf-8') as f:
            f.write(f"EXCEPTION: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

---

## КОНТРОЛЬНА ТОЧКА СПРИНТ 3

**ПЕРЕВІРИТИ ВСІ ФУНКЦІЇ:**

1. ✅ BarcodeElement базовий клас створено
2. ✅ EAN13BarcodeElement працює
3. ✅ Code128BarcodeElement працює
4. ✅ QRCodeElement працює
5. ✅ Toolbar має кнопку "Add Barcode" з підменю
6. ✅ Можна додати EAN-13 на canvas
7. ✅ Можна додати Code 128 на canvas
8. ✅ Можна додати QR Code на canvas
9. ✅ Property Panel показує barcode properties
10. ✅ Можна редагувати Data, Width, Height
11. ✅ Штрихкоди drag-and-drop працює
12. ✅ ZPL генерація для штрихкодів
13. ✅ Save/Load працює зі штрихкодами
14. ✅ Preview показує штрихкоди

**РУЧНИЙ ТЕСТ GUI:**

```bash
cd D:\AiKlientBank\1C_Zebra
.venv\Scripts\activate
python main.py
```

**Тести:**
1. Клік на "Add Barcode" → побачиш підменю
2. Вибери "EAN-13" → з'явиться синій прямокутник
3. Перемісти його drag-and-drop
4. Клік на штрихкод → Property Panel показує Barcode Properties
5. Зміни Data на інше значення
6. Додай Code 128 та QR Code
7. Save → збережи як "test_barcodes.json"
8. Load → завантаж назад
9. Export ZPL → побачиш ZPL з ^BE, ^BC, ^BQ командами
10. Preview → побачиш штрихкоди на етикетці

**Якщо ВСІ тести прошли - Спринт 3 завершено.**

**Якщо щось не працює - ОСТАНОВ, виправ, повтори тест.**

---

## ФОРМАТ КОММУНИКАЦІЇ

**При виконанні кожного кроку пиши:**

```
=== ШАГ X.Y ВИКОНУЄТЬСЯ ===

[Команди або дії]

=== ТЕСТ ===

[Результати тестування]

=== СТАТУС ===
[OK] Все працює
або
[FAILED] Опис проблеми
```

**Після успішного тесту чекай команду:**
- "Продолжай" - перейди до наступного кроку
- "Исправь X" - виправ проблему
- "Покажи код X" - покажи конкретний файл

---

## ПОЧАТОК РОБОТИ

**Виконай ШАГ 3.1**

Створи базовий клас BarcodeElement та GraphicsBarcodeItem згідно інструкції вище.

Після завершення напиши статус і чекай команду.
