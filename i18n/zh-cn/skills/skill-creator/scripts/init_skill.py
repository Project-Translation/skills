#!/usr/bin/env python3
"""
技能初始化器 - 从模板创建新技能

用法：
    init_skill.py <技能名称> --path <路径>

示例：
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-api-helper --path skills/private
    init_skill.py custom-skill --path /custom/location
"""

import sys
from pathlib import Path


SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: 完整且信息丰富的技能功能说明。包括何时使用此技能 - 特定场景、文件类型或任务。]
---

# {skill_title}

## 概述

[TODO: 1-2 句话解释此技能实现的功能]

## 技能结构

[TODO: 选择最适合此技能目的的结构。常见模式：

**1. 工作流式** (适用于顺序流程)
- 适用于有明确步骤程序的场景
- 示例：DOCX 技能的 "工作流决策树" → "读取" → "创建" → "编辑"
- 结构：## 概述 → ## 工作流决策树 → ## 步骤1 → ## 步骤2...

**2. 任务式** (适用于工具集合)
- 适用于技能提供不同操作/能力的场景
- 示例：PDF 技能的 "快速开始" → "合并PDF" → "拆分PDF" → "提取文本"
- 结构：## 概述 → ## 快速开始 → ## 任务类别1 → ## 任务类别2...

**3. 参考/指南式** (适用于标准或规范)
- 适用于品牌指南、编码标准或需求规范
- 示例：品牌样式技能的 "品牌指南" → "颜色" → "字体" → "功能"
- 结构：## 概述 → ## 指南 → ## 规范 → ## 使用...

**4. 能力式** (适用于集成系统)
- 适用于技能提供多个相互关联功能的场景
- 示例：产品管理技能的 "核心能力" → 编号能力列表
- 结构：## 概述 → ## 核心能力 → ### 1. 功能 → ### 2. 功能...

模式可以根据需要混合使用。大多数技能结合多种模式(例如，以任务式开始，为复杂操作添加工作流)。

完成后删除整个 "技能结构" 部分 - 这只是指导信息。]

## [TODO: 基于所选结构替换为第一个主要部分]

[TODO: 在此处添加内容。参考现有技能的示例：
- 技术技能的代码示例
- 复杂工作流的决策树
- 带有真实用户请求的具体示例
- 如需要，引用脚本/模板/参考资料]

## 资源

此技能包含示例资源目录，展示如何组织不同类型的捆绑资源：

### scripts/
可直接执行的代码(Python/Bash等)，用于执行特定操作。

**其他技能的示例：**
- PDF 技能：`fill_fillable_fields.py`, `extract_form_field_info.py` - PDF 操作工具
- DOCX 技能：`document.py`, `utilities.py` - 文档处理 Python 模块

**适用场景：** Python 脚本、shell 脚本或任何执行自动化、数据处理或特定操作的可执行代码。

**注意：** 脚本可能在不加载到上下文的情况下执行，但仍可被 Claude 读取用于补丁或环境调整。

### references/
文档和参考资料，旨在加载到上下文以指导 Claude 的处理和思考。

**其他技能的示例：**
- 产品管理：`communication.md`, `context_building.md` - 详细的工作流程指南
- BigQuery：API 参考文档和查询示例
- 财务：架构文档、公司政策

**适用场景：** 深度文档、API 参考、数据库架构、综合指南或任何 Claude 在工作时应参考的详细信息。

### assets/
不打算加载到上下文的文件，而是用于 Claude 产生的输出中。

**其他技能的示例：**
- 品牌样式：PowerPoint 模板文件(.pptx)、logo 文件
- 前端构建器：HTML/React 样板项目目录
- 排版：字体文件(.ttf, .woff2)

**适用场景：** 模板、样板代码、文档模板、图片、图标、字体或任何打算复制或用于最终输出的文件。

---

**不需要的目录可以删除。** 并非每个技能都需要所有三种资源类型。
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
{skill_name} 的示例辅助脚本

这是一个可直接执行的占位符脚本。
替换为实际实现或删除(如不需要)。

