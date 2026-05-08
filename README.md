# Labeling OCR Packaged

PaddleOCR + Qwen-VL pipeline for character-level text detection and recognition on ancient Chinese documents.

## Quick Start

```python
from research_utils.geometry import split_by_square_overlap
from research_utils.ocr import extract_text_boxes, run_ocr_recognition
from research_utils.html import build_detection_html, build_annotation_html

# Detect text boxes
boxes = extract_text_boxes("page.jpg", output_dir="cropped_boxes")

# Split into character-level bboxes
char_bboxes = []
for box in boxes:
    char_bboxes.extend(split_by_square_overlap(box))

# Run VLM recognition and generate XML
result = run_ocr_recognition("page.jpg", char_bboxes, ground_truth="...")

# Generate visualization HTML
html = build_detection_html("page.jpg", result)
```

## Repository

- **Source**: [asileng/labeling-OCR](https://github.com/asileng/labeling-OCR)
- **Specs**: `specs/SPEC.md`
- **Prompts**: `prompts/PROMPTS.md`

## Dependencies

- `paddleocr` / `paddlepaddle` — OCR detection & recognition
- `dashscope` — Qwen-VL multi-modal API
- `opencv-python`, `Pillow`, `numpy`
