# -*- coding: utf-8 -*-
"""Клиент для Labelary API (preview ZPL)"""

import requests
from PIL import Image
from io import BytesIO
from utils.logger import logger

class LabelaryClient:
    """Клиент для получения preview через Labelary API"""
    
    BASE_URL = "http://api.labelary.com/v1/printers"
    
    # Валидные значения dpmm для Labelary API
    VALID_DPMM = [6, 8, 12, 24]
    
    def __init__(self, dpi=203):
        self.dpi = dpi
        logger.info(f"LabelaryClient initialized with DPI {dpi}")
    
    def _get_valid_dpmm(self, dpi: int) -> int:
        """
        Получить ближайшее валидное значение dpmm для Labelary API
        
        Labelary принимает ТОЛЬКО: 6, 8, 12, 24 dpmm
        
        Args:
            dpi: DPI принтера
            
        Returns:
            Ближайшее валидное значение dpmm
        """
        calculated_dpmm = dpi / 25.4
        
        # Найти ближайшее валидное значение
        closest_dpmm = min(self.VALID_DPMM, key=lambda x: abs(x - calculated_dpmm))
        
        logger.info(f"DPI {dpi} -> calculated {calculated_dpmm:.2f} dpmm -> using valid {closest_dpmm} dpmm")
        
        return closest_dpmm
    
    def preview(self, zpl_code: str, width_mm: float, height_mm: float) -> Image:
        """
        Получить PNG preview этикетки
        
        Args:
            zpl_code: ZPL код
            width_mm: Ширина в мм
            height_mm: Высота в мм
        
        Returns:
            PIL Image или None при ошибке
        """
        logger.info("="*60)
        logger.info("LABELARY PREVIEW REQUEST")
        logger.info("="*60)
        
        try:
            # === КОНВЕРТАЦИЯ ЕДИНИЦ ===
            width_inch = width_mm / 25.4
            height_inch = height_mm / 25.4
            dpmm = self._get_valid_dpmm(self.dpi)
            
            logger.info(f"Input dimensions: {width_mm}mm x {height_mm}mm")
            logger.info(f"Converted to inches: {width_inch:.2f} x {height_inch:.2f}")
            logger.info(f"Using valid dpmm: {dpmm} (from DPI {self.dpi})")
            
            # === ФОРМИРОВАНИЕ URL ===
            url = f"{self.BASE_URL}/{dpmm}dpmm/labels/{width_inch:.2f}x{height_inch:.2f}/0/"
            logger.info(f"API URL: {url}")
            
            # === ZPL КОД ===
            logger.info(f"ZPL code length: {len(zpl_code)} bytes")
            logger.debug("ZPL code content:")
            logger.debug("-" * 40)
            for line in zpl_code.split('\n'):
                logger.debug(line)
            logger.debug("-" * 40)
            
            # === ЗАГОЛОВКИ ЗАПРОСА ===
            headers = {'Accept': 'image/png'}
            logger.info(f"Request headers: {headers}")
            
            # === ОТПРАВКА ЗАПРОСА ===
            logger.info("Sending POST request to Labelary API...")
            
            response = requests.post(
                url,
                data=zpl_code.encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            # === ОТВЕТ ОТ API ===
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                logger.info(f"Response content length: {len(response.content)} bytes")
                logger.info("Preview generated successfully [+]")
                logger.info("="*60)
                return Image.open(BytesIO(response.content))
            else:
                # Детальная информация об ошибке
                logger.error(f"Labelary API returned error code: {response.status_code}")
                logger.error(f"Response content type: {response.headers.get('content-type', 'unknown')}")
                logger.error(f"Response body length: {len(response.content)} bytes")
                
                # Попытаться показать текст ошибки
                try:
                    error_text = response.text
                    logger.error("Response body:")
                    logger.error("-" * 40)
                    logger.error(error_text)
                    logger.error("-" * 40)
                except:
                    logger.error("Could not decode response body as text")
                
                logger.info("="*60)
                return None
        
        except requests.exceptions.Timeout:
            logger.error("Request timeout (>10 seconds)")
            logger.info("="*60)
            return None
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            logger.info("="*60)
            return None
        
        except Exception as e:
            logger.error(f"Unexpected exception during preview: {e}", exc_info=True)
            logger.info("="*60)
            return None
