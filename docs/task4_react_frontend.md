# Task 4: React 前端 MVP

## 目标
构建古籍 OCR 标注平台的 Web 前端，支持自动化标注监控、手动标注审校、多格式导出。

## 技术栈
- React 18 + Vite + TypeScript
- Tailwind CSS v4（`@tailwindcss/vite` 插件）
- Zustand（状态管理，避免 Context 全量重渲染）
- react-router-dom（HashRouter，GitHub Pages 兼容）
- MSW（Mock Service Worker，API mock）
- axios（HTTP 客户端）

## 主题设计
深色主题：
- 基底: `#1a1a1a`
- 面板: `#242424`
- 边框: `#333`
- 文字: `gray-100` / `gray-300` / `gray-500`

## 页面结构

### 1. UploadPage（上传）
- 图片拖拽区域 + 文件选择按钮
- 拖拽/选择后自动跳转到 DetectPage
- `useProjectStore.setImage(file)` 存储图片

### 2. DetectPage（自动化标注监控）
- 顶部：原图预览
- 主体：Pipeline 流程步骤列表
  - 文字区域检测 (PaddleOCR)
  - 字符切分 (色彩分析/投影法)
  - 字符验证 (VLM)
  - 字符识别 (HUNet)
- 每步显示：序号/完成/进行中/待执行 状态
- 进行中显示 spinner
- 每步有参数配置入口（MVP 先做 UI 骨架）

### 3. AnnotatePage（手动标注与审校）— 核心页面
- **左面板**: 原图 + SVG 叠加层
  - SVG viewBox 匹配图片自然尺寸
  - 每个 bbox 渲染为 `<rect>`，支持 hover 高亮、点击选中
  - 拖拽框选新区域 → 调用 VLM 识别
- **右面板**: 标注详情
  - bbox 列表（可点击选择）
  - 选中 bbox 的编辑器：识别结果输入、ground truth
  - 预设古体字/异体字字体列表（楷体、宋体、隶书、篆书、行书、草书、颜真卿、柳公权、欧阳询、赵孟頫）
  - 拖选区域 → VLM 识别按钮

### 4. ExportPage（导出）
- 三种格式按钮：XML / JSON / HTML
- XML: PASCAL VOC 格式（4 点多边形）
- JSON: `{dt_polys_rec: [{points, rec}, ...]}`
- HTML: 自包含，base64 图片 + SVG 叠加

## 状态管理（4 个 Zustand Store）

### useProjectStore
```ts
imageUrl: string | null
imageName: string | null
naturalWidth: number
naturalHeight: number
currentStep: PipelineStep
pipelineRunning: boolean
```

### useDetectionStore
```ts
polygons: DetectionPolygon[]
// DetectionPolygon = {id, points: Point[], confidence, label?}
```

### useAnnotationStore
```ts
bboxes: CharBbox[]
selectedId: string | null
// CharBbox = {id, x, y, width, height, label, groundTruth?, valid?}
```

### useUIStore
```ts
sidebarOpen: boolean
hoveredId: string | null
```

## 核心组件: ImageOverlay
```tsx
<div className="relative inline-block">
  <img src={imageUrl} className="block max-w-full h-auto" />
  <svg className="absolute inset-0 w-full h-full"
       viewBox={`0 0 ${naturalW} ${naturalH}`}>
    {bboxes.map(bbox => <rect ... />)}
  </svg>
</div>
```
SVG viewBox 直接映射图片像素坐标，无需手动计算缩放。

## 路由
```tsx
<HashRouter>
  <Route element={<AppShell />}>
    <Route path="/" element={<UploadPage />} />
    <Route path="/detect" element={<DetectPage />} />
    <Route path="/annotate" element={<AnnotatePage />} />
    <Route path="/export" element={<ExportPage />} />
  </Route>
</HashRouter>
```
HashRouter 避免 GitHub Pages 的 SPA 404 问题。

## Mock 数据
MSW 拦截 API 请求，返回模拟数据：
- 检测: 16 个多边形 + 置信度 (0.62-0.93)
- 字符: 70 个 bbox
- VLM 标注: 16 个带 rec 字段

## 项目结构
```
web/
├── src/
│   ├── api/           # axios 实例 + MSW mocks
│   ├── store/         # 4 个 Zustand store
│   ├── types/         # TypeScript 类型定义
│   ├── components/
│   │   ├── layout/    # AppShell, Navbar
│   │   ├── upload/    # ImageDropzone
│   │   ├── canvas/    # ImageOverlay (SVG)
│   │   ├── sidebar/   # BboxList, BboxEditor
│   │   └── export/    # ExportPanel
│   ├── pages/         # 4 个页面组件
│   └── utils/         # xml.ts, html.ts, download.ts
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## 实施阶段

| Phase | 内容 | 产出 |
|-------|------|------|
| 1 | Vite 脚手架 + 依赖 + 类型 + stores + 路由骨架 | 可运行的空壳 app |
| 2 | ImageDropzone + UploadPage | 图片上传功能 |
| 3 | ImageOverlay + MSW Mock + DetectPage | 检测可视化 |
| 4 | BboxList + BboxEditor + AnnotatePage | 标注编辑器 |
| 5 | XML/JSON/HTML 生成 + ExportPage | 导出功能 |
| 6 | 国际化 + 错误处理 + GitHub Pages 部署 | 完善 |

## 部署
- 前端: `npm run build` → GitHub Pages（静态文件）
- 后端: 独立部署（FastAPI）
- `base: '/labeling-ocr/'` 配置 Vite 的 publicPath
