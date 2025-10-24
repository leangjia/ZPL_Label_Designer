# 画布/GUI智能测试

## 传统测试的问题

**传统测试看不到内部问题：**
```python
# 测试只检查最终结果
assert element.config.x == 6.0  # 通过 ✓

# 但看不到内部吸附功能没工作！
# 日志显示：
#   [SNAP] 6.55mm -> 6.6mm  (拖拽期间)
#   [FINAL-POS] Before: 6.55mm
#   [FINAL-POS] After: 6.55mm  ← 未吸附！
#   [FINAL-POS] Saved: 6.55mm
```

## 解决方案：日志分析

**智能测试分析日志并检测：**

1. **SNAP_FINAL_MISMATCH** - 最后的[SNAP]与[FINAL-POS After]不匹配
   ```
   [SNAP] 6.55mm -> 6.0mm  (显示已吸附)
   [FINAL-POS] After: 6.55mm  (但未吸附！)
   ```

2. **NO_SNAP_IN_FINAL** - [FINAL-POS Before] == [FINAL-POS After]
   ```
   [FINAL-POS] Before: 6.55mm
   [FINAL-POS] After: 6.55mm  (吸附未生效！)
   ```

3. **FINAL_SAVED_MISMATCH** - [FINAL-POS After] != [FINAL-POS Saved]
   ```
   [FINAL-POS] After: 6.0mm
   [FINAL-POS] Saved: 6.55mm  (保存了未吸附的值！)
   ```

## 智能测试结构

```python
class LogAnalyzer:
    """分析日志中的问题"""
    
    @staticmethod
    def parse_snap_logs(log_content):
        """提取所有[SNAP]记录"""
        pattern = r'\[SNAP\] ([\d.]+)mm, ([\d.]+)mm -> ([\d.]+)mm, ([\d.]+)mm'
        # 返回: [(from_x, from_y, to_x, to_y), ...]
    
    @staticmethod
    def parse_final_pos_logs(log_content):
        """提取所有[FINAL-POS]记录"""
        # 返回: {'before': [...], 'after': [...], 'saved': [...]}
    
    @staticmethod
    def detect_snap_issues(snap_logs, final_logs):
        """检测问题"""
        # 检查1: SNAP vs FINAL-POS After
        # 检查2: FINAL-POS Before vs After
        # 检查3: FINAL-POS After vs Saved
```

## 测试算法

1. **记录测试前的日志文件大小**
2. **执行操作**（例如拖拽元素）
3. **读取新日志**（从记录的位置开始）
4. **解析日志**（查找[SNAP], [FINAL-POS]）
5. **检测问题**（不匹配情况）
6. **输出详细报告**

## 使用示例

```python
def test_snap_with_log_analysis():
    log_file = Path('logs/zpl_designer.log')
    file_size_before = log_file.stat().st_size
    
    # 执行操作
    item.setPos(QPointF(x, y))
    app.processEvents()
    
    # 读取新日志
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 分析
    analyzer = LogAnalyzer()
    snap_logs = analyzer.parse_snap_logs(new_logs)
    final_logs = analyzer.parse_final_pos_logs(new_logs)
    issues = analyzer.detect_snap_issues(snap_logs, final_logs)
    
    # 检查
    if issues:
        for issue in issues:
            print(f"[!] {issue['type']}: {issue['desc']}")
        return 1  # 失败
    
    return 0  # 成功
```

## 优势

✅ **检测内部问题** - 能看到逻辑内部发生的情况
✅ **不依赖最终结果** - 即使结果偶然正确也能发现bug
✅ **详细诊断** - 显示具体哪里出了问题
✅ **防止回归** - 如果有人破坏了吸附功能能够捕获

## 检测示例

### 示例1：阈值太小（旧bug）
```
检测到 1 个问题：
1. NO_SNAP_IN_FINAL
   FINAL-POS Before=6.55mm, After=6.55mm (未吸附！)
   threshold=0.5 对于 distance=0.55 太小
```

### 示例2：ItemPositionHasChanged中的吸附不工作
```
检测到 1 个问题：
1. SNAP_FINAL_MISMATCH
   SNAP显示 6.0mm, 但 FINAL-POS After = 6.55mm
   Snap在ItemPositionChange中生效，但在ItemPositionHasChanged中未生效
```

## 文件

- `tests/test_snap_smart_v2.py` - 带日志分析的智能测试
- `tests/run_snap_smart_v2_test.py` - 智能测试运行器

## 使用时机

**始终**用于重要的Canvas/GUI功能内部逻辑：
- 网格吸附
- 缩放
- 拖放
- 坐标转换
- 任何有中间状态的逻辑

**不需要**用于没有日志的简单功能：
- 数学计算
- 简单的getter/setter
- 静态方法