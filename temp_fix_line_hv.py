# -*- coding: utf-8 -*-
"""修复线条ZPL生成 - 水平/垂直线使用 ^GB，对角线使用 ^GD"""

file_path = r'D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 旧的错误代码（总是使用 ^GD）
old_code = '''    def to_zpl(self, dpi=203):
        """生成线条的ZPL命令

        格式: ^GD{width},{height},{thickness},{color},{orientation}
        """
        # 转换坐标 mm -> 点
        x1_dots = int(self.config.x * dpi / 25.4)
        y1_dots = int(self.config.y * dpi / 25.4)
        x2_dots = int(self.config.x2 * dpi / 25.4)
        y2_dots = int(self.config.y2 * dpi / 25.4)

        # 计算宽度和高度
        width_dots = abs(x2_dots - x1_dots)
        height_dots = abs(y2_dots - y1_dots)

        logger.debug(f"[SHAPE-ZPL-LINE] 起点: ({x1_dots}, {y1_dots}) 点")
        logger.debug(f"[SHAPE-ZPL-LINE] 终点: ({x2_dots}, {y2_dots}) 点")
        logger.debug(f"[SHAPE-ZPL-LINE] 宽度: {width_dots}, 高度: {height_dots} 点")

        # 厚度（点）
        thickness = int(self.config.thickness * dpi / 25.4)

        # 颜色 (B=黑色, W=白色)
        color = 'B' if self.config.color == 'black' else 'W'

        # 方向: L (左斜线 \\), R (右斜线 /)
        # 在ZPL中Y轴从上到下
        # R = / 当dx和dy符号不同时
        # L = \\ 当dx和dy符号相同时
        dx = x2_dots - x1_dots
        dy = y2_dots - y1_dots

        if dx * dy < 0:  # 符号不同 = /
            orientation = 'R'
        else:  # 符号相同 = \\
            orientation = 'L'

        logger.debug(f"[SHAPE-ZPL-LINE] 厚度={thickness}, 方向={orientation}")

        zpl_commands = [
            f"^FO{x1_dots},{y1_dots}",
            f"^GD{width_dots},{height_dots},{thickness},{color},{orientation}",
            "^FS"
        ]

        logger.debug(f"[SHAPE-ZPL-LINE] 已生成ZPL")
        return "\\n".join(zpl_commands)'''

# 新的正确代码（水平/垂直线使用 ^GB，对角线使用 ^GD）
new_code = '''    def to_zpl(self, dpi=203):
        """生成线条的ZPL命令

        水平/垂直线: ^GB{width},{height},{thickness}
        对角线: ^GD{width},{height},{thickness},{color},{orientation}
        """
        # 转换坐标 mm -> 点
        x1_dots = int(self.config.x * dpi / 25.4)
        y1_dots = int(self.config.y * dpi / 25.4)
        x2_dots = int(self.config.x2 * dpi / 25.4)
        y2_dots = int(self.config.y2 * dpi / 25.4)

        # 计算宽度和高度
        width_dots = abs(x2_dots - x1_dots)
        height_dots = abs(y2_dots - y1_dots)

        logger.debug(f"[SHAPE-ZPL-LINE] 起点: ({x1_dots}, {y1_dots}) 点")
        logger.debug(f"[SHAPE-ZPL-LINE] 终点: ({x2_dots}, {y2_dots}) 点")
        logger.debug(f"[SHAPE-ZPL-LINE] 宽度: {width_dots}, 高度: {height_dots} 点")

        # 厚度（点）
        thickness = int(self.config.thickness * dpi / 25.4)

        # 颜色 (B=黑色, W=白色)
        color = 'B' if self.config.color == 'black' else 'W'

        # 关键：确定线条类型
        is_horizontal = (height_dots == 0)
        is_vertical = (width_dots == 0)

        if is_horizontal:
            # 水平线: ^GB{width},{thickness},{thickness}
            logger.debug(f"[SHAPE-ZPL-LINE] 类型: 水平线, 使用 ^GB")
            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GB{width_dots},{thickness},{thickness},{color},0",
                "^FS"
            ]
        elif is_vertical:
            # 垂直线: ^GB{thickness},{height},{thickness}
            logger.debug(f"[SHAPE-ZPL-LINE] 类型: 垂直线, 使用 ^GB")
            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GB{thickness},{height_dots},{thickness},{color},0",
                "^FS"
            ]
        else:
            # 对角线: ^GD
            # 方向: L (左斜线 \\), R (右斜线 /)
            dx = x2_dots - x1_dots
            dy = y2_dots - y1_dots

            if dx * dy < 0:  # 符号不同 = /
                orientation = 'R'
            else:  # 符号相同 = \\
                orientation = 'L'

            logger.debug(f"[SHAPE-ZPL-LINE] 类型: 对角线, 方向={orientation}, 使用 ^GD")

            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GD{width_dots},{height_dots},{thickness},{color},{orientation}",
                "^FS"
            ]

        logger.debug(f"[SHAPE-ZPL-LINE] 生成的ZPL: {zpl_commands[1]}")
        return "\\n".join(zpl_commands)'''

# 执行替换
new_content = content.replace(old_code, new_code)

if new_content == content:
    print("[错误] 替换失败 - 未找到旧代码!")
    exit(1)

# 写入文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[成功] 线条ZPL生成已修复!")
print("变更内容:")
print("  1. 水平线 (y1==y2): ^GB{宽度},{厚度},{厚度}")
print("  2. 垂直线 (x1==x2): ^GB{厚度},{高度},{厚度}")
print("  3. 对角线: ^GD{宽度},{高度},{厚度},{颜色},{方向}")
print("\n现在所有线条类型的预览将与画布匹配!")