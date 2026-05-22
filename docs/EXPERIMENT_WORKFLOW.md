# 实验工作流规范

## 标准流程

```
实验脚本 → 生成结果文件 → 更新sandbox页面 → Git提交推送 → 验证
```

## 1. 实验脚本规范

### 脚本位置
- 临时脚本: `/tmp/xxx.py` (实验完成后可清理)
- 持久脚本: `/home/lulu444/labeling-ocr/xxx.py`

### 输出目录
```
docs/sandbox/task{N}/
├── {experiment_name}/          # 实验名称目录
│   ├── {image_stem}_original.png      # 原图
│   ├── {image_stem}_bboxes_overlay.png # 检测结果叠加图
│   ├── {image_stem}_results.json      # 检测结果数据
│   └── summary.json                   # 汇总数据
```

### 结果JSON格式
```json
{
  "image": "filename.png",
  "folder": "pic1",
  "image_size": {"width": 68, "height": 273},
  "total_chars": 4,
  "elapsed_seconds": 1.763,
  "avg_confidence": 0.9524,
  "boxes": [
    {
      "id": 0,
      "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],
      "text": "字",
      "confidence": 0.99,
      "crop_path": "char_0000.png"
    }
  ]
}
```

## 2. Sandbox页面更新

### 文件位置
`docs/index.html`

### 更新步骤

#### 添加新实验结果
1. 在对应Task的section中添加结果表格/对比图
2. 图片路径使用相对路径: `sandbox/task{N}/{experiment}/{filename}`

#### 添加图片浏览器
在`const imageViewer = new ImageViewer(...)`数组中添加条目:
```javascript
{
  name: 'pic1/box_0002 (4字符)',           # 显示名称
  original: 'sandbox/task{N}/xxx/box_0002_original.png',  # 原图路径
  overlay: 'sandbox/task{N}/xxx/box_0002_bboxes_overlay.png',  # 结果图路径
  source: 'pic1/box_0002.png',             # 来源
  charCount: '4',                          # 检测字符数
  confidence: '95.24%',                    # 平均置信度
  text: '识别文字',                         # 识别结果
  accuracy: 0.8                            # 准确率(可选)
}
```

## 3. Git提交推送

### 标准命令
```bash
cd /tmp/labeling-ocr-packaged

# 1. 添加文件
git add docs/sandbox/task{N}/xxx/
git add docs/index.html

# 2. 提交 (描述清楚实验内容)
git commit -m "$(cat <<'EOF'
简短描述

详细说明实验内容、结果、发现。
EOF
)"

# 3. 推送 (需要取消代理)
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && git push origin main
```

### Commit Message规范
- 格式: `<动词> <内容>`
- 动词: Add, Update, Fix, Remove, Refactor
- 示例:
  - `Add RapidOCR det-only experiment results`
  - `Update image viewer to show all 10 samples`
  - `Fix missing overlay images for pic2`

## 4. Task分类

| Task | 目录 | 内容 |
|------|------|------|
| Task 1 | `task1/` | 字符级检测实验 (RapidOCR, CRAFT等) |
| Task 2 | `task2/` | 色彩分析字符切分 |
| Task 3 | `task3/` | VLM字符完整性验证 |
| Task 4 | `task4/` | React前端 |

## 5. 注意事项

### 图片文件
- 必须同时生成 `xxx_original.png` 和 `xxx_bboxes_overlay.png`
- 未检测到文字的图片也要生成这两个文件 (直接用原图)

### 路径
- sandbox中使用相对路径 (相对于docs/)
- 不要用绝对路径

### 验证
- 推送后等待1-2分钟让GitHub Pages部署
- 刷新页面验证 (Ctrl+Shift+R)
- 检查浏览器Console是否有错误

### 常见问题
1. **页面没更新**: 可能是浏览器缓存，强制刷新
2. **图片不显示**: 检查路径是否正确，文件是否已推送
3. **git push失败**: 取消代理 `unset http_proxy https_proxy`
