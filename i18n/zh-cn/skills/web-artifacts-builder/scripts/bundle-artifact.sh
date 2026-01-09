#!/bin/bash
set -e

echo "📦 正在打包 React 应用为单个 HTML 文件..."

# 检查是否在项目目录中
if [ ! -f "package.json" ]; then
  echo "❌ 错误：未找到 package.json。请在项目根目录运行此脚本。"
  exit 1
fi

# 检查 index.html 是否存在
if [ ! -f "index.html" ]; then
  echo "❌ 错误：项目根目录未找到 index.html。"
  echo "   此脚本需要 index.html 作为入口点。"
  exit 1
fi

# 安装打包依赖
echo "📦 安装打包依赖..."
pnpm add -D parcel @parcel/config-default parcel-resolver-tspaths html-inline

# 创建支持路径别名的 Parcel 配置
if [ ! -f ".parcelrc" ]; then
  echo "🔧 创建支持路径别名的 Parcel 配置..."
  cat > .parcelrc << 'EOF'
{
  "extends": "@parcel/config-default",
  "resolvers": ["parcel-resolver-tspaths", "..."]
}
EOF
fi

# 清理之前的构建
echo "🧹 清理之前的构建..."
rm -rf dist bundle.html

# 使用 Parcel 构建
echo "🔨 使用 Parcel 构建..."
pnpm exec parcel build index.html --dist-dir dist --no-source-maps

# 将所有资源内联到单个 HTML 中
echo "🎯 将所有资源内联到单个 HTML 文件..."
pnpm exec html-inline dist/index.html > bundle.html

# 获取文件大小
FILE_SIZE=$(du -h bundle.html | cut -f1)

echo ""
echo "✅ 打包完成！"
echo "📄 输出：bundle.html ($FILE_SIZE)"
echo ""
echo "现在可以将此单个 HTML 文件用作 Claude 对话中的产物。"
echo "本地测试：在浏览器中打开 bundle.html"