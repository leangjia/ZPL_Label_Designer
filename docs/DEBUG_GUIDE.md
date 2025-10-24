# 通过日志诊断问题指南

## 简介

1C_Zebra 的日志系统旨在进行详细的问题诊断。每个过程都记录了完整信息，可以准确定位问题来源。

## 日志级别

默认激活 **DEBUG** 模式：
```python
// config.py
LOG_LEVEL = "DEBUG"           // 所有内容到文件
CONSOLE_LOG_LEVEL = "DEBUG"   // 所有内容到控制台
```

这意味着在诊断时具有最大详细程度。

## Preview 时的日志结构

点击 "Preview" 按钮时记录完整链：

### 1. 请求初始化 (MainWindow)

```
============================================================
预览请求已启动
============================================================
[INFO] 元素数量: 1
[INFO] 元素 1: 类型=TextElement, 文本='新文本', 字体大小=25, 位置=(9.9, 9.9)
[INFO] 标签配置: {'width': 28, 'height': 28, 'dpi': 203}
[INFO] 无占位符，使用实际文本值
[INFO] 生成 ZPL 代码...
```

**检查内容：**
- ✅ 元素数量与 canvas 上的一致
- ✅ 元素坐标正确
- ✅ 标签配置正确 (28x28mm, DPI 203)

### 2. ZPL 生成 (ZPLGenerator)

```
============================================================
ZPL 生成开始
============================================================
[INFO] 元素数量: 1
[INFO] 标签配置: {'width': 28, 'height': 28, 'dpi': 203}
[DEBUG] 添加: ^XA (标签开始)
[DEBUG] 添加: ^CI28 (UTF-8 编码)
[INFO] 标签宽度: 28mm = 223 点 (^PW223)
[INFO] 标签高度: 28mm = 223 点 (^LL223)
[INFO] 处理元素 1/1: TextElement
[DEBUG]   文本: '新文本'
[DEBUG]   字体大小: 25
[DEBUG]   位置: (9.90mm, 9.90mm)
[DEBUG]   生成的 ZPL: ^FO79,79^A0N,25,25^FD新文本^FS
[DEBUG] 添加: ^XZ (标签结束)
[INFO] ZPL 生成完成: 67 字节, 7 行
============================================================
```

**检查内容：**
- ✅ mm -> 点转换正确 (28mm = 223 dots 在 203 DPI)
- ✅ 元素位置正确 (^FO79,79)
- ✅ ZPL 命令正确 (^A0N 用于字体, ^FD 用于数据)

**验证公式：**
```
dots = mm * DPI / 25.4
223 = 28 * 203 / 25.4 ✓
79 = 9.9 * 203 / 25.4 ✓
```

### 3. 最终 ZPL 代码 (DEBUG 模式)

```
============================================================
生成的 ZPL 代码:
============================================================
[DEBUG] ^XA
[DEBUG] ^CI28
[DEBUG] ^PW223
[DEBUG] ^LL223
[DEBUG] ^FO79,79^A0N,25,25^FD新文本^FS
[DEBUG] ^XZ
============================================================
```

**检查内容：**
- ✅ 以 ^XA 开始，以 ^XZ 结束
- ✅ 有 ^CI28 支持 UTF-8
- ✅ 命令未中断 (每个命令在自己的行或连续)

### 4. Labelary API 请求 (LabelaryClient)

```
============================================================
LABELARY 预览请求
============================================================
[INFO] 输入尺寸: 28mm x 28mm
[INFO] 转换为英寸: 1.10 x 1.10
[INFO] DPI: 203 -> dpmm: 8
[INFO] API URL: http://api.labelary.com/v1/printers/8dpmm/labels/1.10x1.10/0/
[INFO] ZPL 代码长度: 67 字节
[DEBUG] ZPL 代码内容:
[DEBUG] ----------------------------------------
[DEBUG] ^XA
[DEBUG] ^CI28
[DEBUG] ^PW223
[DEBUG] ^LL223
[DEBUG] ^FO79,79^A0N,25,25^FD新文本^FS
[DEBUG] ^XZ
[DEBUG] ----------------------------------------
[INFO] 请求头: {'Accept': 'image/png'}
[INFO] 发送 POST 请求到 Labelary API...
```

