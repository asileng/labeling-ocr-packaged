# Labeling OCR — LLM Prompt Templates

All prompts used with Qwen-VL via DashScope API (model: `qwen3-vl-plus`).

---

## Prompt 1: General OCR Text Extraction

**Purpose:** Extract all visible text from an ancient document image.

**Temperature:** 0.7 | **Top-p:** 0.8 | **Max tokens:** 1024

```
请返回这张图片中的文字
```

---

## Prompt 2: Character-to-Bbox Alignment with Ground Truth

**Purpose:** Align known ground truth text to detected bounding boxes, describing spatial layout first then content.

**Temperature:** 0.7 | **Top-p:** 0.8 | **Max tokens:** 1024

```
你现在是一个图片的文字标注员，这个图片中包含的是古籍。古籍中的文字已经确定了，我想测试你能否对齐这个文件（哪个文字应该出现在哪里）。先进行图片的大致理解和文字提取，然后使用我给的真实文本改善提取结果。你需要按照字块的分布位置进行描述，先描述字块集中在哪里，再描述字块中的具体文字内容
古籍中的文字是{ground_truth_text}
```

Where `{ground_truth_text}` is the known text for the page, e.g.:
> 汉麒麟碑/本名麒麟凤凰碑洪氏失去凤凰一纸止存麒麟碑 隶释云麒麟凤凰碑凡二石其像高二尺余图写各有生意题字甚大/隶续云汉人所图二瑞独此最为奇伟其一杂之故乡书庋中寻之未至/邃古斋藏

---

## Prompt 3: Structured Bbox-Text Alignment (JSON Output)

**Purpose:** Given pre-detected bounding boxes (as JSON) and ground truth text, assign each bbox the correct character(s). Output structured JSON.

**Temperature:** 0.7 | **Top-p:** 0.8 | **Max tokens:** 2048

```
你是一个古籍文字标注助手。我会给你一张古籍图片，以及一个 JSON 对象 `ocr_data`，其中包含了已经检测出的所有文字块（bbox），每个 bbox 有 `dt_polys`（多边形坐标）和 `id`（索引）。

任务：
1. 仔细观察图片中的文字分布。
2. 下面的「真实文本」是该古籍页面上所有文字的准确内容（按阅读顺序排列）。
3. 你需要判断每个 bbox 里应该填写哪个字或哪几个字（可能是单个字、词语或短句）。
4. 在返回的 JSON 中，保持原有结构不变，为每个 bbox 对象添加一个字段 "rec"，其值为该 bbox 对应的文字（字符串）。

真实文本：
{ground_truth_text}

输入 JSON（ocr_data）格式（dt_polys 是一个数组，每个元素是一个包含4个坐标点的多边形）：
[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], ...]

要求输出格式：返回一个 JSON 对象，包含 "dt_polys_rec" 数组，每个元素为 {"points": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "rec": "对应文字"}

注意事项：
- 所有 bbox 必须覆盖真实文本中的所有字符，不要遗漏。
- 如果某个 bbox 内图片上实际没有文字（检测错误），rec 设为空字符串 ""。
- 文字顺序为竖排：从右到左、从上到下阅读。
- 只输出 JSON，不要输出其他解释文字。

开始处理，下面是你要处理的 ocr_data：
{ocr_data_json}
```

---

## API Call Pattern

```python
import dashscope
from dashscope import MultiModalConversation
import base64
import os

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

with open(image_path, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

messages = [
    {
        "role": "user",
        "content": [
            {"image": f"data:image/jpeg;base64,{image_b64}"},
            {"text": prompt_text}
        ]
    }
]

response = MultiModalConversation.call(
    model="qwen3-vl-plus",
    messages=messages,
    temperature=0.7,
    top_p=0.8,
    max_tokens=2048
)
```
