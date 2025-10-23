# -*- coding: utf-8 -*-
"""ZPL 标签设计器的条形码类"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor

from utils.logger import logger
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
        super().__init__(config)
        self.barcode_type = barcode_type
        self.data = data
        self.width = width
        self.height = height
        self.data_field = None
        self.show_text = True

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
        raise NotImplementedError

    def _get_barcode_data(self):
        return self.data_field if self.data_field else self.data


class GraphicsBarcodeItem(QGraphicsRectItem):
    """条形码图形元素"""

    def __init__(self, element: BarcodeElement, dpi=203, canvas=None):
        # 关键：使用实际宽度而不是 element.width！
        if hasattr(element, 'calculate_real_width'):
            real_width_mm = element.calculate_real_width(dpi)
            width_px = int(real_width_mm * dpi / 25.4)
            logger.debug(f"[条形码项目] 使用实际宽度: {real_width_mm:.1f}mm -> {width_px}px")
        else:
            # 回退用于 QRCode 和其他
            width_px = int(element.width * dpi / 25.4)
            logger.debug(f"[条形码项目] 使用 element.width: {element.width}mm -> {width_px}px")

        height_px = int(element.height * dpi / 25.4)

        super().__init__(0, 0, width_px, height_px)

        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # 引用 canvas 用于 GridConfig

        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

        pen = QPen(QColor(0, 0, 255), 2, Qt.DashLine)
        brush = QBrush(QColor(200, 220, 255, 100))
        self.setPen(pen)
        self.setBrush(brush)

        # 对齐网格 - 关键：在 setPos() 之前创建！
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0  # grid_step / 2 用于正确对齐

        # 设置位置（触发 itemChange）
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)

    def _mm_to_px(self, mm):
        return int(mm * self.dpi / 25.4)

    def _px_to_mm(self, px):
        return px * 25.4 / self.dpi

    def itemChange(self, change, value):
        """跟踪位置变化，带网格对齐功能"""
        # 网格对齐 - 移动时
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value

            # 转换为毫米
            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())

            logger.debug(
                f"[项目拖拽] 位置变化中: ({new_pos.x():.2f}, {new_pos.y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

            # 拖拽时发送光标位置给标尺
            if self.canvas:
                logger.debug(f"[项目拖拽] 发送光标位置: ({x_mm:.2f}, {y_mm:.2f})mm")
                self.canvas.cursor_position_changed.emit(x_mm, y_mm)

            if self.snap_enabled:
                # 对齐到网格（分别处理 X 和 Y）
                snapped_x = self._snap_to_grid(x_mm, 'x')
                snapped_y = self._snap_to_grid(y_mm, 'y')

                if snapped_x != x_mm or snapped_y != y_mm:
                    logger.debug(
                        f"[对齐] {x_mm:.2f}mm, {y_mm:.2f}mm -> {snapped_x:.1f}mm, {snapped_y:.1f}mm"
                    )

                # 转换回像素
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )

                return snapped_pos

            return new_pos

        # 更新元素 - 移动后
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            # 考虑对齐更新元素
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())

            logger.debug(
                f"[项目拖拽] 位置已改变（原始）: ({self.pos().x():.2f}, {self.pos().y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

            # 如果启用对齐，应用对齐
            if self.snap_enabled:
                x_mm = self._snap_to_grid(x_mm)
                y_mm = self._snap_to_grid(y_mm)

            self.element.config.x = x_mm
            self.element.config.y = y_mm

            if (
                    self.canvas
                    and getattr(self.canvas, 'bounds_update_callback', None)
                    and self.isSelected()
            ):
                logger.debug(
                    f"[项目拖拽] 位置已改变: 需要边界更新 "
                    f"({self.element.config.x:.2f}, {self.element.config.y:.2f})mm"
                )
                self.canvas.bounds_update_callback(self)

        return super().itemChange(change, value)

    def _snap_to_grid(self, value_mm, axis='x'):
        """使用 GridConfig（大小、偏移量）对齐到网格"""
        from config import SnapMode

        # 回退用于没有 canvas 的旧元素
        if not self.canvas:
            logger.debug(f"[对齐回退] 使用默认值: 大小=1.0mm, 偏移=0.0mm")
            size = 1.0
            offset = 0.0
            threshold = 1.0
        else:
            config = self.canvas.grid_config

            # 检查对齐模式
            if config.snap_mode != SnapMode.GRID:
                logger.debug(f"[对齐] 模式={config.snap_mode.value}, 跳过网格对齐")
                return value_mm

            size = config.size_x_mm if axis == 'x' else config.size_y_mm
            offset = config.offset_x_mm if axis == 'x' else config.offset_y_mm
            threshold = size / 2

            logger.debug(f"[对齐-{axis.upper()}] 值: {value_mm:.2f}mm, 偏移: {offset:.2f}mm, 大小: {size:.2f}mm")

        # 对齐公式：nearest = offset + round((value - offset) / size) * size
        relative = value_mm - offset
        rounded = round(relative / size) * size + offset

        logger.debug(f"[对齐-{axis.upper()}] 相对: {relative:.2f}mm, 四舍五入: {rounded:.2f}mm")

        if abs(value_mm - rounded) <= threshold:
            logger.debug(f"[对齐-{axis.upper()}] 结果: {value_mm:.2f}mm -> {rounded:.2f}mm")
            return rounded

        logger.debug(f"[对齐-{axis.upper()}] 未对齐（距离 > 阈值）")
        return value_mm

    def update_size(self, width, height):
        self.element.width = width
        self.element.height = height

        # 关键：使用实际宽度！
        if hasattr(self.element, 'calculate_real_width'):
            real_width_mm = self.element.calculate_real_width(self.dpi)
            width_px = self._mm_to_px(real_width_mm)
            logger.debug(f"[条形码项目] 更新: 实际宽度 {real_width_mm:.1f}mm -> {width_px}px")
        else:
            width_px = self._mm_to_px(width)

        height_px = self._mm_to_px(height)
        self.setRect(0, 0, width_px, height_px)


class EAN13BarcodeElement(BarcodeElement):
    """EAN-13 条形码"""

    def __init__(self, config: ElementConfig, data: str,
                 width: int = 20, height: int = 10):
        super().__init__(config, 'EAN13', data, width, height)
        self.module_width = 2  # 点（^BY 参数）

    def calculate_real_width(self, dpi=203):
        """基于模块宽度计算 EAN-13 的实际宽度

        EAN-13 结构:
        - 3 静区（左侧）
        - 3 起始保护符 (101)
        - 42 左半部分 (6 位数字 * 7 模块)
        - 5 中间保护符 (01010)
        - 42 右半部分 (6 位数字 * 7 模块)
        - 3 结束保护符 (101)
        - 7 静区（右侧）
        总计: 105 模块
        """
        total_modules = 105
        width_dots = total_modules * self.module_width
        width_mm = width_dots * 25.4 / dpi
        logger.debug(f"[条形码-EAN13] 实际宽度: {width_mm:.1f}mm ({total_modules} 模块 * {self.module_width} 点)")
        return width_mm

    def to_zpl(self, dpi):
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)

        logger.debug(f"[条形码-ZPL-EAN13] 位置: ({self.config.x:.1f}, {self.config.y:.1f})mm -> ({x_dots}, {y_dots})点")
        logger.debug(f"[条形码-ZPL-EAN13] 高度: {self.height:.1f}mm -> {height_dots}点")

        barcode_data = self._get_barcode_data()
        logger.debug(f"[条形码-ZPL-EAN13] 数据: '{barcode_data}'")

        # 计算实际宽度用于日志
        real_width_mm = self.calculate_real_width(dpi)
        logger.debug(f"[条形码-ZPL-EAN13] 实际宽度: {real_width_mm:.1f}mm（打印时将使用）")

        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY{self.module_width}")
        zpl_lines.append(f"^BEN,{height_dots},Y,N")
        zpl_lines.append(f"^FD{barcode_data}^FS")

        zpl = "\n".join(zpl_lines)
        logger.debug(f"[条形码-ZPL-EAN13] 已生成: {zpl.replace(chr(10), ' | ')}")

        return zpl

    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            width=data.get('width', 20),
            height=data.get('height', 10)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element


class Code128BarcodeElement(BarcodeElement):
    """Code 128 条形码"""

    def __init__(self, config: ElementConfig, data: str,
                 width: int = 30, height: int = 10):
        super().__init__(config, 'CODE128', data, width, height)
        self.module_width = 2  # 点（^BY 参数）

    def calculate_real_width(self, dpi=203):
        """基于模块宽度计算 CODE128 的实际宽度

        CODE128 结构:
        - 10 静区（左侧）
        - 11 起始字符
        - data_length * 11（每个字符平均值）
        - 13 停止字符（包括 2 条停止模式）
        - 10 静区（右侧）
        """
        data_length = len(self.data)
        total_modules = 10 + 11 + (data_length * 11) + 13 + 10
        width_dots = total_modules * self.module_width
        width_mm = width_dots * 25.4 / dpi
        logger.debug(
            f"[条形码-CODE128] 实际宽度: {width_mm:.1f}mm ({total_modules} 模块 * {self.module_width} 点, 数据长度={data_length})")
        return width_mm

    def to_zpl(self, dpi):
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)

        logger.debug(
            f"[条形码-ZPL-CODE128] 位置: ({self.config.x:.1f}, {self.config.y:.1f})mm -> ({x_dots}, {y_dots})点")
        logger.debug(f"[条形码-ZPL-CODE128] 高度: {self.height:.1f}mm -> {height_dots}点")

        barcode_data = self._get_barcode_data()
        logger.debug(f"[条形码-ZPL-CODE128] 数据: '{barcode_data}' (长度={len(barcode_data)})")

        # 计算实际宽度用于日志
        real_width_mm = self.calculate_real_width(dpi)
        logger.debug(f"[条形码-ZPL-CODE128] 实际宽度: {real_width_mm:.1f}mm（打印时将使用）")

        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY{self.module_width}")
        zpl_lines.append(f"^BCN,{height_dots},Y,N,N")
        zpl_lines.append(f"^FD{barcode_data}^FS")

        zpl = "\n".join(zpl_lines)
        logger.debug(f"[条形码-ZPL-CODE128] 已生成: {zpl.replace(chr(10), ' | ')}")

        return zpl

    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            width=data.get('width', 30),
            height=data.get('height', 10)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element


class QRCodeElement(BarcodeElement):
    """QR 码"""

    def __init__(self, config: ElementConfig, data: str,
                 size: int = 15):
        super().__init__(config, 'QRCODE', data, width=size, height=size)
        self.size = size
        self.magnification = 3

    def to_zpl(self, dpi):
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)

        barcode_data = self._get_barcode_data()

        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BQN,2,{self.magnification}")
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
            size=data.get('size', 15)
        )
        element.data_field = data.get('data_field')
        element.magnification = data.get('magnification', 3)
        return element