**检查内容：**
- ✅ 转换为英寸: 28mm / 25.4 = 1.10 inch ✓
- ✅ dpmm 正确: 203 / 25.4 = 8 ✓
- ✅ URL 格式正确
- ✅ ZPL 代码与生成的匹配

### 5. API 响应

#### 成功响应 (200):

```
[INFO] 响应状态码: 200
[INFO] 响应头: {'Content-Type': 'image/png', ...}
[INFO] 响应内容长度: 1523 字节
[INFO] 预览生成成功 [+]
============================================================
```

#### 错误 (400):

```
[ERROR] Labelary API 返回错误代码: 400
[ERROR] 响应内容类型: text/plain
[ERROR] 响应体长度: 156 字节
[ERROR] 响应体:
[ERROR] ----------------------------------------
[ERROR] ZPL 错误: 无效命令 ^A0N,25,25
[ERROR] 预期格式: ^A0N,height,width
[ERROR] ----------------------------------------
============================================================
```

**400 错误时检查：**
- ❌ Labelary 的错误文本 - 具体问题
- ❌ ZPL 命令格式 - 是否符合规范
- ❌ 数据编码 - 是否有无效字符

## 典型问题及其诊断

### 问题 1: 错误 400 - 无效 ZPL 命令

**日志显示：**
```
[ERROR] 响应体:
[ERROR] ZPL 错误: 无效命令 ^A0N,25,25
```

**原因：** ZPL 命令格式不正确

**解决方案：**
1. 在 zebra.com 检查命令规范
2. 在 `core/elements/text_element.py` 中修复格式
3. 检查命令参数顺序是否正确

### 问题 2: 元素在预览中不可见

**日志显示：**
```
[DEBUG]   位置: (0.50mm, 0.50mm)
[DEBUG]   生成的 ZPL: ^FO4,4^A0N,25,25^FD文本^FS
```

**原因：** 元素太靠近边缘 (在打印区域外)

**解决方案：** 最小位置应距边缘约 2-3mm

### 问题 3: 西里尔字符编码

**日志显示：**
```
[DEBUG] ^CI28
[DEBUG] ^FDПривет^FS
```

**检查：** 
- ✅ 文本前有 ^CI28 命令
- ✅ 文本为 UTF-8 编码

### 问题 4: 标签尺寸不正确

**日志显示：**
```
[INFO] API URL: http://api.labelary.com/v1/printers/8dpmm/labels/0.50x0.50/0/
[ERROR] Labelary API 返回错误代码: 400
[ERROR] 响应体: 标签尺寸太小
```

**原因：** Labelary 中最小标签尺寸为 1x1 英寸 (~25x25mm)

### 问题 5: 超时

**日志显示：**
```
[ERROR] 请求超时 (>10 秒)
```

**原因：** 网络问题或 Labelary API 不可用

**解决方案：** 检查互联网连接

## 完整成功 Preview 示例

