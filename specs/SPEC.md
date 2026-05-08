# Labeling OCR — PaddleOCR + Qwen-VL pipeline for ancient Chinese character-level annotation

## Overview

This pipeline detects text regions in ancient Chinese document images using PaddleOCR, splits detected boxes into character-level bounding boxes, and uses Qwen-VL (via DashScope API) to assign the correct characters to each box. The final output is a PASCAL VOC-style XML annotation file and an interactive HTML visualization.

## Core Pipeline

```
Input Image
  │
  ├──► PaddleOCR Detection ──► Text Polygons (dt_polys)
  │                              │
  │                              ├──► Crop & save individual boxes
  │                              ├──► Generate detection HTML overlay
  │                              └──► split_by_square_overlap ──► Character-level bboxes
  │
  ├──► PaddleOCR Recognition ──► rec_texts + rec_scores (baseline accuracy)
  │
  └──► Qwen-VL Multi-modal ──► Character-to-bbox alignment (JSON with rec field)
                                 │
                                 ├──► Convert to XML (PASCAL VOC format)
                                 └──► Generate annotation HTML (SVG overlay)
```

## Input/Output

| Item | Description |
|------|-------------|
| Input | Image file (JPG/BMP/PNG) of an ancient Chinese document page |
| Output | Cropped text boxes (PNG), character-level XML annotations, HTML visualizations |

## Python Dependencies

| Package | Purpose |
|---------|---------|
| paddleocr / paddlepaddle | Text detection and recognition |
| opencv-python | Image I/O, boundingRect, polygon drawing |
| numpy | Polygon coordinate manipulation |
| dashscope | Qwen-VL multi-modal API calls |
| Pillow | Image size detection |

## Reusable Functions

```python
from research_utils.geometry import split_by_square_overlap
from research_utils.ocr import extract_text_boxes, run_ocr_recognition
from research_utils.html import build_detection_html, build_annotation_html
```

## LLM Prompts

See `../prompts/PROMPTS.md` for complete prompt templates used with Qwen-VL.

## Project Structure

```
labeling-ocr (source)
├── extract_text_boxes.py    # Main detection script + HTML visualization
├── _run_ocr.py              # OCR → PASCAL VOC XML generation
└── test.ipynb               # Full pipeline: detect → split → VLM recognize → annotate
```
