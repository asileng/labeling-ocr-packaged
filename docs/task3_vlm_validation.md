# Task 3: VLM 字符完整性验证

## 目标
用 Qwen2.5-VL-3B via DashScope API 验证每个字符图片是否包含完整、单一的汉字。

## 验证范围（只做完整性，不做识别）
- 单字：图片中只有一个汉字
- 完整：字没有被截断
- 不含其他字：不包含相邻字符的边缘
- **不负责识别具体是什么字**（那是 HUNet 的工作）

## Pipeline 位置
```
PaddleOCR 行检测 → 字符切分 → char crops → [本模块: VLM 验证] → 有效 crops → HUNet 识别
```

## 模型选择
- 模型: `qwen2.5-vl-3b-instruct`
- 平台: DashScope API（付费版）
- 选择理由: 3B 参数量小、中文支持最好、API 稳定

## Prompt 设计
```
这个图片中是否包含一个完整的汉字？只回答 yes 或 no。
```
- Temperature: 0.1（确定性输出）
- Max tokens: 10

## 响应解析策略（保守）
```python
def _parse_yes_no(response_text):
    text = response_text.strip().lower()
    if "yes" in text: return True
    if "no" in text: return False
    if "是" in text and "否" not in text and "不" not in text: return True
    return False  # 模糊回复默认拒绝
```
保守策略：无法明确判断时默认拒绝（False），宁可漏掉有效字符也不引入噪声。

## 核心函数

```python
def _call_vlm(image_b64, prompt, max_retries=3) -> str:
    """DashScope API 调用，带指数退避重试 (1s, 2s, 4s)"""

def validate_character_crop(image_path) -> bool:
    """验证单个字符图片，返回 True/False"""

def validate_character_crops(image_dir, output_dir=None, max_workers=4) -> list[dict]:
    """批量验证，返回 [{path, valid}, ...]"""
```

## 批量处理
- `concurrent.futures.ThreadPoolExecutor` 并发
- 默认 4 workers（DashScope 建议 2-5 并发）
- 按文件名排序输出结果

## 错误处理

| 错误 | 处理 |
|------|------|
| API key 未设置 | 启动时抛 RuntimeError |
| API 超时 | 指数退避重试 3 次 |
| HTTP 429 限流 | 退避重试，减少 workers |
| 模糊回复 | 默认 False（保守拒绝） |
| 图片读取失败 | 返回 False，打印警告 |

## 集成方式
```python
from research_utils.validation import validate_character_crops

results = validate_character_crops("output/char_crops", output_dir="output/valid_crops")
# results = [{"path": "char_0000.png", "valid": True}, ...]
```

## 测试计划
1. `_parse_yes_no` 单元测试（各种回复字符串）
2. 已知样本测试（10 有效 + 5 无效 + 5 模糊）
3. 批量处理测试（split_chars 输出的裁剪图）
4. 端到端 pipeline 测试（有/无验证的识别精度对比）

## 依赖
- `dashscope`（已在 pyproject.toml 中）
- 需要 `DASHSCOPE_API_KEY` 环境变量

## 文件
- 新建: `lib/research_utils/validation/__init__.py`
- 参考: `prompts/PROMPTS.md`（prompt 模板）
- 集成目标: `hun_recognize.py`, `split_chars_final.py`
