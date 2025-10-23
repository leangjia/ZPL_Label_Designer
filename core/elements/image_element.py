# -*- coding: utf-8 -*-
"""ZPL 标签设计器的图片元素"""

from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPixmap
from pathlib import Path
import base64
from PIL import Image
import io

from core.elements.base import BaseElement, ElementConfig
from utils.logger import logger


class ImageConfig(ElementConfig):
    """图片元素配置"""

    def __init__(self, x=0, y=0, width=30, height=30,
                 image_path=None, image_data=None):
        """
        Args:
            x, y: 位置（毫米）
            width, height: 尺寸（毫米）
            image_path: 原始文件路径（用于参考）
            image_data: Base64 编码的图片（用于保存到 JSON）
        """
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.image_path = image_path
        self.image_data = image_data


class ImageElement(BaseElement):
    """图片/Logo 元素"""

    def __init__(self, config=None):
        if config is None:
            config = ImageConfig()
        super().__init__(config)
        logger.debug(
            f"[图片元素] 已创建: 位置=({config.x:.2f}, {config.y:.2f})mm, 尺寸=({config.width}x{config.height})mm")

    def to_dict(self):
        """序列化到 dict 用于 JSON"""
        return {
            'type': 'image',
            'x': self.config.x,
            'y': self.config.y,
            'width': self.config.width,
            'height': self.config.height,
            'image_path': self.config.image_path,
            'image_data': self.config.image_data
        }

    @classmethod
    def from_dict(cls, data):
        """从 dict 反序列化"""
        config = ImageConfig(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            image_path=data.get('image_path'),
            image_data=data.get('image_data')
        )
        return cls(config)

    def to_zpl(self, dpi=203):
        """
        生成图片的 ZPL ^GFA 命令

        Returns:
            str: 打印图片的 ZPL 代码
        """
        if not self.config.image_data and not self.config.image_path:
            logger.warning(f"[图片-ZPL] 没有图片数据或路径")
            return ""

        # 转换坐标 mm → dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        width_dots = int(self.config.width * dpi / 25.4)
        height_dots = int(self.config.height * dpi / 25.4)

        logger.debug(f"[图片-ZPL] 位置: ({x_dots}, {y_dots}) 点")
        logger.debug(f"[图片-ZPL] 尺寸: ({width_dots}x{height_dots}) 点")

        # 转换图片为 ZPL hex 格式
        hex_data = self._convert_image_to_zpl_hex(width_dots, height_dots)

        if not hex_data:
            logger.error(f"[图片-ZPL] 转换图片失败")
            return ""

        # 生成 ZPL ^GFA 命令
        # 格式: ^GFA,{总字节数},{总字节数},{每行字节数},{十六进制数据}
        bytes_per_row = (width_dots + 7) // 8
        total_bytes = bytes_per_row * height_dots

        zpl_commands = [
            f"^FO{x_dots},{y_dots}",
            f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_data}",
            "^FS"
        ]

        logger.debug(f"[图片-ZPL] 已生成: 总字节数={total_bytes}, 每行字节数={bytes_per_row}")
        return "\n".join(zpl_commands)

    def _convert_image_to_zpl_hex(self, width_dots, height_dots):
        """
        转换图片为 ZPL hex 格式

        过程:
        1. 加载图片（从 base64 或路径）
        2. 调整到目标尺寸
        3. 转换为灰度
        4. 应用 Floyd-Steinberg 抖动 → 1位单色
        5. 转换像素为 hex 格式

        Args:
            width_dots: 宽度（点）
            height_dots: 高度（点）

        Returns:
            str: ^GFA 命令的十六进制数据
        """
        try:
            # === 1. 加载图片 ===
            if self.config.image_data:
                # 从 base64
                image_bytes = base64.b64decode(self.config.image_data)
                img = Image.open(io.BytesIO(image_bytes))
                logger.debug(f"[图片转换] 从 base64 加载")
            elif self.config.image_path:
                # 从文件
                img = Image.open(self.config.image_path)
                logger.debug(f"[图片转换] 从文件加载: {self.config.image_path}")
            else:
                logger.error(f"[图片转换] 没有图片源")
                return None

            logger.debug(f"[图片转换] 原始尺寸: {img.size}, 模式: {img.mode}")

            # === 2. 调整尺寸 ===
            img = img.resize((width_dots, height_dots), Image.Resampling.LANCZOS)
            logger.debug(f"[图片转换] 调整尺寸到: {width_dots}x{height_dots} 点")

            # === 3. 灰度转换 ===
            img = img.convert('L')
            logger.debug(f"[图片转换] 转换为灰度")

            # === 4. 抖动 → 单色 ===
            # Floyd-Steinberg 抖动以获得更好质量
            img = img.convert('1')
            logger.debug(f"[图片转换] 应用抖动 + 转换为 1 位单色")

            # === 5. 像素 → HEX 格式 ===
            hex_lines = []
            bytes_per_row = (width_dots + 7) // 8

            for y in range(height_dots):
                row_bytes = []

                for x in range(0, width_dots, 8):
                    byte_value = 0

                    # 8 像素 → 1 字节
                    for bit in range(8):
                        if x + bit < width_dots:
                            pixel = img.getpixel((x + bit, y))
                            # PIL '1' 模式: 0 = 黑色, 255 = 白色
                            # ZPL 格式: 1 = 黑色, 0 = 白色
                            if pixel == 0:  # 黑色像素
                                byte_value |= (1 << (7 - bit))

                    row_bytes.append(f"{byte_value:02X}")

                # 如果需要填充
                while len(row_bytes) < bytes_per_row:
                    row_bytes.append("00")

                hex_lines.append("".join(row_bytes))

            hex_data = "".join(hex_lines)
            logger.debug(f"[图片转换] 十六进制数据长度: {len(hex_data)} 字符 ({len(hex_data) // 2} 字节)")

            return hex_data

        except Exception as e:
            logger.error(f"[图片转换] 错误: {e}", exc_info=True)
            return None


