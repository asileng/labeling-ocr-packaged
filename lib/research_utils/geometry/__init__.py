"""Geometry utilities for OCR bounding box manipulation."""


def split_by_square_overlap(poly, ratio=1.0, overlap_ratio=0.1):
    """Split a text bbox into character-level boxes using square overlap method.

    Divides a detected text bounding box along its long axis with configurable
    overlap between adjacent character boxes to handle ambiguous boundaries.

    Args:
        poly: List of 4 corner points [[x1,y1],[x2,y2],[x3,y3],[x4,y4]].
        ratio: Character size as fraction of the short axis. Default 1.0.
        overlap_ratio: Overlap between adjacent boxes as fraction of short axis.
                       Default 0.1 (10% overlap).

    Returns:
        List of dicts with keys x1, y1, x2, y2 for each character bbox.
        Returns empty list if char_size < 10 pixels.
    """
    import numpy as np

    pts = np.array(poly, dtype=np.int32)
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)
    w = x_max - x_min
    h = y_max - y_min
    short = min(w, h)
    long = max(w, h)

    char_size = int(short * ratio)
    if char_size < 10:
        return []

    overlap = int(short * overlap_ratio)
    step = char_size - overlap

    is_vertical = h >= w

    chars = []
    if is_vertical:
        pos = y_min
        while pos + char_size <= y_max:
            chars.append({
                "x1": int(x_min),
                "y1": int(pos),
                "x2": int(x_max),
                "y2": int(pos + char_size)
            })
            pos += step
        if y_max - pos > char_size * 0.5:
            chars.append({
                "x1": int(x_min),
                "y1": int(pos),
                "x2": int(x_max),
                "y2": int(y_max)
            })
    else:
        pos = x_min
        while pos + char_size <= x_max:
            chars.append({
                "x1": int(pos),
                "y1": int(y_min),
                "x2": int(pos + char_size),
                "y2": int(y_max)
            })
            pos += step
        if x_max - pos > char_size * 0.5:
            chars.append({
                "x1": int(pos),
                "y1": int(y_min),
                "x2": int(x_max),
                "y2": int(y_max)
            })
    return chars
