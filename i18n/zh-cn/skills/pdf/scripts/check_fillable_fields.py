import sys
from pypdf import PdfReader


# 脚本供 Claude 运行以确定 PDF 是否具有可填写表单字段。参见 forms.md。


reader = PdfReader(sys.argv[1])
if (reader.get_fields()):
    print("此 PDF 具有可填写表单字段")
else:
    print("此 PDF 没有可填写表单字段；您需要目视确定数据输入位置")