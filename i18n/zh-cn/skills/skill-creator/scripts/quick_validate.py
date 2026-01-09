#!/usr/bin/env python3
"""
技能快速验证脚本 - 最小版本
"""

import sys
import os
import re
import yaml
from pathlib import Path

def validate_skill(skill_path):
    """对技能进行基本验证"""
    skill_path = Path(skill_path)

    # 检查 SKILL.md 是否存在
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "未找到 SKILL.md"

    # 读取并验证 frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "未找到 YAML frontmatter"

    # 提取 frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "frontmatter 格式无效"

    frontmatter_text = match.group(1)

    # 解析 YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "frontmatter 必须是 YAML 字典"
    except yaml.YAMLError as e:
        return False, f"frontmatter 中 YAML 无效: {e}"

    # 定义允许的属性
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata'}

    # 检查意外的属性（不包括 metadata 下的嵌套键）
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"SKILL.md frontmatter 中出现意外的键: {', '.join(sorted(unexpected_keys))}。"
            f"允许的属性为: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # 检查必需字段
    if 'name' not in frontmatter:
        return False, "frontmatter 中缺少 'name'"
    if 'description' not in frontmatter:
        return False, "frontmatter 中缺少 'description'"

    # 提取名称进行验证
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"名称必须是字符串，实际为 {type(name).__name__}"
    name = name.strip()
    if name:
        # 检查命名约定（连字符命名：小写字母加连字符）
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"名称 '{name}' 应为连字符命名（仅包含小写字母、数字和连字符）"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"名称 '{name}' 不能以连字符开头/结尾或包含连续连字符"
        # 检查名称长度（根据规范最大 64 个字符）
        if len(name) > 64:
            return False, f"名称过长（{len(name)} 个字符）。最大为 64 个字符。"

    # 提取并验证描述
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"描述必须是字符串，实际为 {type(description).__name__}"
    description = description.strip()
    if description:
        # 检查角括号
        if '<' in description or '>' in description:
            return False, "描述不能包含角括号（< 或 >）"
        # 检查描述长度（根据规范最大 1024 个字符）
        if len(description) > 1024:
            return False, f"描述过长（{len(description)} 个字符）。最大为 1024 个字符。"

    return True, "技能有效！"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python quick_validate.py <技能目录>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)