```
============================================================
预览请求已启动
============================================================
[INFO] 元素数量: 1
[INFO] 元素 1: 类型=TextElement, 文本='Hello', 字体大小=30, 位置=(10.0, 10.0)
[INFO] 标签配置: {'width': 28, 'height': 28, 'dpi': 203}
[INFO] 无占位符，使用实际文本值
[INFO] 生成 ZPL 代码...

============================================================
ZPL 生成开始
============================================================
[INFO] 元素数量: 1
[INFO] 标签配置: {'width': 28, 'height': 28, 'dpi': 203}
[INFO] 标签宽度: 28mm = 223 点 (^PW223)
[INFO] 标签高度: 28mm = 223 点 (^LL223)
[INFO] 处理元素 1/1: TextElement
[DEBUG]   文本: 'Hello'
[DEBUG]   字体大小: 30
[DEBUG]   位置: (10.00mm, 10.00mm)
[DEBUG]   生成的 ZPL: ^FO80,80^A0N,30,30^FDHello^FS
[INFO] ZPL 生成完成: 65 字节, 7 行
============================================================

============================================================
LABELARY 预览请求
============================================================
[INFO] 输入尺寸: 28mm x 28mm
[INFO] 转换为英寸: 1.10 x 1.10
[INFO] DPI: 203 -> dpmm: 8
[INFO] API URL: http://api.labelary.com/v1/printers/8dpmm/labels/1.10x1.10/0/
[INFO] ZPL 代码长度: 65 字节
[INFO] 发送 POST 请求到 Labelary API...
[INFO] 响应状态码: 200
[INFO] 响应内容长度: 1842 字节
[INFO] 预览生成成功 [+]
============================================================

[INFO] 收到预览图像，显示对话框
[INFO] 图像尺寸: 223x223px
[INFO] 预览对话框已关闭
============================================================
```

## 如何使用日志进行调试

### 1. 重现问题

```bash
cd D:\AiKlientBank\1C_Zebra
.venv\Scripts\activate
python main.py
```

执行操作直到出现错误。

### 2. 打开日志文件

```bash
type logs\zpl_designer.log
```

或

```powershell
notepad logs\zpl_designer.log
```

### 3. 查找错误部分

搜索关键词：
- `ERROR` - 错误
- `PREVIEW REQUEST` - preview 过程开始
- `LABELARY PREVIEW REQUEST` - API 请求
- `Response status code: 400` - API 错误

### 4. 分析序列

按顺序从 `PREVIEW REQUEST INITIATED` 到错误阅读日志：
1. 检查元素
2. 检查 ZPL 生成
3. 检查 URL 和 API 参数
4. 阅读 Labelary 的错误文本

### 5. 与工作示例比较

将自己的日志与上面的示例比较 - 差异在哪里？

## 配置日志详细程度

### 最大详细程度 (默认)

```python
// config.py
LOG_LEVEL = "DEBUG"
CONSOLE_LOG_LEVEL = "DEBUG"
```

显示 **所有内容**：每行 ZPL、每次转换、每个参数。

### 仅错误

```python
// config.py
LOG_LEVEL = "INFO"           // 所有内容到文件
CONSOLE_LOG_LEVEL = "ERROR"  // 仅错误到控制台
```

静默工作，但文件中有完整日志。

### 平衡 (调试后推荐)

```python
// config.py
LOG_LEVEL = "INFO"
CONSOLE_LOG_LEVEL = "INFO"
```

主要事件，无转换细节。

## 实时监控

### Windows PowerShell

```powershell
// 监控日志
Get-Content logs\zpl_designer.log -Wait -Tail 50
```

### 按级别过滤

```powershell
// 仅错误
Get-Content logs\zpl_designer.log | Select-String "ERROR"

// Preview 部分
Get-Content logs\zpl_designer.log | Select-String -Context 5 "PREVIEW REQUEST"
```

## 发送日志寻求帮助

请求帮助时发送：
1. 完整日志文件 `logs/zpl_designer.log`
2. 有问题元素的 canvas 截图
3. 错误前的操作描述

## 结论

详细日志允许：
- ✅ 准确定位错误发生的阶段
- ✅ 查看所有参数和转换
- ✅ 了解 ZPL 代码的具体问题
- ✅ 获取 Labelary API 的错误文本
- ✅ 快速修复问题

**记住：** 日志是为了阅读而写的！不要忽略日志中的细节 - 那里有"为什么不工作"的答案。

---

**版本：** 1.0  
**日期：** 2025-10-03