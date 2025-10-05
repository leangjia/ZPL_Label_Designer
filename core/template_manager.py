# -*- coding: utf-8 -*-
"""Менеджер шаблонів - збереження/завантаження JSON"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .elements.base import BaseElement
from .elements.text_element import TextElement
from utils.unit_converter import MeasurementUnit


class TemplateManager:
    """Менеджер шаблонів етикеток"""
    
    def __init__(self, templates_dir: str = "templates/library"):
        """
        Ініціалізація менеджера
        
        Args:
            templates_dir: Директорія для збереження шаблонів
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def save_template(self, 
                     name: str,
                     elements: List[BaseElement],
                     label_config: Dict[str, Any],
                     display_unit: MeasurementUnit = MeasurementUnit.MM,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Зберегти шаблон у JSON
        
        Args:
            name: Назва шаблону
            elements: Список елементів етикетки
            label_config: Конфігурація етикетки (width, height, dpi)
            display_unit: Одиниці вимірювання для відображення
            metadata: Додаткові метадані (автор, опис, тощо)
        
        Returns:
            Шлях до збереженого файлу
        """
        # Створити структуру JSON
        template_data = {
            "name": name,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "label_config": {
                "width_mm": label_config.get('width', 28),
                "height_mm": label_config.get('height', 28),
                "dpi": label_config.get('dpi', 203),
                "display_unit": display_unit.value  # ← зберегти як string
            },
            "elements": [element.to_dict() for element in elements],
            "metadata": metadata or {}
        }
        
        # Сформувати ім'я файлу
        safe_name = self._sanitize_filename(name)
        filepath = self.templates_dir / f"{safe_name}.json"
        
        # Записати JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Template saved: {filepath}")
        return str(filepath)
    
    def load_template(self, filepath: str) -> Dict[str, Any]:
        """
        Завантажити шаблон з JSON
        
        Args:
            filepath: Шлях до JSON файлу
        
        Returns:
            Dict з label_config та elements
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        
        # Конвертувати елементи з dict → objects
        elements = []
        for elem_data in template_data.get('elements', []):
            element = self._element_from_dict(elem_data)
            if element:
                elements.append(element)
        
        label_config = template_data.get('label_config', {})
        
        # Завантажити display_unit (default: MM)
        unit_str = label_config.get('display_unit', 'mm')
        try:
            display_unit = MeasurementUnit(unit_str)
        except ValueError:
            from utils.logger import logger
            logger.warning(f"[TEMPLATE] Invalid display_unit '{unit_str}', using MM")
            display_unit = MeasurementUnit.MM
        
        from utils.logger import logger
        logger.info(f"[TEMPLATE] Loaded with display_unit: {display_unit.value}")
        
        print(f"[INFO] Template loaded: {filepath} ({len(elements)} elements)")
        
        return {
            "name": template_data.get('name', 'Untitled'),
            "label_config": label_config,
            "display_unit": display_unit,  # ← повернути як enum
            "elements": elements,
            "metadata": template_data.get('metadata', {})
        }
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        Отримати список усіх шаблонів
        
        Returns:
            Список dict з 'name' та 'path'
        """
        templates = []
        
        for filepath in self.templates_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    templates.append({
                        "name": data.get('name', filepath.stem),
                        "path": str(filepath),
                        "created_at": data.get('created_at', ''),
                        "updated_at": data.get('updated_at', '')
                    })
            except Exception as e:
                print(f"[ERROR] Failed to read template {filepath}: {e}")
        
        return templates
    
    def delete_template(self, filepath: str) -> bool:
        """
        Видалити шаблон
        
        Args:
            filepath: Шлях до JSON файлу
        
        Returns:
            True якщо успішно видалено
        """
        try:
            os.remove(filepath)
            print(f"[INFO] Template deleted: {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete template {filepath}: {e}")
            return False
    
    def _element_from_dict(self, data: Dict[str, Any]) -> Optional[BaseElement]:
        """
        Конвертувати dict → BaseElement
        
        Args:
            data: Dict з даними елемента
        
        Returns:
            Об'єкт елемента або None
        """
        elem_type = data.get('type')
        
        if elem_type == 'text':
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
        
        elif elem_type == 'rectangle':
            from .elements.shape_element import RectangleElement
            return RectangleElement.from_dict(data)
        
        elif elem_type == 'circle':
            from .elements.shape_element import CircleElement
            return CircleElement.from_dict(data)
        
        elif elem_type == 'line':
            from .elements.shape_element import LineElement
            return LineElement.from_dict(data)
        
        elif elem_type == 'image':
            from .elements.image_element import ImageElement
            return ImageElement.from_dict(data)
        
        print(f"[WARNING] Unknown element type: {elem_type}")
        return None
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Очистити назву файлу від небезпечних символів
        
        Args:
            name: Оригінальна назва
        
        Returns:
            Безпечна назва файлу
        """
        # Замінити небезпечні символи на _
        safe_chars = []
        for char in name:
            if char.isalnum() or char in ('-', '_', ' '):
                safe_chars.append(char)
            else:
                safe_chars.append('_')
        
        safe_name = ''.join(safe_chars).strip()
        
        # Якщо пустий - дати дефолтну назву
        if not safe_name:
            safe_name = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return safe_name
