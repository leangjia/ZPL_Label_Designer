# -*- coding: utf-8 -*-
"""Fix Line ZPL - use ^GB for horizontal/vertical, ^GD for diagonal"""

file_path = r'D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# СТАРЫЙ НЕПРАВИЛЬНЫЙ код (ВСЕГДА ^GD)
old_code = '''    def to_zpl(self, dpi=203):
        """Генерація ZPL команд для line
        
        Format: ^GD{width},{height},{thickness},{color},{orientation}
        """
        # Конвертувати координати mm -> dots
        x1_dots = int(self.config.x * dpi / 25.4)
        y1_dots = int(self.config.y * dpi / 25.4)
        x2_dots = int(self.config.x2 * dpi / 25.4)
        y2_dots = int(self.config.y2 * dpi / 25.4)
        
        # Обчислити width і height
        width_dots = abs(x2_dots - x1_dots)
        height_dots = abs(y2_dots - y1_dots)
        
        logger.debug(f"[SHAPE-ZPL-LINE] From: ({x1_dots}, {y1_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-LINE] To: ({x2_dots}, {y2_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-LINE] Width: {width_dots}, Height: {height_dots} dots")
        
        # Thickness у dots
        thickness = int(self.config.thickness * dpi / 25.4)
        
        # Color (B=black, W=white)
        color = 'B' if self.config.color == 'black' else 'W'
        
        # Orientation: L (left lean \\), R (right lean /)
        # В ZPL Y идет сверху вниз
        # R = / когда dx и dy разных знаков
        # L = \\ когда dx и dy одинаковых знаков
        dx = x2_dots - x1_dots
        dy = y2_dots - y1_dots
        
        if dx * dy < 0:  # Разные знаки = /
            orientation = 'R'
        else:  # Одинаковые знаки = \\
            orientation = 'L'
        
        logger.debug(f"[SHAPE-ZPL-LINE] Thickness={thickness}, orientation={orientation}")
        
        zpl_commands = [
            f"^FO{x1_dots},{y1_dots}",
            f"^GD{width_dots},{height_dots},{thickness},{color},{orientation}",
            "^FS"
        ]
        
        logger.debug(f"[SHAPE-ZPL-LINE] Generated ZPL")
        return "\\n".join(zpl_commands)'''

# НОВЫЙ ПРАВИЛЬНЫЙ код (^GB для H/V, ^GD для diagonal)
new_code = '''    def to_zpl(self, dpi=203):
        """Генерація ZPL команд для line
        
        Horizontal/Vertical: ^GB{width},{height},{thickness}
        Diagonal: ^GD{width},{height},{thickness},{color},{orientation}
        """
        # Конвертувати координати mm -> dots
        x1_dots = int(self.config.x * dpi / 25.4)
        y1_dots = int(self.config.y * dpi / 25.4)
        x2_dots = int(self.config.x2 * dpi / 25.4)
        y2_dots = int(self.config.y2 * dpi / 25.4)
        
        # Обчислити width і height
        width_dots = abs(x2_dots - x1_dots)
        height_dots = abs(y2_dots - y1_dots)
        
        logger.debug(f"[SHAPE-ZPL-LINE] From: ({x1_dots}, {y1_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-LINE] To: ({x2_dots}, {y2_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-LINE] Width: {width_dots}, Height: {height_dots} dots")
        
        # Thickness у dots
        thickness = int(self.config.thickness * dpi / 25.4)
        
        # Color (B=black, W=white)
        color = 'B' if self.config.color == 'black' else 'W'
        
        # КРИТИЧНО: Определить тип линии
        is_horizontal = (height_dots == 0)
        is_vertical = (width_dots == 0)
        
        if is_horizontal:
            # ГОРИЗОНТАЛЬНАЯ линия: ^GB{width},{thickness},{thickness}
            logger.debug(f"[SHAPE-ZPL-LINE] Type: HORIZONTAL, using ^GB")
            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GB{width_dots},{thickness},{thickness},{color},0",
                "^FS"
            ]
        elif is_vertical:
            # ВЕРТИКАЛЬНАЯ линия: ^GB{thickness},{height},{thickness}
            logger.debug(f"[SHAPE-ZPL-LINE] Type: VERTICAL, using ^GB")
            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GB{thickness},{height_dots},{thickness},{color},0",
                "^FS"
            ]
        else:
            # ДИАГОНАЛЬНАЯ линия: ^GD
            # Orientation: L (left lean \\), R (right lean /)
            dx = x2_dots - x1_dots
            dy = y2_dots - y1_dots
            
            if dx * dy < 0:  # Разные знаки = /
                orientation = 'R'
            else:  # Одинаковые знаки = \\
                orientation = 'L'
            
            logger.debug(f"[SHAPE-ZPL-LINE] Type: DIAGONAL, orientation={orientation}, using ^GD")
            
            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GD{width_dots},{height_dots},{thickness},{color},{orientation}",
                "^FS"
            ]
        
        logger.debug(f"[SHAPE-ZPL-LINE] Generated ZPL: {zpl_commands[1]}")
        return "\\n".join(zpl_commands)'''

# Заменяем
new_content = content.replace(old_code, new_code)

if new_content == content:
    print("[ERROR] Replacement failed - old code not found!")
    exit(1)

# Записываем
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] Line ZPL generation fixed!")
print("Changes:")
print("  1. Horizontal lines (y1==y2): ^GB{width},{thickness},{thickness}")
print("  2. Vertical lines (x1==x2): ^GB{thickness},{height},{thickness}")
print("  3. Diagonal lines: ^GD{width},{height},{thickness},{color},{orientation}")
print("\nNow Preview will match Canvas for ALL line types!")
