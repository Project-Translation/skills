# HTML 转 PowerPoint 指南

使用 `html2pptx.js` 库将 HTML 幻灯片转换为 PowerPoint 演示文稿，实现精确定位。

## 目录

1. [创建 HTML 幻灯片](#创建-html-幻灯片)
2. [使用 html2pptx 库](#使用-html2pptx-库)
3. [使用 PptxGenJS](#使用-pptxgenjs)

---

## 创建 HTML 幻灯片

每个 HTML 幻灯片必须包含正确的主体尺寸：

### 布局尺寸

- **16:9**（默认）：`width: 720pt; height: 405pt`
- **4:3**：`width: 720pt; height: 540pt`
- **16:10**：`width: 720pt; height: 450pt`

### 支持的元素

- `<p>`, `<h1>`-`<h6>` - 带样式的文本
- `<ul>`, `<ol>` - 列表（切勿使用手动项目符号 •, -, *）
- `<b>`, `<strong>` - 粗体文本（内联格式）
- `<i>`, `<em>` - 斜体文本（内联格式）
- `<u>` - 下划线文本（内联格式）
- `<span>` - 带 CSS 样式的内联格式（粗体、斜体、下划线、颜色）
- `<br>` - 换行
- `<div>` 带背景/边框 - 转换为形状
- `<img>` - 图片
- `class="placeholder"` - 图表的预留空间（返回 `{ id, x, y, w, h }`）

### 关键文本规则

**所有文本必须位于 `<p>`、`<h1>`-`<h6>`、`<ul>` 或 `<ol>` 标签内：**
- ✅ 正确：`<div><p>此处文本</p></div>`
- ❌ 错误：`<div>此处文本</div>` - **文本不会在 PowerPoint 中显示**
- ❌ 错误：`<span>文本</span>` - **文本不会在 PowerPoint 中显示**
- `<div>` 或 `<span>` 中没有文本标签的文本将被静默忽略

**切勿使用手动项目符号符号（•, -, * 等）** - 使用 `<ul>` 或 `<ol>` 列表代替

**仅使用普遍可用的 Web 安全字体：**
- ✅ Web 安全字体：`Arial`、`Helvetica`、`Times New Roman`、`Georgia`、`Courier New`、`Verdana`、`Tahoma`、`Trebuchet MS`、`Impact`、`Comic Sans MS`
- ❌ 错误：`'Segoe UI'`、`'SF Pro'`、`'Roboto'`、自定义字体 - **可能导致渲染问题**

### 样式设置

- 在 body 上使用 `display: flex` 以防止边距折叠破坏溢出验证
- 使用 `margin` 进行间距（padding 包含在大小中）
- 内联格式：使用 `<b>`、`<i>`、`<u>` 标签或带 CSS 样式的 `<span>`
  - `<span>` 支持：`font-weight: bold`、`font-style: italic`、`text-decoration: underline`、`color: #rrggbb`
  - `<span>` 不支持：`margin`、`padding`（PowerPoint 文本运行中不支持）
  - 示例：`<span style="font-weight: bold; color: #667eea;">粗体蓝色文本</span>`
- Flexbox 有效 - 位置根据渲染布局计算
- CSS 中使用带 `#` 前缀的十六进制颜色
- **文本对齐**：需要时使用 CSS `text-align`（`center`、`right` 等）作为 PptxGenJS 的文本格式提示（如果文本长度略有差异）

### 形状样式（仅 DIV 元素）

**重要：背景、边框和阴影仅在 `<div>` 元素上有效，不在文本元素（`<p>`、`<h1>`-`<h6>`、`<ul>`、`<ol>`）上有效**

- **背景**：CSS `background` 或 `<div>` 元素上的 `background-color`（仅限 `<div>` 元素）
  - 示例：`<div style="background: #f0f0f0;">` - 创建带背景的形状
- **边框**：CSS `border` 在 `<div>` 元素上转换为 PowerPoint 形状边框
  - 支持统一边框：`border: 2px solid #333333`
  - 支持部分边框：`border-left`、`border-right`、`border-top`、`border-bottom`（渲染为线条形状）
  - 示例：`<div style="border-left: 8pt solid #E76F51;">`
- **边框半径**：CSS `border-radius` 在 `<div>` 元素上用于圆角
  - `border-radius: 50%` 或更高创建圆形形状
  - 小于 50% 的百分比根据形状的较小尺寸计算
  - 支持 px 和 pt 单位（例如，`border-radius: 8pt;`、`border-radius: 12px;`）
  - 示例：100x200px 框上的 `<div style="border-radius: 25%;">` = 100px 的 25% = 25px 半径
- **盒阴影**：CSS `box-shadow` 在 `<div>` 元素上转换为 PowerPoint 阴影
  - 仅支持外部阴影（内部阴影被忽略以防止损坏）
  - 示例：`<div style="box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);">`
  - 注意：PowerPoint 不支持内部/内部阴影，将被跳过

### 图标和渐变

- **重要：切勿使用 CSS 渐变（`linear-gradient`、`radial-gradient`）** - 它们无法转换为 PowerPoint
- **始终首先使用 Sharp 创建渐变/图标 PNG，然后在 HTML 中引用**
- 对于渐变：将 SVG 光栅化为 PNG 背景图像
- 对于图标：将 react-icons SVG 光栅化为 PNG 图像
- 所有视觉效果必须在 HTML 渲染前预渲染为光栅图像

**使用 Sharp 光栅化图标：**

```javascript
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const { FaHome } = require('react-icons/fa');

async function rasterizeIconPng(IconComponent, color, size = "256", filename) {
  const svgString = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color: `#${color}`, size: size })
  );

  // 使用 Sharp 将 SVG 转换为 PNG
  await sharp(Buffer.from(svgString))
    .png()
    .toFile(filename);

  return filename;
}

// 用法：在 HTML 中使用前先光栅化图标
const iconPath = await rasterizeIconPng(FaHome, "4472c4", "256", "home-icon.png");
// 然后在 HTML 中引用：<img src="home-icon.png" style="width: 40pt; height: 40pt;">
```

**使用 Sharp 光栅化渐变：**

```javascript
const sharp = require('sharp');

async function createGradientBackground(filename) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="562.5">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#COLOR1"/>
        <stop offset="100%" style="stop-color:#COLOR2"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
  </svg>`;

  await sharp(Buffer.from(svg))
    .png()
    .toFile(filename);

  return filename;
}

// 用法：在 HTML 前创建渐变背景
const bgPath = await createGradientBackground("gradient-bg.png");
// 然后在 HTML 中：<body style="background-image: url('gradient-bg.png');">
```

### 示例

```html
<!DOCTYPE html>
<html>
<head>
<style>
html { background: #ffffff; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #f5f5f5; font-family: Arial, sans-serif;
  display: flex;
}
.content { margin: 30pt; padding: 40pt; background: #ffffff; border-radius: 8pt; }
h1 { color: #2d3748; font-size: 32pt; }
.box {
  background: #70ad47; padding: 20pt; border: 3px solid #5a8f37;
  border-radius: 12pt; box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.25);
}
</style>
</head>
<body>
<div class="content">
  <h1>食谱标题</h1>
  <ul>
    <li><b>项目：</b> 描述</li>
  </ul>
  <p>文本带有 <b>粗体</b>、<i>斜体</i>、<u>下划线</u>。</p>
  <div id="chart" class="placeholder" style="width: 350pt; height: 200pt;"></div>

  <!-- 文本必须在 <p> 标签中 -->
  <div class="box">
    <p>5</p>
  </div>
</div>
</body>
</html>
```

## 使用 html2pptx 库

### 依赖项

这些库已全局安装并可使用：
- `pptxgenjs`
- `playwright`
- `sharp`

### 基本用法

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_16x9';  // 必须与 HTML body 尺寸匹配

const { slide, placeholders } = await html2pptx('slide1.html', pptx);

// 向占位符区域添加图表
if (placeholders.length > 0) {
    slide.addChart(pptx.charts.LINE, chartData, placeholders[0]);
}

await pptx.writeFile('output.pptx');
```

### API 参考

#### 函数签名
```javascript
await html2pptx(htmlFile, pres, options)
```

#### 参数
- `htmlFile`（字符串）：HTML 文件路径（绝对或相对）
- `pres`（pptxgen）：已设置布局的 PptxGenJS 演示文稿实例
- `options`（对象，可选）：
  - `tmpDir`（字符串）：生成文件的临时目录（默认：`process.env.TMPDIR || '/tmp'`）
  - `slide`（对象）：要重用的现有幻灯片（默认：创建新幻灯片）

#### 返回值
```javascript
{
    slide: pptxgenSlide,           // 创建/更新的幻灯片
    placeholders: [                 // 占位符位置数组
        { id: string, x: number, y: number, w: number, h: number },
        ...
    ]
}
```

### 验证

库会自动验证并在抛出前收集所有错误：

1. **HTML 尺寸必须与演示文稿布局匹配** - 报告尺寸不匹配
2. **内容不能溢出 body** - 报告溢出及确切测量值
3. **CSS 渐变** - 报告不支持的渐变使用
4. **文本元素样式** - 报告文本元素上的背景/边框/阴影（仅在 div 上允许）

**所有验证错误都会被收集并在单个错误消息中报告**，允许您一次性修复所有问题，而不是逐一修复。

### 使用占位符

```javascript
const { slide, placeholders } = await html2pptx('slide.html', pptx);

// 使用第一个占位符
slide.addChart(pptx.charts.BAR, data, placeholders[0]);

// 按 ID 查找
const chartArea = placeholders.find(p => p.id === 'chart-area');
slide.addChart(pptx.charts.LINE, data, chartArea);
```

### 完整示例

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = '您的姓名';
    pptx.title = '我的演示文稿';

    // 幻灯片 1：标题
    const { slide: slide1 } = await html2pptx('slides/title.html', pptx);

    // 幻灯片 2：带图表的内容
    const { slide: slide2, placeholders } = await html2pptx('slides/data.html', pptx);

    const chartData = [{
        name: '销售',
        labels: ['Q1', 'Q2', 'Q3', 'Q4'],
        values: [4500, 5500, 6200, 7100]
    }];

    slide2.addChart(pptx.charts.BAR, chartData, {
        ...placeholders[0],
        showTitle: true,
        title: '季度销售',
        showCatAxisTitle: true,
        catAxisTitle: '季度',
        showValAxisTitle: true,
        valAxisTitle: '销售（千美元）'
    });

    // 保存
    await pptx.writeFile({ fileName: 'presentation.pptx' });
    console.log('演示文稿创建成功！');
}

createPresentation().catch(console.error);
```

## 使用 PptxGenJS

使用 `html2pptx` 将 HTML 转换为幻灯片后，您将使用 PptxGenJS 添加图表、图片和附加元素等动态内容。

### ⚠️ 关键规则

#### 颜色
- **切勿在 PptxGenJS 中使用 `#` 前缀的十六进制颜色** - 会导致文件损坏
- ✅ 正确：`color: "FF0000"`、`fill: { color: "0066CC" }`
- ❌ 错误：`color: "#FF0000"`（破坏文档）

### 添加图片

始终根据实际图片尺寸计算宽高比：

```javascript
// 获取图片尺寸：identify image.png | grep -o '[0-9]* x [0-9]*'
const imgWidth = 1860, imgHeight = 1519;  // 来自实际文件
const aspectRatio = imgWidth / imgHeight;

const h = 3;  // 最大高度
const w = h * aspectRatio;
const x = (10 - w) / 2;  // 在 16:9 幻灯片上居中

slide.addImage({ path: "chart.png", x, y: 1.5, w, h });
```

### 添加文本

```javascript
// 带格式的富文本
slide.addText([
    { text: "粗体 ", options: { bold: true } },
    { text: "斜体 ", options: { italic: true } },
    { text: "普通" }
], {
    x: 1, y: 2, w: 8, h: 1
});
```

### 添加形状

```javascript
// 矩形
slide.addShape(pptx.shapes.RECTANGLE, {
    x: 1, y: 1, w: 3, h: 2,
    fill: { color: "4472C4" },
    line: { color: "000000", width: 2 }
});

// 圆形
slide.addShape(pptx.shapes.OVAL, {
    x: 5, y: 1, w: 2, h: 2,
    fill: { color: "ED7D31" }
});

// 圆角矩形
slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, {
    x: 1, y: 4, w: 3, h: 1.5,
    fill: { color: "70AD47" },
    rectRadius: 0.2
});
```

### 添加图表

**大多数图表需要：** 使用 `catAxisTitle`（分类）和 `valAxisTitle`（值）的轴标签。

**图表数据格式：**
- 对简单条形图/线形图使用**单系列与所有标签**
- 每个系列创建一个单独的图例条目
- 标签数组定义 X 轴值

**时间序列数据 - 选择正确的粒度：**
- **< 30 天**：使用每日分组（例如，“10-01”、“10-02”）- 避免月度聚合创建单点图表
- **30-365 天**：使用月度分组（例如，“2024-01”、“2024-02”）
- **> 365 天**：使用年度分组（例如，“2023”、“2024”）
- **验证**：只有 1 个数据点的图表可能表示时间周期的聚合不正确

```javascript
const { slide, placeholders } = await html2pptx('slide.html', pptx);

// 正确：单系列与所有标签
slide.addChart(pptx.charts.BAR, [{
    name: "2024 年销售",
    labels: ["Q1", "Q2", "Q3", "Q4"],
    values: [4500, 5500, 6200, 7100]
}], {
    ...placeholders[0],  // 使用占位符位置
    barDir: 'col',       // 'col' = 垂直条形，'bar' = 水平条形
    showTitle: true,
    title: '季度销售',
    showLegend: false,   // 单系列不需要图例
    // 需要的轴标签
    showCatAxisTitle: true,
    catAxisTitle: '季度',
    showValAxisTitle: true,
    valAxisTitle: '销售（千美元）',
    // 可选：控制缩放（根据数据范围调整最小值以获得更好的可视化效果）
    valAxisMaxVal: 8000,
    valAxisMinVal: 0,  // 计数/金额使用 0；对于聚类数据（例如 4500-7100），考虑从接近最小值开始
    valAxisMajorUnit: 2000,  // 控制 y 轴标签间距以防止拥挤
    catAxisLabelRotate: 45,  // 如果标签拥挤则旋转
    dataLabelPosition: 'outEnd',
    dataLabelColor: '000000',
    // 单系列图表使用单色
    chartColors: ["4472C4"]  // 所有条形同色
});
```

#### 散点图

**重要**：散点图数据格式不寻常 - 第一系列包含 X 轴值，后续系列包含 Y 值：

```javascript
// 准备数据
const data1 = [{ x: 10, y: 20 }, { x: 15, y: 25 }, { x: 20, y: 30 }];
const data2 = [{ x: 12, y: 18 }, { x: 18, y: 22 }];

const allXValues = [...data1.map(d => d.x), ...data2.map(d => d.x)];

slide.addChart(pptx.charts.SCATTER, [
    { name: 'X 轴', values: allXValues },  // 第一系列 = X 值
    { name: '系列 1', values: data1.map(d => d.y) },  // 仅 Y 值
    { name: '系列 2', values: data2.map(d => d.y) }   // 仅 Y 值
], {
    x: 1, y: 1, w: 8, h: 4,
    lineSize: 0,  // 0 = 无线条连接
    lineDataSymbol: 'circle',
    lineDataSymbolSize: 6,
    showCatAxisTitle: true,
    catAxisTitle: 'X 轴',
    showValAxisTitle: true,
    valAxisTitle: 'Y 轴',
    chartColors: ["4472C4", "ED7D31"]
});
```

#### 线形图

```javascript
slide.addChart(pptx.charts.LINE, [{
    name: "温度",
    labels: ["1 月", "2 月", "3 月", "4 月"],
    values: [32, 35, 42, 55]
}], {
    x: 1, y: 1, w: 8, h: 4,
    lineSize: 4,
    lineSmooth: true,
    // 需要的轴标签
    showCatAxisTitle: true,
    catAxisTitle: '月份',
    showValAxisTitle: true,
    valAxisTitle: '温度（°F）',
    // 可选：Y 轴范围（根据数据范围设置最小值以获得更好的可视化效果）
    valAxisMinVal: 0,     // 从 0 开始的范围（计数、百分比等）
    valAxisMaxVal: 60,
    valAxisMajorUnit: 20,  // 控制 y 轴标签间距以防止拥挤（例如，10、20、25）
    // valAxisMinVal: 30,  // 首选：对于聚类数据范围（例如 32-55 或 3-5 分评级），从接近最小值开始轴以显示变化
    // 可选：图表颜色
    chartColors: ["4472C4", "ED7D31", "A5A5A5"]
});
```

#### 饼图（不需要轴标签）

**重要**：饼图需要**单个数据系列**，所有类别在 `labels` 数组中，对应值在 `values` 数组中。

```javascript
slide.addChart(pptx.charts.PIE, [{
    name: "市场份额",
    labels: ["产品 A", "产品 B", "其他"],  // 所有类别在一个数组中
    values: [35, 45, 20]  // 所有值在一个数组中
}], {
    x: 2, y: 1, w: 6, h: 4,
    showPercent: true,
    showLegend: true,
    legendPos: 'r',  // 右侧
    chartColors: ["4472C4", "ED7D31", "A5A5A5"]
});
```

#### 多个数据系列

```javascript
slide.addChart(pptx.charts.LINE, [
    {
        name: "产品 A",
        labels: ["Q1", "Q2", "Q3", "Q4"],
        values: [10, 20, 30, 40]
    },
    {
        name: "产品 B",
        labels: ["Q1", "Q2", "Q3", "Q4"],
        values: [15, 25, 20, 35]
    }
], {
    x: 1, y: 1, w: 8, h: 4,
    showCatAxisTitle: true,
    catAxisTitle: '季度',
    showValAxisTitle: true,
    valAxisTitle: '收入（百万美元）'
});
```

### 图表颜色

**重要**：使用**不带** `#` 前缀的十六进制颜色 - 包含 `#` 会导致文件损坏。

**将图表颜色与您选择的设计调色板对齐**，确保数据可视化的对比度足够且区分度高。调整颜色以：
- 相邻系列之间的强对比度
- 对幻灯片背景的可读性
- 无障碍性（避免仅红绿组合）

```javascript
// 示例：受海洋调色板启发的图表颜色（调整对比度）
const chartColors = ["16A085", "FF6B9D", "2C3E50", "F39C12", "9B59B6"];

// 单系列图表：所有条形/点使用一种颜色
slide.addChart(pptx.charts.BAR, [{
    name: "销售",
    labels: ["Q1", "Q2", "Q3", "Q4"],
    values: [4500, 5500, 6200, 7100]
}], {
    ...placeholders[0],
    chartColors: ["16A085"],  // 所有条形同色
    showLegend: false
});

// 多系列图表：每个系列使用不同颜色
slide.addChart(pptx.charts.LINE, [
    { name: "产品 A", labels: ["Q1", "Q2", "Q3"], values: [10, 20, 30] },
    { name: "产品 B", labels: ["Q1", "Q2", "Q3"], values: [15, 25, 20] }
], {
    ...placeholders[0],
    chartColors: ["16A085", "FF6B9D"]  // 每个系列一种颜色
});
```

### 添加表格

表格可以使用基本或高级格式添加：

#### 基本表格

```javascript
slide.addTable([
    ["标题 1", "标题 2", "标题 3"],
    ["行 1，列 1", "行 1，列 2", "行 1，列 3"],
    ["行 2，列 1", "行 2，列 2", "行 2，列 3"]
], {
    x: 0.5,
    y: 1,
    w: 9,
    h: 3,
    border: { pt: 1, color: "999999" },
    fill: { color: "F1F1F1" }
});
```

#### 带自定义格式的表格

```javascript
const tableData = [
    // 带自定义样式的标题行
    [
        { text: "产品", options: { fill: { color: "4472C4" }, color: "FFFFFF", bold: true } },
        { text: "收入", options: { fill: { color: "4472C4" }, color: "FFFFFF", bold: true } },
        { text: "增长", options: { fill: { color: "4472C4" }, color: "FFFFFF", bold: true } }
    ],
    // 数据行
    ["产品 A", "$50M", "+15%"],
    ["产品 B", "$35M", "+22%"],
    ["产品 C", "$28M", "+8%"]
];

slide.addTable(tableData, {
    x: 1,
    y: 1.5,
    w: 8,
    h: 3,
    colW: [3, 2.5, 2.5],  // 列宽
    rowH: [0.5, 0.6, 0.6, 0.6],  // 行高
    border: { pt: 1, color: "CCCCCC" },
    fill: { color: "F1F1F1" },
    align: "center",
    valign: "middle",
    fontSize: 14
});
```

#### 带合并单元格的表格

```javascript
const mergedTableData = [
    [
        { text: "Q1 结果", options: { colspan: 3, fill: { color: "4472C4" }, color: "FFFFFF", bold: true } }
    ],
    ["产品", "销售", "市场份额"],
    ["产品 A", "$25M", "35%"],
    ["产品 B", "$18M", "25%"]
];

slide.addTable(mergedTableData, {
    x: 1,
    y: 1,
    w: 8,
    h: 2.5,
    colW: [3, 2.5, 2.5],
    border: { pt: 1, color: "DDDDDD" }
});
```

### 表格选项

常见表格选项：
- `x, y, w, h` - 位置和大小
- `colW` - 列宽数组（英寸）
- `rowH` - 行高数组（英寸）
- `border` - 边框样式：`{ pt: 1, color: "999999" }`
- `fill` - 背景颜色（无 # 前缀）
- `align` - 文本对齐：`"left"`、`"center"`、`"right"`
- `valign` - 垂直对齐：`"top"`、`"middle"`、`"bottom"`
- `fontSize` - 文本大小
- `autoPage` - 如果内容溢出自动创建新幻灯片