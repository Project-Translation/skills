---
name: web-artifacts-builder
description: 用于使用现代前端技术(React、Tailwind CSS、shadcn/ui)创建复杂的多组件 claude.ai HTML artifacts 的工具套件。用于需要状态管理、路由或 shadcn/ui 组件的复杂 artifacts - 不适用于简单的单文件 HTML/JSX artifacts。
license: 完整条款见 LICENSE.txt
---

# Web Artifacts Builder

要构建强大的前端 claude.ai artifacts，请按以下步骤操作：
1. 使用 `scripts/init-artifact.sh` 初始化前端仓库
2. 通过编辑生成的代码开发您的 artifact
3. 使用 `scripts/bundle-artifact.sh` 将所有代码打包成单个 HTML 文件
4. 向用户展示 artifact
5. (可选)测试 artifact

**技术栈**: React 18 + TypeScript + Vite + Parcel (打包) + Tailwind CSS + shadcn/ui

## 设计与风格指南

非常重要：为避免通常被称为"AI slop"的问题，避免使用过度居中的布局、紫色渐变、统一的圆角和 Inter 字体。

## 快速开始

### 第 1 步：初始化项目

运行初始化脚本创建新的 React 项目：
```bash
bash scripts/init-artifact.sh <项目名称>
cd <项目名称>
```

这将创建一个完全配置的项目，包含：
- ✅ React + TypeScript (通过 Vite)
- ✅ Tailwind CSS 3.4.1 与 shadcn/ui 主题系统
- ✅ 路径别名 (`@/`) 配置
- ✅ 预安装 40+ 个 shadcn/ui 组件
- ✅ 包含所有 Radix UI 依赖
- ✅ Parcel 配置用于打包 (通过 .parcelrc)
- ✅ Node 18+ 兼容性 (自动检测并固定 Vite 版本)

### 第 2 步：开发您的 Artifact

要构建 artifact，请编辑生成的文件。参见下面的**常见开发任务**以获取指导。

### 第 3 步：打包成单个 HTML 文件

将 React 应用打包成单个 HTML artifact：
```bash
bash scripts/bundle-artifact.sh
```

这将创建 `bundle.html` - 一个包含所有 JavaScript、CSS 和依赖的自包含 artifact。此文件可直接在 Claude 对话中作为 artifact 分享。

**要求**：您的项目必须在根目录有 `index.html`。

**脚本作用**：
- 安装打包依赖 (parcel、@parcel/config-default、parcel-resolver-tspaths、html-inline)
- 创建带有路径别名支持的 `.parcelrc` 配置
- 使用 Parcel 构建 (无源映射)
- 使用 html-inline 将所有资源内联到单个 HTML 中

### 第 4 步：与用户共享 Artifact

最后，将打包的 HTML 文件在对话中与用户共享，以便他们可以将其作为 artifact 查看。

### 第 5 步：测试/可视化 Artifact (可选)

注意：这是一个完全可选的步骤。仅在必要时或被要求时执行。要测试/可视化 artifact，请使用可用的工具(包括其他技能或内置工具如 Playwright 或 Puppeteer)。通常，避免在开始时测试 artifact，因为这会增加请求与完成的 artifact 可见之间的延迟。在展示 artifact 后，如果被要求或出现问题时再进行测试。

## 参考资料

- **shadcn/ui 组件**: https://ui.shadcn.com/docs/components