#!/usr/bin/env python3
"""
用于根据 XSD 模式和跟踪的更改验证 Office 文档 XML 文件的命令行工具。

用法:
    python validate.py <dir> --original <original_file>
"""

import argparse
import sys
from pathlib import Path

from validation import DOCXSchemaValidator, PPTXSchemaValidator, RedliningValidator


def main():
    parser = argparse.ArgumentParser(description="验证 Office 文档 XML 文件")
    parser.add_argument(
        "unpacked_dir",
        help="解包后的 Office 文档目录路径",
    )
    parser.add_argument(
        "--original",
        required=True,
        help="原始文件路径 (.docx/.pptx/.xlsx)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="启用详细输出",
    )
    args = parser.parse_args()

    # 验证路径
    unpacked_dir = Path(args.unpacked_dir)
    original_file = Path(args.original)
    file_extension = original_file.suffix.lower()
    assert unpacked_dir.is_dir(), f"错误: {unpacked_dir} 不是一个目录"
    assert original_file.is_file(), f"错误: {original_file} 不是一个文件"
    assert file_extension in [".docx", ".pptx", ".xlsx"], (
        f"错误: {original_file} 必须是 .docx、.pptx 或 .xlsx 文件"
    )

    # 运行验证
    match file_extension:
        case ".docx":
            validators = [DOCXSchemaValidator, RedliningValidator]
        case ".pptx":
            validators = [PPTXSchemaValidator]
        case _:
            print(f"错误: 不支持文件类型 {file_extension} 的验证")
            sys.exit(1)

    # 运行验证器
    success = True
    for V in validators:
        validator = V(unpacked_dir, original_file, verbose=args.verbose)
        if not validator.validate():
            success = False

    if success:
        print("所有验证均通过！")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
