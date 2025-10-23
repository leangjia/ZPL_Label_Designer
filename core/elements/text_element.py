# -*- coding: utf-8 -*-
"""标签文本元素"""

from PySide6.QtWidgets import QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QFont

from utils.logger import logger
from .base import BaseElement, ElementConfig
from enum import Enum


class ZplFont(Enum):
    """ZEBRA 打印机字体"""
    SCALABLE_0 = ("0", "可缩放 (类似 Helvetica)", True, (10, 32000))
    FONT_A = ("A", "9x5 等宽", False, (9, 5))
    FONT_B = ("B", "11x7 等宽", False, (11, 7))
    FONT_C = ("C", "18x10 等宽斜体", False, (18, 10))
    FONT_D = ("D", "18x10 等宽", False, (18, 10))
    FONT_E = ("E", "28x15 OCR-B", False, (28, 15))
    FONT_F = ("F", "26x13 等宽", False, (26, 13))
    FONT_G = ("G", "60x40 大号", False, (60, 40))
    FONT_H = ("H", "34x22 OCR-A", False, (34, 22))

    def __init__(self, zpl_code, display_name, scalable, base_size):
        self.zpl_code = zpl_code
        self.display_name = display_name
        self.scalable = scalable
        self.base_width, self.base_height = base_size

    @classmethod
    def from_zpl_code(cls, code):
        """根据 ZPL 代码查找字体"""
        for font in cls:
            if font.zpl_code == code:
                return font
        return cls.SCALABLE_0  # 默认


class TextElement(BaseElement):
    """文本元素"""

    def __init__(self, config: ElementConfig, text="文本", font_size=20, font_family=None):
        super().__init__(config)
        self.text = text
        self.font_size = font_size
        self.font_family = font_family or ZplFont.SCALABLE_0  # 默认字体 0
        self.data_field = None  # 占位符 {{FIELD}}
        # 字体样式
        self.bold = False
        self.italic = False  # 没有字体上传时 ZPL 不支持斜体
        self.underline = False

    def to_dict(self):
        return {
            'type': 'text',
            'x': self.config.x,
            'y': self.config.y,
            'text': self.text,
            'font_size': self.font_size,
            'font_family': self.font_family.zpl_code,  # 保存 ZPL 代码
            'data_field': self.data_field,
            'bold': self.bold,
            'italic': self.italic,
            'underline': self.underline
        }

    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])

        # 向后兼容：如果缺少 font_family -> 字体 0
        font_code = data.get('font_family', '0')
        font_family = ZplFont.from_zpl_code(font_code)

        element = cls(config, data['text'], data['font_size'], font_family)
        element.data_field = data.get('data_field')
        element.bold = data.get('bold', False)
        element.italic = data.get('italic', False)
        element.underline = data.get('underline', False)
        return element

    def to_zpl(self, dpi):
        """生成 ZPL 代码"""

        # 转换毫米 → dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)

        # 使用占位符或文本
        content = self.data_field if self.data_field else self.text

        # 字体高度和宽度
        font_height = self.font_size

        # 粗体：字体宽度增加 50%（仅适用于字体 0）
        if self.bold and self.font_family == ZplFont.SCALABLE_0:
            font_width = int(font_height * 1.5)
        else:
            font_width = font_height  # 等比例

        # ZPL 字体命令: ^A{字体代码}N,{高度},{宽度}
        font_cmd = f"^A{self.font_family.zpl_code}N,{font_height},{font_width}"

        logger.debug(
            f"[ZPL-字体] 字体={self.font_family.zpl_code} "
            f"({self.font_family.display_name}), "
            f"高度={font_height}, 宽度={font_width}"
        )

        # 生成 ZPL
        lines = []
        lines.append(f"^FO{x_dots},{y_dots}")
        lines.append(font_cmd)
        lines.append(f"^FD{content}^FS")

        # 下划线：在文本下方绘制线条
        if self.underline:
            # 线条位置: y + font_height + 2px 偏移
            underline_y = y_dots + font_height + 2

            # 文本长度（点，近似值）
            char_count = len(content)
            avg_char_width = font_height * 0.6  # 大约高度的 60%
            text_width = int(char_count * avg_char_width)

            underline_cmd = f"^FO{x_dots},{underline_y}^GB{text_width},1,1^FS"
            lines.append(underline_cmd)
            logger.debug(f"[ZPL-下划线] y={underline_y}, 宽度={text_width}px")

        logger.debug(f"[ZPL-字体样式] 粗体={self.bold}, 斜体={self.italic}, 下划线={self.underline}")

        return '\n'.join(lines)


