### 冲刺 3: 条形码 (7个步骤)

---

## 步骤 3.1: 基础 BarcodeElement 类

**创建: core/elements/barcode_element.py**

```python
# -*- coding: utf-8 -*-
"""条形码基础类"""

from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPen, QBrush, QColor
from .base import BaseElement, ElementConfig


class BarcodeElement(BaseElement):
    """条形码基础类"""
    
    BARCODE_TYPES = {
        'EAN13': 'EAN-13',
        'CODE128': 'Code 128',
        'QRCODE': 'QR Code'
    }
    
    def __init__(self, config: ElementConfig, barcode_type: str, data: str, 
                 width: int = 50, height: int = 30):
        """
        Args:
            config: 位置配置
            barcode_type: 条形码类型 ('EAN13', 'CODE128', 'QRCODE')
            data: 编码数据
            width: 宽度（毫米）
            height: 高度（毫米）
        """
        super().__init__(config)
        self.barcode_type = barcode_type
        self.data = data
        self.width = width
        self.height = height
        self.data_field = None  # 占位符 {{FIELD}}
        self.show_text = True   # 在条形码下方显示文本
    
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
        """生成 ZPL 代码 - 在子类中实现"""
        raise NotImplementedError
    
    def _get_barcode_data(self):
        """获取条形码数据（占位符或实际数据）"""
        return self.data_field if self.data_field else self.data


class GraphicsBarcodeItem(QGraphicsRectItem):
    """带有拖放功能的条形码图形元素"""
    
    position_changed = Signal(float, float)  # x, y 以毫米为单位
    
    def __init__(self, element: BarcodeElement, dpi=203):
        # 毫米 → 像素转换
        width_px = int(element.width * dpi / 25.4)
        height_px = int(element.height * dpi / 25.4)
        
        super().__init__(0, 0, width_px, height_px)
        
        self.element = element
        self.dpi = dpi
        
        # 设置
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        
        # 矩形样式（条形码占位符）
        pen = QPen(QColor(0, 0, 255), 2, Qt.DashLine)
        brush = QBrush(QColor(200, 220, 255, 100))
        self.setPen(pen)
        self.setBrush(brush)
        
        # 设置位置
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)
    
    def _mm_to_px(self, mm):
        return int(mm * self.dpi / 25.4)
    
    def _px_to_mm(self, px):
        return px * 25.4 / self.dpi
    
    def itemChange(self, change, value):
        """跟踪位置变化"""
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            # 更新元素
            self.element.config.x = self._px_to_mm(self.pos().x())
            self.element.config.y = self._px_to_mm(self.pos().y())
            
            # 发送变化信号
            self.position_changed.emit(
                self.element.config.x, 
                self.element.config.y
            )
        
        return super().itemChange(change, value)
    
    def update_size(self, width, height):
        """更新尺寸"""
        self.element.width = width
        self.element.height = height
        
        width_px = self._mm_to_px(width)
        height_px = self._mm_to_px(height)
        self.setRect(0, 0, width_px, height_px)
```

**测试:**
```python
# 在 tests/test_barcode_base.py 中创建测试
from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
from core.elements.base import ElementConfig

config = ElementConfig(x=10, y=10)
barcode = BarcodeElement(config, 'EAN13', '1234567890123', width=50, height=30)

print(f"[OK] BarcodeElement 已创建: {barcode.barcode_type}")
print(f"[OK] 数据: {barcode.data}")
print(f"[OK] 尺寸: {barcode.width}x{barcode.height}mm")
```

---

## 步骤 3.2: EAN-13 条形码

**更新: core/elements/barcode_element.py** (添加类)

```python
class EAN13BarcodeElement(BarcodeElement):
    """EAN-13 条形码"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 width: int = 50, height: int = 30):
        super().__init__(config, 'EAN13', data, width, height)
    
    def to_zpl(self, dpi):
        """生成 EAN-13 的 ZPL"""
        # 毫米 → dots 转换
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)
        
        # 使用占位符或数据
        barcode_data = self._get_barcode_data()
        
        # EAN-13 的 ZPL 命令
        # ^BY - 条宽度
        # ^BC - 条形码类型（默认为 Code 128，但我们使用 ^B3 用于 Code 39/128）
        # 对于 EAN 我们使用 ^BE
        
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY2")  # 条宽度
        zpl_lines.append(f"^BEN,{height_dots},Y,N")  # EAN-13, 高度, 显示文本
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

**测试:**
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

# 预期输出:
# ^FO80,80
# ^BY2
# ^BEN,236,Y,N
# ^FD1234567890123^FS
```

