"""HTML visualization utilities for OCR detection and annotation results."""

from pathlib import Path


def build_detection_html(out_dir, img, boxes, image_path):
    """Generate an HTML page with semi-transparent yellow boxes overlaying the original image.

    Args:
        out_dir: Output directory for the HTML file.
        img: OpenCV image array (numpy array).
        boxes: List of polygon coordinates from OCR detection.
        image_path: Original image path for the src reference.
    """
    img_h, img_w = img.shape[:2]

    boxes_html = ""
    for idx, box in enumerate(boxes):
        import numpy as np
        pts = np.array(box, dtype=np.int32)
        x, y, w, h = cv2.boundingRect(pts)

        left = x / img_w * 100
        top = y / img_h * 100
        width = w / img_w * 100
        height = h / img_h * 100

        boxes_html += (
            f'<div class="box" id="box_{idx}" title="Box #{idx}" '
            f'style="left:{left:.4f}%;top:{top:.4f}%;width:{width:.4f}%;height:{height:.4f}%"></div>\n'
        )

    import cv2
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>Text Detection Result &mdash; {len(boxes)} boxes</title>
<style>
  .container {{ position: relative; display: inline-block; }}
  .container img {{ display: block; max-width: 100%; height: auto; }}
  .box {{
    position: absolute;
    background: rgba(255, 255, 0, 0.2);
    border: 1px solid rgba(255, 200, 0, 0.7);
    box-sizing: border-box;
  }}
  .box:hover {{
    background: rgba(255, 255, 0, 0.45);
    border-color: #ffc800;
    outline: 2px solid #ffc800;
    z-index: 10;
  }}
  .info {{ font-family: system-ui, sans-serif; margin: 10px 0; color: #666; }}
</style>
</head>
<body>
<h2>Detection Result &mdash; {len(boxes)} bounding boxes</h2>
<p class="info">Hover to highlight detection areas</p>
<div class="container">
  <img src="../{image_path.name}" alt="original">
  {boxes_html}
</div>
</body>
</html>"""

    html_path = out_dir / "detection_result.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML result saved: {html_path}")


def build_annotation_html(image_b64, vlm_result, img_width, img_height):
    """Generate an HTML page showing VLM annotation polygons with character labels.

    Args:
        image_b64: Base64-encoded image string (without data URI prefix).
        vlm_result: Dict with "dt_polys_rec" array, each having "points" and "rec".
        img_width: Natural image width for SVG viewBox.
        img_height: Natural image height for SVG viewBox.

    Returns:
        Complete HTML string ready to write to file.
    """
    img_src = f"data:image/jpeg;base64,{image_b64}"

    polygons = ""
    labels = ""
    for item in vlm_result["dt_polys_rec"]:
        pts = item["points"]
        points_str = " ".join(f"{p[0]},{p[1]}" for p in pts)
        polygons += f'<polygon points="{points_str}" class="bbox"/>'

        rec = item.get("rec", "")
        if rec:
            cx = sum(p[0] for p in pts) / 4
            cy = sum(p[1] for p in pts) / 4
            labels += f'<div class="label" style="left:{cx}px;top:{cy}px;">{rec}</div>'

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>
  body {{ margin: 0; background: #1a1a1a; display: flex; justify-content: center; padding: 20px; }}
  .container {{ position: relative; display: inline-block; }}
  img {{ display: block; max-width: 100%; }}
  svg {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }}
  polygon {{ fill: rgba(255,0,0,0.08); stroke: red; stroke-width: 2; transition: fill 0.2s; }}
  polygon:hover {{ fill: rgba(255,0,0,0.25); }}
  .label {{
    position: absolute; transform: translate(-50%,-50%);
    background: rgba(0,0,0,0.65); color: #fff; padding: 2px 6px;
    border-radius: 3px; font-size: 12px; white-space: nowrap;
    pointer-events: none; font-family: sans-serif;
  }}
</style>
</head>
<body>
<div class="container">
  <img src="{img_src}" id="img"/>
  <svg id="svg" viewBox="0 0 {img_width} {img_height}">
    {polygons}
  </svg>
  {labels}
</div>
<script>
  const img = document.getElementById('img');
  const svg = document.getElementById('svg');
  img.onload = () => {{
    svg.setAttribute('viewBox', `0 0 ${{img.naturalWidth}} ${{img.naturalHeight}}`);
  }};
</script>
</body>
</html>"""

    return html
