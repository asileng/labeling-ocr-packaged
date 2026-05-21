# Task 1: 字符级检测实验

## 目标
测试多种字符级检测方案在古籍碑文场景下的效果，选出最优方案。

## 三个候选方案

### 方案 A: RapidOCR v1.4.0（主推）
- **原理**: 基于 PaddleOCR 推理引擎，v1.4.0 新增单字识别模式，返回单字坐标
- **优点**: PaddleOCR 生态成熟，无需 PyTorch，跨平台，性能好
- **安装**: `pip install rapidocr-onnxruntime` (ONNX 版) 或 `pip install rapidocr-openvino`
- **关键特性**: 支持单字级别检测 + 识别，一次调用同时返回坐标和文字
- **用法**: 待查文档确认具体 API（`det` 参数或 `level` 参数控制粒度）
- **风险**: 古籍碑文是否适配需要实际测试

### 方案 B: char-detection (fanqie03)
- **原理**: 基于 CRNN + CTC loss 的位置信息定位字符。CRNN 解码时字符位置映射到源图像像素位置
- **底层**: chineseocr_lite OCR 引擎 + DBNet 文字检测
- **安装**: `pip install -r requirements.txt`
- **用法**:
  ```bash
  python model.py --level char --images images/0.png   # 单字级别
  python model.py --level line --images images/0.png   # 行级别
  python model.py --level word --images images/0.png   # 词级别
  ```
- **特点**: 支持横排和竖排/古文，char 级别可逐字切分
- **风险**: 基于 chineseocr_lite，古籍场景效果未知

### 方案 C: CRAFT（备选）
- **原理**: Character Region Awareness for Text Detection，产出 per-character 的 region/affinity score map
- **安装**: `pip install craft-text-detector`（PyTorch）
- **方案 C1**: CRAFT 直接对整页检测
- **方案 C2**: PaddleOCR 行级 → CRAFT 行内
- **风险**: PyTorch 依赖重，古籍碑文背景复杂可能误检多

### Baseline: 投影法（现有方案）
- `split_chars_final.py` 的水平投影 + 间隙检测 + 等分补救
- 作为对比基准

## 对比实验设计

### 实验矩阵

| 方案 | 模式 | 说明 |
|------|------|------|
| A | RapidOCR 单字模式 | 一次调用，检测+识别 |
| B | char-detection --level char | CRNN 位置映射 |
| C1 | CRAFT 整页 | 端到端字符检测 |
| C2 | PaddleOCR 行 → CRAFT 行内 | 两级级联 |
| Baseline | 投影法 | 水平投影 + 间隙 + 等分 |

### 参数调优
- **RapidOCR**: 查文档确认单字模式相关参数，做参数扫描
- **char-detection**: `--level char` 固定，主要测试输入分辨率的影响
- **CRAFT**: `link_threshold` [0.05-0.4], `text_threshold` [0.2-0.7], `long_size` [1280-2560]

### 评估指标

| 指标 | 说明 |
|------|------|
| 字符数 | 检测到的区域数 vs 预期字符数 |
| bbox 面积 CV | 变异系数，越小越一致 |
| 宽高比分布 | 竖排文字应接近 1:1 |
| 字符间距标准差 | 同列内相邻字符间距应均匀 |
| 推理时间 | 总耗时 |
| 人工目视检查 | 热力图/bbox 叠加图人工评估 |

### 输出物
```
output_char_detection/
├── rapidocr/              # 方案 A
│   ├── pic1/
│   │   ├── bboxes_overlay.png
│   │   ├── char_crops/
│   │   └── results.json
│   └── ...
├── char_detection/        # 方案 B
│   ├── pic1/
│   │   ├── bboxes_overlay.png
│   │   ├── char_crops/
│   │   └── results.json
│   └── ...
├── craft/                 # 方案 C
│   ├── pic1/
│   │   ├── heatmap_text.png
│   │   ├── heatmap_link.png
│   │   ├── bboxes_overlay.png
│   │   ├── char_crops/
│   │   └── results.json
│   └── ...
├── baseline/              # 投影法
│   └── ...
└── comparison_table.md    # 五方案对比汇总
```

## 执行顺序
1. **方案 A**: 安装 RapidOCR，查文档确认单字模式 API，在 pic1 上测试
2. **方案 B**: 安装 char-detection，在 pic1 上跑 `--level char`
3. **方案 C**: 安装 CRAFT，在 pic1 上跑参数扫描
4. **Baseline**: 跑投影法
5. **全量测试**: 四个方案在 pic1-pic4 上跑
6. **对比**: 生成对比表，人工目视检查
7. **结论**: 选出最优方案（或组合方案）

## 依赖
- `rapidocr-onnxruntime`（方案 A，ONNX 推理）
- char-detection + `chineseocr_lite`（方案 B）
- `craft-text-detector`（方案 C，PyTorch）
- `paddleocr` + `paddlepaddle`（方案 C2 行检测）
- `opencv-python`, `numpy`（通用）

## 测试图片
- `source/pic1.jpg` - `pic4.jpg`（韩麒麟碑等古籍拓片）
- 预期字符数：需人工标注或从已有 pipeline 结果估算

## GPU 配置
- A100 48GB，CUDA 12
- 当前阶段用 API 调用，后期可迁移到本地推理