class GraphicsImageItem(QGraphicsPixmapItem):
    """画布上图片的图形项"""

    # 用于更新属性面板的信号
    position_changed = Signal(float, float)

    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # 引用 canvas 用于 GridConfig

        # 对齐网格 - 关键：在 setPos() 之前创建！
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0

        # 加载图片
        self._load_image()

        # 设置位置
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)

        # 拖放标志
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        logger.debug(f"[图片项] 已创建于: ({element.config.x:.2f}, {element.config.y:.2f})mm")

    def _load_image(self):
        """加载并显示图片"""
        try:
            if self.element.config.image_data:
                # 从 base64
                image_bytes = base64.b64decode(self.element.config.image_data)
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes)
                logger.debug(f"[图片项] 从 base64 加载")
            elif self.element.config.image_path:
                # 从文件
                pixmap = QPixmap(self.element.config.image_path)
                logger.debug(f"[图片项] 从文件加载")
            else:
                # 占位符
                pixmap = QPixmap(100, 100)
                pixmap.fill(Qt.lightGray)
                logger.debug(f"[图片项] 创建占位符")

            # 调整到所需尺寸
            width_px = int(self._mm_to_px(self.element.config.width))
            height_px = int(self._mm_to_px(self.element.config.height))

            pixmap = pixmap.scaled(
                width_px,
                height_px,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.setPixmap(pixmap)
            logger.debug(f"[图片项] 已显示: 尺寸=({pixmap.width()}x{pixmap.height()})px")

        except Exception as e:
            logger.error(f"[图片项] 加载错误: {e}", exc_info=True)
            # 错误时的占位符
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.red)
            self.setPixmap(pixmap)

    def itemChange(self, change, value):
        """处理项目变化（网格对齐、位置更新）"""
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
                # 对齐到网格
                snapped_x = self._snap_to_grid(x_mm)
                snapped_y = self._snap_to_grid(y_mm)

                logger.debug(f"[图片对齐] ({x_mm:.2f}, {y_mm:.2f})mm -> ({snapped_x:.2f}, {snapped_y:.2f})mm")

                # 转换回像素
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )

                return snapped_pos

            return new_pos

        elif change == QGraphicsItem.ItemPositionHasChanged:
            # 移动后更新配置
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())

            logger.debug(
                f"[项目拖拽] 位置已改变（原始）: ({self.pos().x():.2f}, {self.pos().y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

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

            # 属性面板的信号
            self.position_changed.emit(x_mm, y_mm)

        return super().itemChange(change, value)

    def _snap_to_grid(self, value_mm):
        """将值对齐到网格"""
        nearest = round(value_mm / self.grid_step_mm) * self.grid_step_mm

        if abs(value_mm - nearest) <= self.snap_threshold_mm:
            return nearest

        return value_mm

    def _mm_to_px(self, mm):
        """转换毫米 → 像素"""
        return mm * self.dpi / 25.4

    def _px_to_mm(self, px):
        """转换像素 → 毫米"""
        return px * 25.4 / self.dpi

    def update_from_element(self):
        """从元素配置更新图形项"""
        self._load_image()

        x_px = self._mm_to_px(self.element.config.x)
        y_px = self._mm_to_px(self.element.config.y)
        self.setPos(x_px, y_px)

        logger.debug(f"[图片项] 从元素更新")