---

## 步骤 3.3: Code128 条形码

**更新: core/elements/barcode_element.py** (添加类)

```python
class Code128BarcodeElement(BarcodeElement):
    """Code 128 条形码"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 width: int = 60, height: int = 30):
        super().__init__(config, 'CODE128', data, width, height)
    
    def to_zpl(self, dpi):
        """生成 Code 128 的 ZPL"""
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)
        
        barcode_data = self._get_barcode_data()
        
        # Code 128 的 ZPL
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY2")
        zpl_lines.append(f"^BCN,{height_dots},Y,N,N")  # Code 128, 高度, 文本
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

## 步骤 3.4: QR 码

**更新: core/elements/barcode_element.py** (添加类)

```python
class QRCodeElement(BarcodeElement):
    """QR 码"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 size: int = 25):
        # QR 码是正方形的，所以 width = height = size
        super().__init__(config, 'QRCODE', data, width=size, height=size)
        self.size = size
        self.magnification = 3  # 放大倍数 (1-10)
    
    def to_zpl(self, dpi):
        """生成 QR 码的 ZPL"""
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        
        barcode_data = self._get_barcode_data()
        
        # QR 码的 ZPL
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BQN,2,{self.magnification}")  # QR, 模型 2, 放大倍数
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

## 步骤 3.5: GUI 集成 - 工具栏

**更新: gui/toolbar.py**

```python
# 在 Add Text 后添加:

self.addSeparator()

# 添加条形码菜单
self.barcode_menu_action = QAction("添加条形码", self)
self.barcode_menu_action.setToolTip("添加条形码")

# 创建子菜单
from PySide6.QtWidgets import QMenu
self.barcode_menu = QMenu(self)

self.add_ean13_action = QAction("EAN-13", self)
self.add_ean13_action.setToolTip("添加 EAN-13 条形码")
self.barcode_menu.addAction(self.add_ean13_action)

self.add_code128_action = QAction("Code 128", self)
self.add_code128_action.setToolTip("添加 Code 128 条形码")
self.barcode_menu.addAction(self.add_code128_action)

self.add_qrcode_action = QAction("QR 码", self)
self.add_qrcode_action.setToolTip("添加 QR 码")
self.barcode_menu.addAction(self.add_qrcode_action)

self.barcode_menu_action.setMenu(self.barcode_menu)

# 添加到工具栏
self.addAction(self.barcode_menu_action)
```

**更新: gui/main_window.py** (连接信号)

```python
# 在连接 add_text_action 后:

self.toolbar.add_ean13_action.triggered.connect(self._add_ean13)
self.toolbar.add_code128_action.triggered.connect(self._add_code128)
self.toolbar.add_qrcode_action.triggered.connect(self._add_qrcode)
```

**在 MainWindow 中添加方法:**

```python
def _add_ean13(self):
    """添加 EAN-13 条形码"""
    from core.elements.barcode_element import EAN13BarcodeElement, GraphicsBarcodeItem
    
    # 创建元素
    config = ElementConfig(x=10, y=10)
    element = EAN13BarcodeElement(config, data='1234567890123', width=50, height=30)
    
    # 创建图形元素
    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    self.canvas.scene.addItem(graphics_item)
    
    # 保存
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
    
    logger.info(f"EAN-13 条形码已添加在 ({element.config.x}, {element.config.y})")

def _add_code128(self):
    """添加 Code 128 条形码"""
    from core.elements.barcode_element import Code128BarcodeElement, GraphicsBarcodeItem
    
    config = ElementConfig(x=10, y=10)
    element = Code128BarcodeElement(config, data='SAMPLE128', width=60, height=30)
    
    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    self.canvas.scene.addItem(graphics_item)
    
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
    
    logger.info(f"Code 128 条形码已添加在 ({element.config.x}, {element.config.y})")

def _add_qrcode(self):
    """添加 QR 码"""
    from core.elements.barcode_element import QRCodeElement, GraphicsBarcodeItem
    
    config = ElementConfig(x=10, y=10)
    element = QRCodeElement(config, data='https://example.com', size=25)
    
    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    self.canvas.scene.addItem(graphics_item)
    
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
    
    logger.info(f"QR 码已添加在 ({element.config.x}, {element.config.y})")
```

---

## 步骤 3.6: 条形码属性面板

**更新: gui/property_panel.py**

在 Text Properties Group 后添加:

```python
# === 条形码属性组 ===
self.barcode_group = QGroupBox("条形码属性")
barcode_form = QFormLayout()

self.barcode_type_label = QLabel()
barcode_form.addRow("类型:", self.barcode_type_label)

self.barcode_data_input = QLineEdit()
self.barcode_data_input.textChanged.connect(
    lambda v: self._on_property_change('barcode_data', v)
)
barcode_form.addRow("数据:", self.barcode_data_input)

self.barcode_width_input = QSpinBox()
self.barcode_width_input.setRange(20, 100)
self.barcode_width_input.setSuffix(" mm")
self.barcode_width_input.valueChanged.connect(
    lambda v: self._on_property_change('barcode_width', v)
)
barcode_form.addRow("宽度:", self.barcode_width_input)

self.barcode_height_input = QSpinBox()
self.barcode_height_input.setRange(10, 100)
self.barcode_height_input.setSuffix(" mm")
self.barcode_height_input.valueChanged.connect(
    lambda v: self._on_property_change('barcode_height', v)
)
barcode_form.addRow("高度:", self.barcode_height_input)

self.barcode_placeholder_input = QLineEdit()
self.barcode_placeholder_input.setPlaceholderText("{{FIELD_NAME}}")
self.barcode_placeholder_input.textChanged.connect(
    lambda v: self._on_property_change('barcode_data_field', v if v else None)
)
barcode_form.addRow("占位符:", self.barcode_placeholder_input)

self.barcode_group.setLayout(barcode_form)
self.barcode_group.setVisible(False)  # 默认隐藏

# 添加到布局
layout.addWidget(text_group)
layout.addWidget(self.barcode_group)  # <-- 在此添加
layout.addStretch()
```

**更新 set_element 方法:**

```python
def set_element(self, element, graphics_item):
    """显示元素属性"""
    self.current_element = element
    self.current_graphics_item = graphics_item
    
    if element:
        self.setEnabled(True)
        self.blockSignals(True)
        
        # 通用属性
        self.x_input.setValue(int(element.config.x))
        self.y_input.setValue(int(element.config.y))
        
        # 确定元素类型
        from core.elements.text_element import TextElement
        from core.elements.barcode_element import BarcodeElement
        
        if isinstance(element, TextElement):
            # 只显示文本属性
            self.text_group.setVisible(True)
            self.barcode_group.setVisible(False)
            
            self.text_input.setText(element.text)
            self.font_size_input.setValue(element.font_size)
            self.placeholder_input.setText(
                element.data_field if element.data_field else ""
            )
        
        elif isinstance(element, BarcodeElement):
            # 只显示条形码属性
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

**更新 _on_property_change 方法:**

```python
# 添加条形码属性处理:

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

## 步骤 3.7: 更新模板管理器

**更新: core/template_manager.py**

在 `_element_from_dict` 方法中:

```python
def _element_from_dict(self, data: Dict[str, Any]) -> Optional[BaseElement]:
    """转换 dict → BaseElement"""
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
    
    print(f"[警告] 未知元素类型: {elem_type}")
    return None
```

**更新: gui/main_window.py** 中的 `_load_template`:

```python
# 添加元素到画布
for element in template_data['elements']:
    from core.elements.text_element import TextElement
    from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
    
    # 创建图形元素
    if isinstance(element, TextElement):
        graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi)
    elif isinstance(element, BarcodeElement):
        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
    else:
        continue
    
    self.canvas.scene.addItem(graphics_item)
    
    # 保存
    self.elements.append(element)
    self.graphics_items.append(graphics_item)
```

---

## 步骤 3.8: 测试

**创建: tests/test_barcodes.py**

```python
# -*- coding: utf-8 -*-
"""条形码测试"""

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
    """测试条形码创建和 ZPL 生成"""
    
    results = []
    
    # EAN-13
    results.append("\n[测试 1] EAN-13 条形码")
    config1 = ElementConfig(x=10, y=10)
    ean13 = EAN13BarcodeElement(config1, data='1234567890123', width=50, height=30)
    
    results.append(f"[+] 已创建 EAN-13: {ean13.data}")
    results.append(f"[+] 尺寸: {ean13.width}x{ean13.height}mm")
    
    zpl1 = ean13.to_zpl(dpi=203)
    results.append("[INFO] EAN-13 ZPL:")
    results.append(zpl1)
    
    # Code 128
    results.append("\n[测试 2] Code 128 条形码")
    config2 = ElementConfig(x=10, y=50)
    code128 = Code128BarcodeElement(config2, data='SAMPLE128', width=60, height=30)
    
    results.append(f"[+] 已创建 Code 128: {code128.data}")
    
    zpl2 = code128.to_zpl(dpi=203)
    results.append("[INFO] Code 128 ZPL:")
    results.append(zpl2)
    
    # QR 码
    results.append("\n[测试 3] QR 码")
    config3 = ElementConfig(x=70, y=10)
    qr = QRCodeElement(config3, data='https://example.com', size=25)
    
    results.append(f"[+] 已创建 QR 码: {qr.data}")
    results.append(f"[+] 尺寸: {qr.size}x{qr.size}mm")
    
    zpl3 = qr.to_zpl(dpi=203)
    results.append("[INFO] QR 码 ZPL:")
    results.append(zpl3)
    
    # 包含所有条形码的完整 ZPL
    results.append("\n[测试 4] 包含所有条形码的完整 ZPL")
    
    label_config = {
        'width': 100,
        'height': 100,
        'dpi': 203
    }
    
    generator = ZPLGenerator(dpi=203)
    elements = [ean13, code128, qr]
    
    full_zpl = generator.generate(elements, label_config)
    results.append("[INFO] 完整 ZPL:")
    results.append(full_zpl)
    
    results.append("\n[成功] 所有条形码测试通过!")
    
    # 保存结果
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
            f.write(f"异常: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        print(f"[错误] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

---

## 冲刺 3 检查点

**检查所有功能:**

1. ✅ BarcodeElement 基础类已创建
2. ✅ EAN13BarcodeElement 正常工作
3. ✅ Code128BarcodeElement 正常工作
4. ✅ QRCodeElement 正常工作
5. ✅ 工具栏有"添加条形码"按钮和子菜单
6. ✅ 可以在画布上添加 EAN-13
7. ✅ 可以在画布上添加 Code 128
8. ✅ 可以在画布上添加 QR 码
9. ✅ 属性面板显示条形码属性
10. ✅ 可以编辑数据、宽度、高度
11. ✅ 条形码拖放功能正常工作
12. ✅ 条形码的 ZPL 生成
13. ✅ 保存/加载功能与条形码配合使用
14. ✅ 预览显示条形码

**手动 GUI 测试:**

```bash
cd D:\AiKlientBank\1C_Zebra
.venv\Scripts\activate
python main.py
```

**测试:**
1. 点击"添加条形码" → 看到子菜单
2. 选择"EAN-13" → 出现蓝色矩形
3. 拖放移动它
4. 点击条形码 → 属性面板显示条形码属性
5. 将数据更改为其他值
6. 添加 Code 128 和 QR 码
7. 保存 → 保存为 "test_barcodes.json"
8. 加载 → 重新加载回来
9. 导出 ZPL → 看到带有 ^BE, ^BC, ^BQ 命令的 ZPL
10. 预览 → 在标签上看到条形码

**如果所有测试通过 - 冲刺 3 完成。**

**如果有任何问题 - 停止，修复，重新测试。**

---

## 沟通格式

**执行每个步骤时请写:**

```
=== 步骤 X.Y 执行中 ===

[命令或操作]

=== 测试 ===

[测试结果]

=== 状态 ===
[OK] 一切正常
或
[失败] 问题描述
```

**成功测试后等待命令:**
- "继续" - 转到下一步
- "修复 X" - 修复问题
- "显示代码 X" - 显示特定文件

---

## 开始工作

**执行步骤 3.1**

根据以上说明创建基础 BarcodeElement 和 GraphicsBarcodeItem 类。

完成后写状态并等待命令。