class GraphicsTextItem(QGraphicsTextItem):
    """带有拖放功能的图形文本元素"""

    position_changed = Signal(float, float)  # x, y 以毫米为单位

    def __init__(self, element: TextElement, dpi=203, canvas=None):
        super().__init__(element.text)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # 引用 canvas 用于 GridConfig

        # 设置
        self.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.setFlag(QGraphicsTextItem.ItemIsSelectable)
        self.setFlag(QGraphicsTextItem.ItemSendsGeometryChanges)

        # 为 ZEBRA 字体设置正确的 Qt 字体
        font = self._get_qt_font_for_zebra_font(element.font_size)
        self.setFont(font)

        # 对齐网格 - 关键：在 setPos() 之前创建！
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0  # grid_step / 2 用于完全对齐

        # 设置位置（触发 itemChange）
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)

        # 更新显示（如果有占位符则显示）
        self.update_display_text()

    def _mm_to_px(self, mm):
        return mm * self.dpi / 25.4

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
                logger.debug(f"[项目拖拽] 发送光标: ({x_mm:.2f}, {y_mm:.2f})mm")
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
        if change == QGraphicsTextItem.ItemPositionHasChanged:
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

            # 发送变化信号
            self.position_changed.emit(
                self.element.config.x,
                self.element.config.y
            )

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

        # 对齐公式: nearest = offset + round((value - offset) / size) * size
        relative = value_mm - offset
        rounded = round(relative / size) * size + offset

        logger.debug(f"[对齐-{axis.upper()}] 相对: {relative:.2f}mm, 四舍五入: {rounded:.2f}mm")

        if abs(value_mm - rounded) <= threshold:
            logger.debug(f"[对齐-{axis.upper()}] 结果: {value_mm:.2f}mm -> {rounded:.2f}mm")
            return rounded

        logger.debug(f"[对齐-{axis.upper()}] 未对齐（距离 > 阈值）")
        return value_mm

    def update_text(self, text):
        """更新文本"""
        self.element.text = text
        self.update_display_text()

    def _get_qt_font_for_zebra_font(self, size):
        """获取用于可视化 ZEBRA 字体的 Qt 字体"""
        zpl_font = self.element.font_family

        if zpl_font == ZplFont.SCALABLE_0:
            # 字体 0: Arial 粗体 (类似 Helvetica)
            font = QFont("Arial", size)
            font.setBold(True)
            logger.debug(f"[画布字体] 字体 0 -> Arial 粗体, 大小={size}")

        elif zpl_font == ZplFont.FONT_C:
            # 字体 C: Courier 斜体
            font = QFont("Courier New", size)
            font.setItalic(True)
            logger.debug(f"[画布字体] 字体 C -> Courier 斜体, 大小={size}")

        elif zpl_font in [ZplFont.FONT_E, ZplFont.FONT_H]:
            # 字体 E, H: OCR 字体 (回退到 Courier)
            # 尝试使用 OCR-A 或 OCR-B（如果已安装）
            font_name = "OCR A Extended" if zpl_font == ZplFont.FONT_H else "OCR B"
            font = QFont(font_name, size)
            if not font.exactMatch():
                # 回退到 Courier
                font = QFont("Courier New", size)
                logger.debug(f"[画布字体] 字体 {zpl_font.zpl_code} -> Courier (OCR 不可用), 大小={size}")
            else:
                logger.debug(f"[画布字体] 字体 {zpl_font.zpl_code} -> {font_name}, 大小={size}")

        else:
            # 字体 A, B, D, F, G: Courier New (等宽)
            font = QFont("Courier New", size)
            logger.debug(f"[画布字体] 字体 {zpl_font.zpl_code} -> Courier New, 大小={size}")

        # 应用用户样式（粗体、下划线）
        if self.element.bold and zpl_font != ZplFont.SCALABLE_0:
            # 字体 0 始终为粗体，其他字体如果用户启用则应用
            font.setBold(True)

        if self.element.underline:
            font.setUnderline(True)

        return font

    def update_font_size(self, font_size):
        """更新字体大小"""
        self.element.font_size = font_size
        # 为 ZEBRA 字体使用正确的字体
        font = self._get_qt_font_for_zebra_font(font_size)
        self.setFont(font)

    def update_font_family(self):
        """更新字体族（从属性面板调用）"""
        logger.debug(
            f"[画布字体] 更新字体族为 {self.element.font_family.zpl_code} ({self.element.font_family.display_name})")
        font = self._get_qt_font_for_zebra_font(self.element.font_size)
        self.setFont(font)
        logger.debug(f"[画布字体] 字体族更新成功")

    def update_display_text(self):
        """更新显示的文本（占位符或文本）"""
        # 如果有占位符则显示占位符，否则显示文本
        display = self.element.data_field if self.element.data_field else self.element.text
        self.setPlainText(display)

    def update_display(self):
        """更新视觉显示，考虑样式"""

        font = self.font()

        # 粗体
        font.setBold(self.element.bold)

        # 下划线
        font.setUnderline(self.element.underline)

        # 斜体 - 不设置，因为 ZPL 不支持
        # font.setItalic(self.element.italic)  # ← 不要这样做！

        self.setFont(font)
        logger.debug(f"[文本项] 显示已更新: 粗体={self.element.bold}, 下划线={self.element.underline}")