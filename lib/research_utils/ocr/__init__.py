"""OCR core functions — PaddleOCR text detection and character-level recognition."""

import cv2
import numpy as np
from pathlib import Path
from paddleocr import PaddleOCR, TextDetection


def extract_text_boxes(image_path, output_dir="cropped_boxes", visualize=True):
    """Use PaddleOCR to detect text bounding boxes and crop/save each box.

    Detection only — no recognition. Uses PP-OCRv5_server_det model.

    Args:
        image_path: Input image path.
        output_dir: Output directory for cropped boxes.
        visualize: Whether to generate PNG and HTML visualizations.

    Returns:
        List of detected polygon coordinates.
    """
    from research_utils.html import build_detection_html

    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    result = ocr.predict(str(image_path))

    boxes = []
    for res in result:
        json_result = res.json
        boxes = json_result.get("dt_polys", [])

    if not boxes:
        print("No text boxes detected.")
        return []

    print(f"Detected {len(boxes)} text bounding boxes.")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for f in out.glob("box_*.png"):
        f.unlink()

    for idx, box in enumerate(boxes):
        pts = np.array(box, dtype=np.int32)
        x, y, w, h = cv2.boundingRect(pts)
        cropped = img[y:y+h, x:x+w]
        save_path = out / f"box_{idx:04d}.png"
        cv2.imwrite(str(save_path), cropped)

    print(f"Cropped boxes saved to: {out}")

    if visualize:
        vis_img = img.copy()
        for box in boxes:
            pts = np.array(box, dtype=np.int32)
            cv2.polylines(vis_img, [pts], True, (0, 0, 255), 2)
        vis_path = out / "detection_result.png"
        cv2.imwrite(str(vis_path), vis_img)
        print(f"Visualization saved: {vis_path}")

        build_detection_html(out, img, boxes, Path(image_path))

    return boxes


def run_ocr_recognition(image_path, boxes=None):
    """Run full OCR (detection + recognition) on an image.

    Args:
        image_path: Input image path.
        boxes: Optional pre-detected boxes. If None, runs detection internally.

    Returns:
        PaddleOCR result object with rec_texts, rec_scores, rec_polys.
    """
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    result = ocr.predict(str(image_path))
    return result
