# Labeling OCR Pipeline — Developer Notes

## Pipeline Stages

1. **Text Detection** — PaddleOCR detects text regions (polygons) in the image
2. **Box Cropping** — Each polygon is cropped and saved as `box_NNNN.png`
3. **Character Splitting** — `split_by_square_overlap()` divides text boxes into per-character boxes
4. **Recognition** — Two approaches:
   - PaddleOCR built-in recognition (baseline)
   - Qwen-VL multi-modal alignment (higher accuracy for ancient Chinese)
5. **Output** — JSON → XML (PASCAL VOC) + HTML visualization

## Qwen-VL Approach

The key insight is that PaddleOCR struggles with ancient Chinese fonts. Qwen-VL (a vision-language model) can align known ground-truth text to detected bounding boxes, achieving better character-level accuracy when you have reference text.

## XML Format

Output uses a custom PASCAL VOC-like format with 4-point polygons instead of simple bounding boxes:

```xml
<object>
  <name>字符内容</name>
  <bndbox>
    <x1>...</x1><y1>...</y1>
    <x2>...</x2><y2>...</y2>
    <x3>...</x3><y3>...</y3>
    <x4>...</x4><y4>...</y4>
  </bndbox>
</object>
```
