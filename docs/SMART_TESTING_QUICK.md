# 智能测试 - 快速入门

## 🎯 传统测试的问题

```python
# ❌ 传统（盲目）测试:
assert element.config.x == 6.0  # 通过 ✓

# 但看不到:
# [SNAP] 6.55mm -> 6.6mm  (显示已吸附)
# [FINAL-POS] Before: 6.55mm
# [FINAL-POS] After: 6.55mm  ← 未吸附!
```

**结果偶然正确，但逻辑已损坏！**

## 🔬 解决方案：LogAnalyzer

智能测试解析 DEBUG 日志并检测3类问题：
- `SNAP_FINAL_MISMATCH` - SNAP显示一个值，FINAL显示另一个
- `NO_SNAP_IN_FINAL` - Before == After (吸附未生效)
- `FINAL_SAVED_MISMATCH` - After != Saved

## 📋 智能测试结构

### 1. 日志分析器

```python
class LogAnalyzer:
    @staticmethod
    def parse_snap_logs(log):
        """提取 [SNAP] 记录"""
        pattern = r'\[SNAP\] ([\d.]+)mm, ([\d.]+)mm -> ([\d.]+)mm, ([\d.]+)mm'
        return [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) 
                for m in re.findall(pattern, log)]
    
    @staticmethod
    def detect_issues(snap_logs, final_logs):
        """检测问题"""
        issues = []
        
        # 检查1: SNAP vs FINAL
        if snap_logs[-1][2] != final_logs['after'][-1][0]:
            issues.append({
                'type': 'SNAP_FINAL_MISMATCH',
                'desc': f'SNAP显示 {snap_logs[-1][2]}, 但 FINAL = {final_logs["after"][-1][0]}'
            })
        
        return issues
```

### 2. 带日志分析的测试

```python
def test_feature_smart():
    log_file = Path('logs/zpl_designer.log')
    file_size_before = log_file.stat().st_size  # 之前的大小
    
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
    issues = analyzer.detect_issues(snap_logs, final_logs)
    
    if issues:
        print(f"检测到 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        return 1
    
    return 0
```

## 🚀 运行测试

### 单个测试
```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_cursor_smart_test.py').read())
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_zoom_smart_test.py').read())
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_snap_smart_test.py').read())
```

### 所有测试
```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_all_smart_tests.py').read())
```

## 📊 添加 DEBUG 日志

### 画布视图
```python
def mouseMoveEvent(self, event):
    logger.debug(f"[CURSOR] 信号发射: {x_mm:.2f}mm, {y_mm:.2f}mm")

def wheelEvent(self, event):
    logger.debug(f"[ZOOM] 之前: scale={self.current_scale:.2f}, cursor_pos=({old_pos.x():.1f}, {old_pos.y():.1f})")
    # ... 缩放逻辑 ...
    logger.debug(f"[ZOOM] 之后: scale={self.current_scale:.2f}, cursor_pos=({new_pos.x():.1f}, {new_pos.y():.1f})")
```

### 标尺
```python
def update_cursor_position(self, mm):
    logger.debug(f"[RULER-{orientation_name}] 更新位置: {mm:.2f}mm")

def _draw_cursor_marker(self, painter):
    logger.debug(f"[RULER-{orientation_name}] 绘制位置: {pos_px}px")
```

## 🎯 画布功能的3个阶段

| 阶段 | 测试 | 检测内容 |
|------|------|-------------|
| **1. 光标跟踪** | `test_cursor_tracking_smart.py` | 光标 != 标尺更新<br>标尺更新 != 绘制 |
| **2. 点缩放** | `test_zoom_smart.py` | 光标偏移<br>标尺缩放不匹配 |
| **3. 网格吸附** | `test_snap_smart.py` | 吸附 != 最终<br>未应用吸附<br>最终 != 保存 |

## ✅ 使用时机

**必须使用：**
- ✅ 网格吸附
- ✅ 缩放
- ✅ 拖放
- ✅ 坐标转换
- ✅ 任何有中间状态的逻辑

**不需要：**
- ❌ 简单数学计算
- ❌ 无逻辑的getter/setter

## 🔑 关键规则

**没有日志分析 = 不工作！**