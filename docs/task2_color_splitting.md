# Task 2: 色彩分析字符切分

## 目标
通过颜色聚类分析，在竖排文字条中找到纯色行（背景色）作为字符间的自然切分边界。

## 背景
现有方法（`split_chars_v3/v4.py`）使用水平投影法切分字符，在字符间距不明显时效果差。色彩分析法利用碑文中"字体色"和"背景色"的天然对比，找到纯背景色行作为切分间隙。

## 输入
PaddleOCR 检测后裁剪出的单列文字条（如 `HUNoutput/pic5_crops/box_0000.png`）。仅处理竖排文字。

## 算法流程

```
输入: 裁剪后的文字列图片 (BGR)
  │
  ├── 1. 颜色聚类 (Otsu 二值化)
  │     灰度化 → Otsu 自动阈值 → 前景/背景二值图
  │     不需要区分哪个是字体哪个是背景
  │
  ├── 2. 逐行颜色占比分析
  │     每行计算白色像素占比 white_ratio
  │     主色占比 = max(white_ratio, 1 - white_ratio)
  │     主色占比 >= 95% → 标记为"纯色行"
  │
  ├── 3. 纯色行区间 → 间隔区域
  │     连续纯色行合并为一个间隔
  │     间隔最小宽度 >= 2px
  │     间隔中点 → 切分线
  │
  ├── 4. 降级策略
  │     找不到足够间隔 (< 3 个) → 退化为等分方法
  │     估算字符数 = 文字高度 / (文字宽度 × 1.3)
  │
  └── 5. 输出
        字符裁剪图 + 可视化图
```

## 核心函数

```python
def analyze_colors(img) -> tuple[int, np.ndarray]:
    """Otsu 二值化，返回 (阈值, 二值图)"""

def find_pure_rows(binary, purity=0.95) -> list[tuple[int, int]]:
    """找纯色行区间，返回 [(start, end), ...]"""

def split_by_color(img, output_dir=None, purity=0.95, min_char_height=15) -> list[tuple[int, int]]:
    """完整切分流程，返回字符区域 [(y1, y2), ...]"""
```

## 可视化输出
1. 左侧：原图
2. 右侧：逐行主色占比条形图（灰色=纯色行，深灰=非纯色行）
3. 红色横线：间隔区域中点（切分线）
4. 绿色横线：字符区域边界

## 与现有方法的关系
- `archive/split_chars_v3.py`: 投影法 + 间隙检测 + 等分补救
- `archive/split_chars_v4.py`: 裁剪文字区 + 投影法 + 等分补救
- **本方法**: 颜色聚类 + 纯色行检测 + 等分补救（降级策略相同，核心算法不同）

## 依赖
- `opencv-python`, `numpy`（已在 pyproject.toml 中）
- 无需额外依赖

## 文件
- 新建: `lib/research_utils/splitting/__init__.py`
- 测试数据: `HUNoutput/pic5_crops/` 中的裁剪文字条
- 参考: `archive/split_chars_v3.py`, `archive/split_chars_v4.py`

## 执行顺序
1. 创建 `lib/research_utils/splitting/__init__.py`
2. 在 pic5_crops 上的裁剪文字条上测试
3. 对比色彩分析法 vs 投影法的切分效果
4. 调整 purity 阈值（0.90-0.98）找到最优值
5. 集成到主 pipeline
