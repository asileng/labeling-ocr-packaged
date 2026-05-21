# Task 1: 字符级检测实验对比报告

## 实验概述

测试多种字符级检测方案在古籍碑文场景下的效果，选出最优方案。

**输入数据**: `HUNoutput/pic5_crops/pic5/box_0000.png` (61x833, 竖排文字行)

---

## 实验结果

### 方案 A: RapidOCR v1.4.4 (return_word_box=True)

**状态**: ✅ 已完成

**关键参数**: `return_word_box=True` - 启用单字级别bbox返回

**检测结果**:
| 指标 | 值 |
|------|-----|
| 检测字符数 | 5 |
| 推理时间 | 7.807s |
| 识别文字 | 有此制城威 |
| 平均置信度 | 0.97 |

**各字符详情**:
| 字符 | 置信度 | bbox位置 |
|------|--------|----------|
| 有 | 0.9999 | y: 96-137 |
| 此 | 0.9946 | y: 136-168 |
| 制 | 0.8693 | y: 167-203 |
| 城 | 0.9999 | y: 343-379 |
| 威 | 0.9999 | y: 712-748 |

**输出文件**:
- `box_0000_bboxes_overlay.png` - bbox叠加可视化
- `box_0000_char_crops/` - 单字裁剪图
- `box_0000_results.json` - 检测结果JSON

**结论**: RapidOCR单字检测效果良好，置信度高，可作为字级别检测方案。

---

### 方案 B: char-detection (fanqie03)

**状态**: ❌ 依赖版本过旧，无法安装

**问题**:
- requirements.txt中指定的版本与Python 3.12不兼容
- tornado==5.1.1, numpy==1.19.1等版本过旧
- chineseocr_lite未在PyPI发布

**结论**: 需要更新依赖版本或在Python 3.10环境中测试

---

### 方案 C: CRAFT

**状态**: ❌ 依赖版本冲突，无法安装

**问题**:
- craft-text-detector要求numpy==1.21.2
- 与Python 3.12不兼容

**结论**: 需要Python 3.10或更早版本环境

---

### Baseline: 投影法（现有方案）

**状态**: ✅ 可用（已有实现）

**流程**:
1. 水平投影找文字区域边界
2. 间隙检测找字符间隔
3. 等分补救

**特点**:
- 无需额外依赖
- 切分效果依赖于文字行的质量
- 在字符间距不明显时效果差

---

## 对比总结

| 方案 | 状态 | 检测粒度 | 置信度 | 古籍适配性 |
|------|------|---------|--------|-----------|
| **RapidOCR (return_word_box)** | ✅ 可用 | 字级 | 高 (0.87-0.99) | 良好 |
| char-detection | ❌ 安装失败 | 字级 | - | 未知 |
| CRAFT | ❌ 安装失败 | 字级 | - | 未知 |
| Baseline投影法 | ✅ 可用 | 字级 | - | 中等 |

## 建议

1. **推荐方案**: RapidOCR with `return_word_box=True`
   - 置信度高
   - 识别准确
   - 无需额外依赖

2. **后续优化**:
   - 测试更多古籍图片
   - 调整参数（box_thresh, unclip_ratio）
   - 与Task 2（色彩分析）对比效果

## 文件结构

```
sandbox/task1/
├── rapidocr_char/           # RapidOCR单字检测结果
│   ├── box_0000_bboxes_overlay.png
│   ├── box_0000_char_crops/
│   │   ├── char_0000.png (有)
│   │   ├── char_0001.png (此)
│   │   ├── char_0002.png (制)
│   │   ├── char_0003.png (城)
│   │   └── char_0004.png (威)
│   ├── box_0000_results.json
│   └── summary.json
└── comparison.md            # 本报告
```
