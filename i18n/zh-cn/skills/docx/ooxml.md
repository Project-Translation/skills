# Office Open XML 技术参考

**重要：开始前请完整阅读本文档。** 本文档涵盖：
- [技术指南](#技术指南) - 模式合规规则和验证要求
- [文档内容模式](#文档内容模式) - 标题、列表、表格、格式等的 XML 模式
- [文档库（Python）](#文档库-python) - 推荐的 OOXML 操作方法，自动设置基础设施
- [跟踪更改（修订标记）](#跟踪更改-修订标记) - 实现跟踪更改的 XML 模式

## 技术指南

### 模式合规性
- **`<w:pPr>` 中的元素顺序**：`<w:pStyle>`、`<w:numPr>`、`<w:spacing>`、`<w:ind>`、`<w:jc>`
- **空白符**：在具有前导/尾随空格的 `<w:t>` 元素上添加 `xml:space='preserve'`
- **Unicode**：将 ASCII 内容中的字符转义为：`"` 变为 `&#8220;`
  - **字符编码参考**：弯引号 `""` 变为 `&#8220;&#8221;`，撇号 `'` 变为 `&#8217;`，破折号 `—` 变为 `&#8212;`
- **跟踪更改**：在 `<w:r>` 元素外使用 `<w:del>` 和 `<w:ins>` 标签，`w:author="Claude"`
  - **关键**：`<w:ins>` 以 `</w:ins>` 结尾，`<w:del>` 以 `</w:del>` 结尾 - 切勿混淆
  - **RSIDs 必须是 8 位十六进制**：使用类似 `00AB1234` 的值（仅限 0-9、A-F 字符）
  - **trackRevisions 位置**：在 settings.xml 中的 `<w:proofState>` 后添加 `<w:trackRevisions/>`
- **图像**：添加到 `word/media/`，在 `document.xml` 中引用，设置尺寸以防止溢出

## 文档内容模式

### 基本结构
```xml
<w:p>
  <w:r><w:t>文本内容</w:t></w:r>
</w:p>
```

### 标题和样式
```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="Title"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t>文档标题</w:t></w:r>
</w:p>

<w:p>
  <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
  <w:r><w:t>章节标题</w:t></w:r>
</w:p>
```

### 文本格式化
```xml
<!-- 加粗 -->
<w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>加粗</w:t></w:r>
<!-- 斜体 -->
<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>斜体</w:t></w:r>
<!-- 下划线 -->
<w:r><w:rPr><w:u w:val="single"/></w:rPr><w:t>下划线</w:t></w:r>
<!-- 高亮 -->
<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>高亮</w:t></w:r>
```

### 列表
```xml
<!-- 编号列表 -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>
    <w:spacing w:before="240"/>
  </w:pPr>
  <w:r><w:t>第一项</w:t></w:r>
</w:p>

<!-- 从 1 重新开始编号列表 - 使用不同的 numId -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr>
    <w:spacing w:before="240"/>
  </w:pPr>
  <w:r><w:t>新列表项 1</w:t></w:r>
</w:p>

<!-- 项目符号列表（级别 2） -->
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr>
    <w:spacing w:before="240"/>
    <w:ind w:left="900"/>
  </w:pPr>
  <w:r><w:t>项目符号项</w:t></w:r>
</w:p>
```

### 表格
```xml
<w:tbl>
  <w:tblPr>
    <w:tblStyle w:val="TableGrid"/>
    <w:tblW w:w="0" w:type="auto"/>
  </w:tblPr>
  <w:tblGrid>
    <w:gridCol w:w="4675"/><w:gridCol w:w="4675"/>
  </w:tblGrid>
  <w:tr>
    <w:tc>
      <w:tcPr><w:tcW w:w="4675" w:type="dxa"/></w:tcPr>
      <w:p><w:r><w:t>单元格 1</w:t></w:r></w:p>
    </w:tc>
    <w:tc>
      <w:tcPr><w:tcW w:w="4675" w:type="dxa"/></w:tcPr>
      <w:p><w:r><w:t>单元格 2</w:t></w:r></w:p>
    </w:tc>
  </w:tr>
</w:tbl>
```

### 布局
```xml
<!-- 新章节前分页（常见模式） -->
<w:p>
  <w:r>
    <w:br w:type="page"/>
  </w:r>
</w:p>
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading1"/>
  </w:pPr>
  <w:r>
    <w:t>新章节标题</w:t>
  </w:r>
</w:p>

<!-- 居中段落 -->
<w:p>
  <w:pPr>
    <w:spacing w:before="240" w:after="0"/>
    <w:jc w:val="center"/>
  </w:pPr>
  <w:r><w:t>居中文本</w:t></w:r>
</w:p>

<!-- 字体更改 - 段落级别（应用于所有运行） -->
<w:p>
  <w:pPr>
    <w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/></w:rPr>
  </w:pPr>
  <w:r><w:t>等宽文本</w:t></w:r>
</w:p>

<!-- 字体更改 - 运行级别（仅适用于此文本） -->
<w:p>
  <w:r>
    <w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/></w:rPr>
    <w:t>此文本为 Courier New</w:t>
  </w:r>
  <w:r><w:t> 而此文本使用默认字体</w:t></w:r>
</w:p>
```

## 文件更新

添加内容时，更新以下文件：

**`word/_rels/document.xml.rels`：**
```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>
```

**`[Content_Types].xml`：**
```xml
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
```

### 图像
**关键**：计算尺寸以防止页面溢出并保持宽高比。

```xml
<!-- 最小必需结构 -->
<w:p>
  <w:r>
    <w:drawing>
      <wp:inline>
        <wp:extent cx="2743200" cy="1828800"/>
        <wp:docPr id="1" name="Picture 1"/>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr>
                <pic:cNvPr id="0" name="image1.png"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="rId5"/>
                <!-- 添加拉伸填充并保持宽高比 -->
                <a:stretch>
                  <a:fillRect/>
                </a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm>
                  <a:ext cx="2743200" cy="1828800"/>
                </a:xfrm>
                <a:prstGeom prst="rect"/>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
```

### 链接（超链接）

**重要**：所有超链接（内部和外部）都需要在 styles.xml 中定义 Hyperlink 样式。没有此样式，链接将显示为普通文本，而不是蓝色下划线的可点击链接。

**外部链接：**
```xml
<!-- 在 document.xml 中 -->
<w:hyperlink r:id="rId5">
  <w:r>
    <w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>
    <w:t>链接文本</w:t>
  </w:r>
</w:hyperlink>

<!-- 在 word/_rels/document.xml.rels 中 -->
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" 
              Target="https://www.example.com/" TargetMode="External"/>
```

**内部链接：**

```xml
<!-- 链接到书签 -->
<w:hyperlink w:anchor="myBookmark">
  <w:r>
    <w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>
    <w:t>链接文本</w:t>
  </w:r>
</w:hyperlink>

<!-- 书签目标 -->
<w:bookmarkStart w:id="0" w:name="myBookmark"/>
<w:r><w:t>目标内容</w:t></w:r>
<w:bookmarkEnd w:id="0"/>
```

**超链接样式（在 styles.xml 中必需）：**
```xml
<w:style w:type="character" w:styleId="Hyperlink">
  <w:name w:val="Hyperlink"/>
  <w:basedOn w:val="DefaultParagraphFont"/>
  <w:uiPriority w:val="99"/>
  <w:unhideWhenUsed/>
  <w:rPr>
    <w:color w:val="467886" w:themeColor="hyperlink"/>
    <w:u w:val="single"/>
  </w:rPr>
</w:style>
```

## 文档库（Python）

使用 `scripts/document.py` 中的 Document 类处理所有跟踪更改和注释。它会自动处理基础设施设置（people.xml、RSIDs、settings.xml、注释文件、关系、内容类型）。仅在库不支持的复杂场景中使用直接 XML 操作。

**处理 Unicode 和实体：**
- **搜索**：实体表示法和 Unicode 字符均可使用 - `contains="&#8220;Company"` 和 `contains="\u201cCompany"` 找到相同文本
- **替换**：使用实体（`&#8220;`）或 Unicode（`\u201c`）均可 - 两者都有效，将根据文件编码进行适当转换（ascii → 实体，utf-8 → Unicode）

### 初始化

**找到 docx 技能根目录**（包含 `scripts/` 和 `ooxml/` 的目录）：
```bash
# 搜索 document.py 以定位技能根目录
# 注意：这里使用 /mnt/skills 作为示例；请根据您的上下文检查实际位置
find /mnt/skills -name "document.py" -path "*/docx/scripts/*" 2>/dev/null | head -1
# 示例输出：/mnt/skills/docx/scripts/document.py
# 技能根目录为：/mnt/skills/docx
```

**使用 PYTHONPATH 运行脚本**：
```bash
PYTHONPATH=/mnt/skills/docx python your_script.py
```

**在脚本中**，从技能根目录导入：
```python
from scripts.document import Document, DocxXMLEditor

# 基本初始化（自动创建临时副本并设置基础设施）
doc = Document('unpacked')

# 自定义作者和姓名首字母
doc = Document('unpacked', author="John Doe", initials="JD")

# 启用跟踪修订模式
doc = Document('unpacked', track_revisions=True)

# 指定自定义 RSID（未提供时自动生成）
doc = Document('unpacked', rsid="07DC5ECB")
```

### 创建跟踪更改

**关键**：仅标记实际更改的文本。保持所有未更改的文本在 `<w:del>`/`<w:ins>` 标签外。标记未更改的文本会使编辑显得不专业且难以审查。

**属性处理**：Document 类会自动将属性（w:id、w:date、w:rsidR、w:rsidDel、w16du:dateUtc、xml:space）注入新元素。当保留原始文档中的未更改文本时，复制原始 `<w:r>` 元素及其现有属性以保持文档完整性。

**方法选择指南**：
- **向常规文本添加自己的更改**：使用 `<w:del>`/`<w:ins>` 标签的 `replace_node()`，或使用 `suggest_deletion()` 删除整个 `<w:r>` 或 `<w:p>` 元素
- **部分修改其他作者的跟踪更改**：使用 `replace_node()` 将您的更改嵌套在他们的 `<w:ins>`/`<w:del>` 内
- **完全拒绝其他作者的插入**：在 `<w:ins>` 元素上使用 `revert_insertion()`（不是 `suggest_deletion()`）
- **完全拒绝其他作者的删除**：在 `<w:del>` 元素上使用 `revert_deletion()` 以使用跟踪更改恢复已删除的内容

```python
# 最小编辑 - 更改一个单词："The report is monthly" → "The report is quarterly"
# 原始：<w:r w:rsidR="00AB12CD"><w:rPr><w:rFonts w:ascii="Calibri"/></w:rPr><w:t>The report is monthly</w:t></w:r>
node = doc["word/document.xml"].get_node(tag="w:r", contains="The report is monthly")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:r w:rsidR="00AB12CD">{rpr}<w:t>The report is </w:t></w:r><w:del><w:r>{rpr}<w:delText>monthly</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>quarterly</w:t></w:r></w:ins>'
doc["word/document.xml"].replace_node(node, replacement)

# 最小编辑 - 更改数字："within 30 days" → "within 45 days"
# 原始：<w:r w:rsidR="00XYZ789"><w:rPr><w:rFonts w:ascii="Calibri"/></w:rPr><w:t>within 30 days</w:t></w:r>
node = doc["word/document.xml"].get_node(tag="w:r", contains="within 30 days")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:r w:rsidR="00XYZ789">{rpr}<w:t>within </w:t></w:r><w:del><w:r>{rpr}<w:delText>30</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>45</w:t></w:r></w:ins><w:r w:rsidR="00XYZ789">{rpr}<w:t> days</w:t></w:r>'
doc["word/document.xml"].replace_node(node, replacement)

# 完全替换 - 即使替换所有文本也保持格式
node = doc["word/document.xml"].get_node(tag="w:r", contains="apple")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""
replacement = f'<w:del><w:r>{rpr}<w:delText>apple</w:delText></w:r></w:del><w:ins><w:r>{rpr}<w:t>banana orange</w:t></w:r></w:ins>'
doc["word/document.xml"].replace_node(node, replacement)

# 插入新内容（不需要属性 - 自动注入）
node = doc["word/document.xml"].get_node(tag="w:r", contains="existing text")
doc["word/document.xml"].insert_after(node, '<w:ins><w:r><w:t>new text</w:t></w:r></w:ins>')

# 部分删除其他作者的插入
# 原始：<w:ins w:author="Jane Smith" w:date="..."><w:r><w:t>quarterly financial report</w:t></w:r></w:ins>
# 目标：仅删除 "financial" 使其变为 "quarterly report"
node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
# 重要：在外部 <w:ins> 上保留 w:author="Jane Smith" 以保持作者身份
replacement = '''<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:r><w:t>quarterly </w:t></w:r>
  <w:del><w:r><w:delText>financial </w:delText></w:r></w:del>
  <w:r><w:t>report</w:t></w:r>
</w:ins>'''
doc["word/document.xml"].replace_node(node, replacement)

# 更改其他作者插入的部分
# 原始：<w:ins w:author="Jane Smith"><w:r><w:t>in silence, safe and sound</w:t></w:r></w:ins>
# 目标：将 "safe and sound" 更改为 "soft and unbound"
node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "8"})
replacement = f'''<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:r><w:t>in silence, </w:t></w:r>
</w:ins>
<w:ins>
  <w:r><w:t>soft and unbound</w:t></w:r>
</w:ins>
<w:ins w:author="Jane Smith" w:date="2025-01-15T10:00:00Z">
  <w:del><w:r><w:delText>safe and sound</w:delText></w:r></w:del>
</w:ins>'''
doc["word/document.xml"].replace_node(node, replacement)

# 删除整个运行（仅在删除所有内容时使用；部分删除使用 replace_node）
node = doc["word/document.xml"].get_node(tag="w:r", contains="要删除的文本")
doc["word/document.xml"].suggest_deletion(node)

# 删除整个段落（就地处理，处理常规和编号列表段落）
para = doc["word/document.xml"].get_node(tag="w:p", contains="要删除的段落")
doc["word/document.xml"].suggest_deletion(para)

# 添加新的编号列表项
target_para = doc["word/document.xml"].get_node(tag="w:p", contains="现有列表项")
pPr = tags[0].toxml() if (tags := target_para.getElementsByTagName("w:pPr")) else ""
new_item = f'<w:p>{pPr}<w:r><w:t>新项</w:t></w:r></w:p>'
tracked_para = DocxXMLEditor.suggest_paragraph(new_item)
doc["word/document.xml"].insert_after(target_para, tracked_para)
# 可选：在内容前添加间距段落以获得更好的视觉分离
# spacing = DocxXMLEditor.suggest_paragraph('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/></w:pPr></w:p>')
# doc["word/document.xml"].insert_after(target_para, spacing + tracked_para)
```

### 添加注释

```python
# 在两个现有跟踪更改上添加注释
# 注意：w:id 是自动生成的。只有在从 XML 检查中知道时才按 w:id 搜索
start_node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})
end_node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "2"})
doc.add_comment(start=start_node, end=end_node, text="此更改的说明")

# 在段落上添加注释
para = doc["word/document.xml"].get_node(tag="w:p", contains="段落文本")
doc.add_comment(start=para, end=para, text="关于此段落的注释")

# 在新创建的跟踪更改上添加注释
# 首先创建跟踪更改
node = doc["word/document.xml"].get_node(tag="w:r", contains="old")
new_nodes = doc["word/document.xml"].replace_node(
    node,
    '<w:del><w:r><w:delText>old</w:delText></w:r></w:del><w:ins><w:r><w:t>new</w:t></w:r></w:ins>'
)
# 然后在新创建的元素上添加注释
# new_nodes[0] 是 <w:del>，new_nodes[1] 是 <w:ins>
doc.add_comment(start=new_nodes[0], end=new_nodes[1], text="根据要求将 old 更改为 new")

# 回复现有注释
doc.reply_to_comment(parent_comment_id=0, text="我同意此更改")
```

### 拒绝跟踪更改

**重要**：使用 `revert_insertion()` 拒绝插入，使用 `revert_deletion()` 使用跟踪更改恢复删除。仅对常规未标记内容使用 `suggest_deletion()`。

```python
# 拒绝插入（将其包装在删除中）
# 当其他作者插入您想要删除的文本时使用
ins = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
nodes = doc["word/document.xml"].revert_insertion(ins)  # 返回 [ins]

# 拒绝删除（创建插入以恢复已删除的内容）
# 当其他作者删除您想要恢复的文本时使用
del_elem = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "3"})
nodes = doc["word/document.xml"].revert_deletion(del_elem)  # 返回 [del_elem, new_ins]

# 拒绝段落中的所有插入
para = doc["word/document.xml"].get_node(tag="w:p", contains="段落文本")
nodes = doc["word/document.xml"].revert_insertion(para)  # 返回 [para]

# 拒绝段落中的所有删除
para = doc["word/document.xml"].get_node(tag="w:p", contains="段落文本")
nodes = doc["word/document.xml"].revert_deletion(para)  # 返回 [para]
```

### 插入图像

**关键**：Document 类使用 `doc.unpacked_path` 处的临时副本工作。始终将图像复制到此临时目录，而不是原始的 unpacked 文件夹。

```python
from PIL import Image
import shutil, os

# 首先初始化文档
doc = Document('unpacked')

# 复制图像并计算保持宽高比的全宽尺寸
media_dir = os.path.join(doc.unpacked_path, 'word/media')
os.makedirs(media_dir, exist_ok=True)
shutil.copy('image.png', os.path.join(media_dir, 'image1.png'))
img = Image.open(os.path.join(media_dir, 'image1.png'))
width_emus = int(6.5 * 914400)  # 6.5" 可用宽度，914400 EMUs/英寸
height_emus = int(width_emus * img.size[1] / img.size[0])

# 添加关系和内容类型
rels_editor = doc['word/_rels/document.xml.rels']
next_rid = rels_editor.get_next_rid()
rels_editor.append_to(rels_editor.dom.documentElement,
    f'<Relationship Id="{next_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>')
doc['[Content_Types].xml'].append_to(doc['[Content_Types].xml'].dom.documentElement,
    '<Default Extension="png" ContentType="image/png"/>')

# 插入图像
node = doc["word/document.xml"].get_node(tag="w:p", line_number=100)
doc["word/document.xml"].insert_after(node, f'''<w:p>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{width_emus}" cy="{height_emus}"/>
        <wp:docPr id="1" name="Picture 1"/>
        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
              <pic:nvPicPr><pic:cNvPr id="1" name="image1.png"/><pic:cNvPicPr/></pic:nvPicPr>
              <pic:blipFill><a:blip r:embed="{next_rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
              <pic:spPr><a:xfrm><a:ext cx="{width_emus}" cy="{height_emus}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>''')
```

### 获取节点

```python
# 按文本内容
node = doc["word/document.xml"].get_node(tag="w:p", contains="特定文本")

# 按行范围
para = doc["word/document.xml"].get_node(tag="w:p", line_number=range(100, 150))

# 按属性
node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})

# 按确切行号（必须是标签打开的行号）
para = doc["word/document.xml"].get_node(tag="w:p", line_number=42)

# 组合过滤器
node = doc["word/document.xml"].get_node(tag="w:r", line_number=range(40, 60), contains="text")

# 当文本多次出现时消除歧义 - 添加 line_number 范围
node = doc["word/document.xml"].get_node(tag="w:r", contains="Section", line_number=range(2400, 2500))
```

### 保存

```python
# 保存并自动验证（复制回原始目录）
doc.save()  # 默认验证，如果验证失败则引发错误

# 保存到不同位置
doc.save('modified-unpacked')

# 跳过验证（仅用于调试 - 在生产中需要此功能表明 XML 存在问题）
doc.save(validate=False)
```

### 直接 DOM 操作

对于库未涵盖的复杂场景：

```python
# 访问任何 XML 文件
editor = doc["word/document.xml"]
editor = doc["word/comments.xml"]

# 直接 DOM 访问（defusedxml.minidom.Document）
node = doc["word/document.xml"].get_node(tag="w:p", line_number=5)
parent = node.parentNode
parent.removeChild(node)
parent.appendChild(node)  # 移动到末尾

# 常规文档操作（无跟踪更改）
old_node = doc["word/document.xml"].get_node(tag="w:p", contains="原始文本")
doc["word/document.xml"].replace_node(old_node, "<w:p><w:r><w:t>替换文本</w:t></w:r></w:p>")

# 多次插入 - 使用返回值保持顺序
node = doc["word/document.xml"].get_node(tag="w:r", line_number=100)
nodes = doc["word/document.xml"].insert_after(node, "<w:r><w:t>A</w:t></w:r>")
nodes = doc["word/document.xml"].insert_after(nodes[-1], "<w:r><w:t>B</w:t></w:r>")
nodes = doc["word/document.xml"].insert_after(nodes[-1], "<w:r><w:t>C</w:t></w:r>")
# 结果：original_node, A, B, C
```

## 跟踪更改（修订标记）

**在所有跟踪更改上使用上述 Document 类。** 以下模式仅供参考，用于构造替换 XML 字符串。

### 验证规则
验证器检查文档文本在还原 Claude 的更改后是否与原始文档匹配。这意味着：
- **切勿修改其他作者 `<w:ins>` 或 `<w:del>` 标签内的内容**
- **始终使用嵌套删除**移除其他作者的插入
- **每个编辑都必须使用 `<w:ins>` 或 `<w:del>` 标签进行适当跟踪**

### 跟踪更改模式

**关键规则**：
1. 切勿修改其他作者跟踪更改内的内容。始终使用嵌套删除。
2. **XML 结构**：始终在包含完整 `<w:r>` 元素的段落级别放置 `<w:del>` 和 `<w:ins>`。切勿嵌套在 `<w:r>` 元素内 - 这会创建无效的 XML，破坏文档处理。

**文本插入：**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-07-30T23:05:00Z" w16du:dateUtc="2025-07-31T06:05:00Z">
  <w:r w:rsidR="00792858">
    <w:t>插入的文本</w:t>
  </w:r>
</w:ins>
```

**文本删除：**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-07-30T23:05:00Z" w16du:dateUtc="2025-07-31T06:05:00Z">
  <w:r w:rsidDel="00792858">
    <w:delText>删除的文本</w:delText>
  </w:r>
</w:del>
```

**删除其他作者的插入（必须使用嵌套结构）：**
```xml
<!-- 在原始插入内嵌套删除 -->
<w:ins w:author="Jane Smith" w:id="16">
  <w:del w:author="Claude" w:id="40">
    <w:r><w:delText>monthly</w:delText></w:r>
  </w:del>
</w:ins>
<w:ins w:author="Claude" w:id="41">
  <w:r><w:t>weekly</w:t></w:r>
</w:ins>
```

**恢复其他作者的删除：**
```xml
<!-- 保持他们的删除不变，在其后添加新的插入 -->
<w:del w:author="Jane Smith" w:id="50">
  <w:r><w:delText>within 30 days</w:delText></w:r>
</w:del>
<w:ins w:author="Claude" w:id="51">
  <w:r><w:t>within 30 days</w:t></w:r>
</w:ins>
```