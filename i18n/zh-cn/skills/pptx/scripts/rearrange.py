#!/usr/bin/env python3
"""
根据索引序列重新排列 PowerPoint 幻灯片。

用法：
    python rearrange.py template.pptx output.pptx 0,34,34,50,52

这将使用 template.pptx 中指定顺序的幻灯片创建 output.pptx。
幻灯片可以重复（例如，34 出现两次）。
"""

import argparse
import shutil
import sys
from copy import deepcopy
from pathlib import Path

import six
from pptx import Presentation


def main():
    parser = argparse.ArgumentParser(
        description="根据索引序列重新排列 PowerPoint 幻灯片。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python rearrange.py template.pptx output.pptx 0,34,34,50,52
    使用 template.pptx 中的幻灯片 0、34（两次）、50 和 52 创建 output.pptx

  python rearrange.py template.pptx output.pptx 5,3,1,2,4
    按照指定顺序重新排序幻灯片创建 output.pptx

注意：幻灯片索引基于 0（第一张幻灯片是 0，第二张是 1，依此类推）
        """,
    )

    parser.add_argument("template", help="模板 PPTX 文件路径")
    parser.add_argument("output", help="输出 PPTX 文件路径")
    parser.add_argument(
        "sequence", help="逗号分隔的幻灯片索引序列（基于 0）"
    )

    args = parser.parse_args()

    # 解析幻灯片序列
    try:
        slide_sequence = [int(x.strip()) for x in args.sequence.split(",")]
    except ValueError:
        print(
            "错误：无效的序列格式。使用逗号分隔的整数（例如，0,34,34,50,52）"
        )
        sys.exit(1)

    # 检查模板是否存在
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"错误：未找到模板文件：{args.template}")
        sys.exit(1)

    # 如有需要，创建输出目录
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        rearrange_presentation(template_path, output_path, slide_sequence)
    except ValueError as e:
        print(f"错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"处理演示文稿时出错：{e}")
        sys.exit(1)


def duplicate_slide(pres, index):
    """复制演示文稿中的幻灯片。"""
    source = pres.slides[index]

    # 使用源幻灯片的布局以保留格式
    new_slide = pres.slides.add_slide(source.slide_layout)

    # 从源幻灯片收集所有图像和媒体关系
    image_rels = {}
    for rel_id, rel in six.iteritems(source.part.rels):
        if "image" in rel.reltype or "media" in rel.reltype:
            image_rels[rel_id] = rel

    # 关键：清除占位符形状以避免重复
    for shape in new_slide.shapes:
        sp = shape.element
        sp.getparent().remove(sp)

    # 复制源幻灯片的所有形状
    for shape in source.shapes:
        el = shape.element
        new_el = deepcopy(el)
        new_slide.shapes._spTree.insert_element_before(new_el, "p:extLst")

        # 处理图片形状 - 需要更新 blip 引用
        # 查找所有 blip 元素（它们可能在 pic 或其他上下文中）
        # 使用元素自己的 xpath 方法，不带命名空间参数
        blips = new_el.xpath(".//a:blip[@r:embed]")
        for blip in blips:
            old_rId = blip.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
            )
            if old_rId in image_rels:
                # 为目标幻灯片中的此图像创建新的关系
                old_rel = image_rels[old_rId]
                # get_or_add 直接返回 rId，或添加并返回新的 rId
                new_rId = new_slide.part.rels.get_or_add(
                    old_rel.reltype, old_rel._target
                )
                # 更新 blip 的 embed 引用以使用新的关系 ID
                blip.set(
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed",
                    new_rId,
                )

    # 复制可能在其他地方引用的任何额外图像/媒体关系
    for rel_id, rel in image_rels.items():
        try:
            new_slide.part.rels.get_or_add(rel.reltype, rel._target)
        except Exception:
            pass  # 关系可能已经存在

    return new_slide


def delete_slide(pres, index):
    """从演示文稿中删除幻灯片。"""
    rId = pres.slides._sldIdLst[index].rId
    pres.part.drop_rel(rId)
    del pres.slides._sldIdLst[index]


def reorder_slides(pres, slide_index, target_index):
    """将幻灯片从一个位置移动到另一个位置。"""
    slides = pres.slides._sldIdLst

    # 从当前位置移除幻灯片元素
    slide_element = slides[slide_index]
    slides.remove(slide_element)

    # 插入到目标位置
    slides.insert(target_index, slide_element)


def rearrange_presentation(template_path, output_path, slide_sequence):
    """
    使用模板中指定顺序的幻灯片创建新演示文稿。

    参数：
        template_path: 模板 PPTX 文件路径
        output_path: 输出 PPTX 文件路径
        slide_sequence: 要包含的幻灯片索引列表（基于 0）
    """
    # 复制模板以保留尺寸和主题
    if template_path != output_path:
        shutil.copy2(template_path, output_path)
        prs = Presentation(output_path)
    else:
        prs = Presentation(template_path)

    total_slides = len(prs.slides)

    # 验证索引
    for idx in slide_sequence:
        if idx < 0 or idx >= total_slides:
            raise ValueError(f"幻灯片索引 {idx} 超出范围 (0-{total_slides - 1})")

    # 跟踪原始幻灯片及其副本
    slide_map = []  # 最终演示文稿的实际幻灯片索引列表
    duplicated = {}  # 跟踪副本：original_idx -> [duplicate_indices]

    # 步骤 1：复制重复的幻灯片
    print(f"从模板处理 {len(slide_sequence)} 张幻灯片...")
    for i, template_idx in enumerate(slide_sequence):
        if template_idx in duplicated and duplicated[template_idx]:
            # 已经复制了此幻灯片，使用副本
            slide_map.append(duplicated[template_idx].pop(0))
            print(f"  [{i}] 使用幻灯片 {template_idx} 的副本")
        elif slide_sequence.count(template_idx) > 1 and template_idx not in duplicated:
            # 重复幻灯片的第一次出现 - 创建副本
            slide_map.append(template_idx)
            duplicates = []
            count = slide_sequence.count(template_idx) - 1
            print(
                f"  [{i}] 使用原始幻灯片 {template_idx}，创建 {count} 个副本"
            )
            for _ in range(count):
                duplicate_slide(prs, template_idx)
                duplicates.append(len(prs.slides) - 1)
            duplicated[template_idx] = duplicates
        else:
            # 唯一幻灯片或已处理的第一次出现，使用原始幻灯片
            slide_map.append(template_idx)
            print(f"  [{i}] 使用原始幻灯片 {template_idx}")

    # 步骤 2：删除不需要的幻灯片（反向操作）
    slides_to_keep = set(slide_map)
    print(f"\n删除 {len(prs.slides) - len(slides_to_keep)} 张未使用的幻灯片...")
    for i in range(len(prs.slides) - 1, -1, -1):
        if i not in slides_to_keep:
            delete_slide(prs, i)
            # 删除后更新 slide_map 索引
            slide_map = [idx - 1 if idx > i else idx for idx in slide_map]

    # 步骤 3：重新排序为最终序列
    print(f"将 {len(slide_map)} 张幻灯片重新排序为最终序列...")
    for target_pos in range(len(slide_map)):
        # 找出哪个幻灯片应该在 target_pos
        current_pos = slide_map[target_pos]
        if current_pos != target_pos:
            reorder_slides(prs, current_pos, target_pos)
            # 更新 slide_map：移动会改变其他幻灯片的位置
            for i in range(len(slide_map)):
                if slide_map[i] > current_pos and slide_map[i] <= target_pos:
                    slide_map[i] -= 1
                elif slide_map[i] < current_pos and slide_map[i] >= target_pos:
                    slide_map[i] += 1
            slide_map[target_pos] = target_pos

    # 保存演示文稿
    prs.save(output_path)
    print(f"\n已将重新排列的演示文稿保存到：{output_path}")
    print(f"最终演示文稿有 {len(prs.slides)} 张幻灯片")


if __name__ == "__main__":
    main()