其他技能的真实脚本示例：
- pdf/scripts/fill_fillable_fields.py - 填充 PDF 表单字段
- pdf/scripts/convert_pdf_to_images.py - 将 PDF 页面转换为图片
"""

def main():
    print("这是 {skill_name} 的示例脚本")
    # TODO: 在此处添加实际脚本逻辑
    # 可以是数据处理、文件转换、API 调用等

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# {skill_title} 的参考文档

这是详细参考文档的占位符。
替换为实际参考内容或删除(如不需要)。

其他技能的真实参考文档示例：
- product-management/references/communication.md - 状态更新综合指南
- product-management/references/context_building.md - 收集上下文的深度指南
- bigquery/references/ - API 参考和查询示例

## 参考文档的适用场景

参考文档适用于：
- 全面的 API 文档
- 详细的工作流程指南
- 复杂的多步骤流程
- 对主 SKILL.md 来说过于冗长的信息
- 仅在特定用例中需要的内容

## 结构建议

### API 参考示例
- 概述
- 认证
- 带示例的端点
- 错误代码
- 速率限制

### 工作流程指南示例
- 前置条件
- 逐步说明
- 常见模式
- 故障排除
- 最佳实践
"""

EXAMPLE_ASSET = """# 示例资源文件

此占位符表示资源文件的存储位置。
替换为实际资源文件(模板、图片、字体等)或删除(如不需要)。

资源文件不打算加载到上下文，而是用于 Claude 产生的输出中。

其他技能的真实资源文件示例：
- 品牌指南：logo.png, slides_template.pptx
- 前端构建器：hello-world/ 目录，包含 HTML/React 样板
- 排版：custom-font.ttf, font-family.woff2
- 数据：sample_data.csv, test_dataset.json

## 常见资源类型

- 模板：.pptx, .docx, 样板目录
- 图片：.png, .jpg, .svg, .gif
- 字体：.ttf, .otf, .woff, .woff2
- 样板代码：项目目录、起始文件
- 图标：.ico, .svg
- 数据文件：.csv, .json, .xml, .yaml

注意：这是文本占位符。实际资源可以是任何文件类型。
"""


def title_case_skill_name(skill_name):
    """将连字符技能名称转换为标题大小写用于显示。"""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path):
    """
    使用模板 SKILL.md 初始化新技能目录。

    Args:
        skill_name: 技能名称
        path: 应创建技能目录的路径

    Returns:
        创建的技能目录路径，或错误时返回 None
    """
    # 确定技能目录路径
    skill_dir = Path(path).resolve() / skill_name

    # 检查目录是否已存在
    if skill_dir.exists():
        print(f"❌ 错误：技能目录已存在：{skill_dir}")
        return None

    # 创建技能目录
    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"✅ 已创建技能目录：{skill_dir}")
    except Exception as e:
        print(f"❌ 创建目录时出错：{e}")
        return None

    # 从模板创建 SKILL.md
    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print("✅ 已创建 SKILL.md")
    except Exception as e:
        print(f"❌ 创建 SKILL.md 时出错：{e}")
        return None

    # 创建资源目录及示例文件
    try:
        # 创建 scripts/ 目录及示例脚本
        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        example_script.chmod(0o755)
        print("✅ 已创建 scripts/example.py")

        # 创建 references/ 目录及示例参考文档
        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_reference = references_dir / 'api_reference.md'
        example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("✅ 已创建 references/api_reference.md")

        # 创建 assets/ 目录及示例资源占位符
        assets_dir = skill_dir / 'assets'
        assets_dir.mkdir(exist_ok=True)
        example_asset = assets_dir / 'example_asset.txt'
        example_asset.write_text(EXAMPLE_ASSET)
        print("✅ 已创建 assets/example_asset.txt")
    except Exception as e:
        print(f"❌ 创建资源目录时出错：{e}")
        return None

    # 打印下一步操作
    print(f"\n✅ 技能 '{skill_name}' 已成功在 {skill_dir} 初始化")
    print("\n下一步：")
    print("1. 编辑 SKILL.md 以完成 TODO 项目并更新描述")
    print("2. 定制或删除 scripts/、references/ 和 assets/ 中的示例文件")
    print("3. 准备就绪时运行验证器以检查技能结构")

    return skill_dir


def main():
    if len(sys.argv) < 4 or sys.argv[2] != '--path':
        print("用法：init_skill.py <技能名称> --path <路径>")
        print("\n技能名称要求：")
        print("  - 连字符标识符(例如 'data-analyzer')")
        print("  - 仅小写字母、数字和连字符")
        print("  - 最多 40 个字符")
        print("  - 必须与目录名称完全匹配")
        print("\n示例：")
        print("  init_skill.py my-new-skill --path skills/public")
        print("  init_skill.py my-api-helper --path skills/private")
        print("  init_skill.py custom-skill --path /custom/location")
        sys.exit(1)

    skill_name = sys.argv[1]
    path = sys.argv[3]

    print(f"🚀 初始化技能：{skill_name}")
    print(f"   位置：{path}")
    print()

    result = init_skill(skill_name, path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
