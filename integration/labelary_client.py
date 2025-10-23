# -*- coding: utf-8 -*-
"""Labelary API 客户端 (ZPL 预览)"""

import requests
from PIL import Image
from io import BytesIO
from utils.logger import logger


class LabelaryClient:
    """通过 Labelary API 获取预览的客户端"""

    BASE_URL = "http://api.labelary.com/v1/printers"

    # Labelary API 的有效 dpmm 值
    VALID_DPMM = [6, 8, 12, 24]

    def __init__(self, dpi=203):
        self.dpi = dpi
        logger.info(f"Labelary客户端已初始化，DPI: {dpi}")

    def _get_valid_dpmm(self, dpi: int) -> int:
        """
        获取 Labelary API 最接近的有效 dpmm 值

        Labelary 仅接受: 6, 8, 12, 24 dpmm

        Args:
            dpi: 打印机 DPI

        Returns:
            最接近的有效 dpmm 值
        """
        calculated_dpmm = dpi / 25.4

        # 找到最接近的有效值
        closest_dpmm = min(self.VALID_DPMM, key=lambda x: abs(x - calculated_dpmm))

        logger.info(f"DPI {dpi} -> 计算值 {calculated_dpmm:.2f} dpmm -> 使用有效值 {closest_dpmm} dpmm")

        return closest_dpmm

    def preview(self, zpl_code: str, width_mm: float, height_mm: float) -> Image:
        """
        获取标签的 PNG 预览

        Args:
            zpl_code: ZPL 代码
            width_mm: 宽度（毫米）
            height_mm: 高度（毫米）

        Returns:
            PIL Image 或出错时返回 None
        """
        logger.info("=" * 60)
        logger.info("LABELARY 预览请求")
        logger.info("=" * 60)

        try:
            # === 单位转换 ===
            width_inch = width_mm / 25.4
            height_inch = height_mm / 25.4
            dpmm = self._get_valid_dpmm(self.dpi)

            logger.info(f"输入尺寸: {width_mm}mm x {height_mm}mm")
            logger.info(f"转换为英寸: {width_inch:.2f} x {height_inch:.2f}")
            logger.info(f"使用有效 dpmm: {dpmm} (来自 DPI {self.dpi})")

            # === 构建 URL ===
            url = f"{self.BASE_URL}/{dpmm}dpmm/labels/{width_inch:.2f}x{height_inch:.2f}/0/"
            logger.info(f"API URL: {url}")

            # === ZPL 代码 ===
            logger.info(f"ZPL 代码长度: {len(zpl_code)} 字节")
            logger.debug("ZPL 代码内容:")
            logger.debug("-" * 40)
            for line in zpl_code.split('\n'):
                logger.debug(line)
            logger.debug("-" * 40)

            # === 请求头 ===
            headers = {'Accept': 'image/png'}
            logger.info(f"请求头: {headers}")

            # === 发送请求 ===
            logger.info("正在向 Labelary API 发送 POST 请求...")

            response = requests.post(
                url,
                data=zpl_code.encode('utf-8'),
                headers=headers,
                timeout=10
            )

            # === API 响应 ===
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")

            if response.status_code == 200:
                logger.info(f"响应内容长度: {len(response.content)} 字节")
                logger.info("预览生成成功 [+]")
                logger.info("=" * 60)
                return Image.open(BytesIO(response.content))
            else:
                # 错误详细信息
                logger.error(f"Labelary API 返回错误代码: {response.status_code}")
                logger.error(f"响应内容类型: {response.headers.get('content-type', 'unknown')}")
                logger.error(f"响应体长度: {len(response.content)} 字节")

                # 尝试显示错误文本
                try:
                    error_text = response.text
                    logger.error("响应体:")
                    logger.error("-" * 40)
                    logger.error(error_text)
                    logger.error("-" * 40)
                except:
                    logger.error("无法将响应体解码为文本")

                logger.info("=" * 60)
                return None

        except requests.exceptions.Timeout:
            logger.error("请求超时 (>10 秒)")
            logger.info("=" * 60)
            return None

        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            logger.info("=" * 60)
            return None

        except Exception as e:
            logger.error(f"预览过程中出现意外异常: {e}", exc_info=True)
            logger.info("=" * 60)
            return None