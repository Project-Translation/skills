"""
Word 文档修订追踪验证器。
"""

import subprocess
import tempfile
import zipfile
from pathlib import Path


class RedliningValidator:
    """Word 文档修订追踪验证器。"""

    def __init__(self, unpacked_dir, original_docx, verbose=False):
        self.unpacked_dir = Path(unpacked_dir)
        self.original_docx = Path(original_docx)
        self.verbose = verbose
        self.namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

    def validate(self):
        """主验证方法，如果有效返回 True，否则返回 False。"""
        # 验证解压目录存在且具有正确结构
        modified_file = self.unpacked_dir / "word" / "document.xml"
        if not modified_file.exists():
            print(f"FAILED - 未在 {modified_file} 找到修改后的 document.xml")
            return False

        # 首先，检查是否有 Claude 的修订追踪变更需要验证
        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(modified_file)
            root = tree.getroot()

            # 检查是否有 Claude 作者的 w:del 或 w:ins 标签
            del_elements = root.findall(".//w:del", self.namespaces)
            ins_elements = root.findall(".//w:ins", self.namespaces)

            # 过滤出仅包含 Claude 的变更
            claude_del_elements = [
                elem
                for elem in del_elements
                if elem.get(f"{{{self.namespaces['w']}}}author") == "Claude"
            ]
            claude_ins_elements = [
                elem
                for elem in ins_elements
                if elem.get(f"{{{self.namespaces['w']}}}author") == "Claude"
            ]

            # 仅当存在 Claude 的修订追踪变更时才需要进行修订追踪验证。
            if not claude_del_elements and not claude_ins_elements:
                if self.verbose:
                    print("PASSED - 未找到 Claude 的修订追踪变更。")
                return True

        except Exception:
            # 如果无法解析 XML，继续进行完整验证
            pass

        # 为解压原始 docx 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 解压原始 docx
            try:
                with zipfile.ZipFile(self.original_docx, "r") as zip_ref:
                    zip_ref.extractall(temp_path)
            except Exception as e:
                print(f"FAILED - 解压原始 docx 时出错: {e}")
                return False

            original_file = temp_path / "word" / "document.xml"
            if not original_file.exists():
                print(
                    f"FAILED - 在 {self.original_docx} 中未找到原始 document.xml"
                )
                return False

            # 使用 xml.etree.ElementTree 解析两个 XML 文件以进行修订追踪验证
            try:
                import xml.etree.ElementTree as ET

                modified_tree = ET.parse(modified_file)
                modified_root = modified_tree.getroot()
                original_tree = ET.parse(original_file)
                original_root = original_tree.getroot()
            except ET.ParseError as e:
                print(f"FAILED - 解析 XML 文件时出错: {e}")
                return False

            # 从两个文档中移除 Claude 的修订追踪变更
            self._remove_claude_tracked_changes(original_root)
            self._remove_claude_tracked_changes(modified_root)

            # 提取并比较文本内容
            modified_text = self._extract_text_content(modified_root)
            original_text = self._extract_text_content(original_root)

            if modified_text != original_text:
                # 为每个段落显示详细字符级差异
                error_message = self._generate_detailed_diff(
                    original_text, modified_text
                )
                print(error_message)
                return False

            if self.verbose:
                print("PASSED - Claude 的所有变更都已正确追踪")
            return True

    def _generate_detailed_diff(self, original_text, modified_text):
        """使用 git 单词差异生成详细单词级差异。"""
        error_parts = [
            "FAILED - 移除 Claude 的修订追踪变更后文档文本不匹配",
            "",
            "可能的原因:",
            "  1. 在其他作者的 <w:ins> 或 <w:del> 标签内修改文本",
            "  2. 进行编辑时未使用适当的修订追踪",
            "  3. 删除他人插入时未在 <w:ins> 内嵌套 <w:del>",
            "",
            "对于预修订文档，请使用正确的模式:",
            "  - 要拒绝他人的 INSERTION：在他们的 <w:ins> 内嵌套 <w:del>",
            "  - 要恢复他人的 DELETION：在他们的 <w:del> 后添加新的 <w:ins>",
            "",
        ]

        # 显示 git 单词差异
        git_diff = self._get_git_word_diff(original_text, modified_text)
        if git_diff:
            error_parts.extend(["差异:", "============", git_diff])
        else:
            error_parts.append("无法生成单词差异 (git 不可用)")

        return "\n".join(error_parts)

    def _get_git_word_diff(self, original_text, modified_text):
        """使用 git 生成字符级精度的单词差异。"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # 创建两个文件
                original_file = temp_path / "original.txt"
                modified_file = temp_path / "modified.txt"

                original_file.write_text(original_text, encoding="utf-8")
                modified_file.write_text(modified_text, encoding="utf-8")

                # 首先尝试字符级差异以获得精确差异
                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--word-diff=plain",
                        "--word-diff-regex=.",  # 逐字符差异
                        "-U0",  # 零行上下文 - 仅显示变更行
                        "--no-index",
                        str(original_file),
                        str(modified_file),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.stdout.strip():
                    # 清理输出 - 移除 git diff 头部行
                    lines = result.stdout.split("\n")
                    # 跳过头部行 (diff --git, index, +++, ---, @@)
                    content_lines = []
                    in_content = False
                    for line in lines:
                        if line.startswith("@@"):
                            in_content = True
                            continue
                        if in_content and line.strip():
                            content_lines.append(line)

                    if content_lines:
                        return "\n".join(content_lines)

                # 如果字符级差异过于冗长，则回退到单词级差异
                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--word-diff=plain",
                        "-U0",  # 零行上下文
                        "--no-index",
                        str(original_file),
                        str(modified_file),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.stdout.strip():
                    lines = result.stdout.split("\n")
                    content_lines = []
                    in_content = False
                    for line in lines:
                        if line.startswith("@@"):
                            in_content = True
                            continue
                        if in_content and line.strip():
                            content_lines.append(line)
                    return "\n".join(content_lines)

        except (subprocess.CalledProcessError, FileNotFoundError, Exception):
            # git 不可用或其他错误，返回 None 以使用回退
            pass

        return None

    def _remove_claude_tracked_changes(self, root):
        """从 XML 根元素中移除 Claude 作者的修订追踪变更。"""
        ins_tag = f"{{{self.namespaces['w']}}}ins"
        del_tag = f"{{{self.namespaces['w']}}}del"
        author_attr = f"{{{self.namespaces['w']}}}author"

        # 移除 w:ins 元素
        for parent in root.iter():
            to_remove = []
            for child in parent:
                if child.tag == ins_tag and child.get(author_attr) == "Claude":
                    to_remove.append(child)
            for elem in to_remove:
                parent.remove(elem)

        # 解包 w:del 元素中的内容，其中作者为 "Claude"
        deltext_tag = f"{{{self.namespaces['w']}}}delText"
        t_tag = f"{{{self.namespaces['w']}}}t"

        for parent in root.iter():
            to_process = []
            for child in parent:
                if child.tag == del_tag and child.get(author_attr) == "Claude":
                    to_process.append((child, list(parent).index(child)))

            # 反向处理以保持索引
            for del_elem, del_index in reversed(to_process):
                # 在移动前将 w:delText 转换为 w:t
                for elem in del_elem.iter():
                    if elem.tag == deltext_tag:
                        elem.tag = t_tag

                # 在移除 w:del 前将 w:del 的所有子元素移动到其父元素
                for child in reversed(list(del_elem)):
                    parent.insert(del_index, child)
                parent.remove(del_elem)

    def _extract_text_content(self, root):
        """从 Word XML 中提取文本内容，保持段落结构。

        空段落会被跳过，以避免当追踪插入仅添加结构元素而不添加文本内容时出现误报。
        """
        p_tag = f"{{{self.namespaces['w']}}}p"
        t_tag = f"{{{self.namespaces['w']}}}t"

        paragraphs = []
        for p_elem in root.findall(f".//{p_tag}"):
            # 获取此段落中的所有文本元素
            text_parts = []
            for t_elem in p_elem.findall(f".//{t_tag}"):
                if t_elem.text:
                    text_parts.append(t_elem.text)
            paragraph_text = "".join(text_parts)
            # 跳过空段落 - 它们不影响内容验证
            if paragraph_text:
                paragraphs.append(paragraph_text)

        return "\n".join(paragraphs)


if __name__ == "__main__":
    raise RuntimeError("此模块不应直接运行。")