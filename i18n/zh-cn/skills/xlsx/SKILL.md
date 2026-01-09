---
name: xlsx
description: "全面的电子表格创建、编辑和分析，支持公式、格式化、数据分析和可视化。当 Claude 需要处理电子表格（.xlsx、.xlsm、.csv、.tsv 等）时使用：(1) 创建带有公式和格式化的电子表格，(2) 读取或分析数据，(3) 修改现有电子表格同时保留公式，(4) 电子表格中的数据分析和可视化，或 (5) 重新计算公式"
license: 专有。LICENSE.txt 包含完整条款
---

# 输出要求

## 所有 Excel 文件

### 零公式错误
- 每个 Excel 模型必须交付时零公式错误（#REF!、#DIV/0!、#VALUE!、#N/A、#NAME?）

### 保留现有模板（更新模板时）
- 研究并完全匹配现有格式、样式和约定，修改文件时
- 切勿在已有固定模式的文件上强加标准化格式
- 现有模板约定始终优先于这些指南

## 财务模型

### 颜色编码标准
除非用户另有说明或现有模板另有规定

#### 行业标准颜色约定
- **蓝色文本 (RGB: 0,0,255)**: 硬编码输入和用户将更改情景的数字
- **黑色文本 (RGB: 0,0,0)**: 所有公式和计算
- **绿色文本 (RGB: 0,128,0)**: 从同一工作簿内其他工作表拉取的链接
- **红色文本 (RGB: 255,0,0)**: 到其他文件的外部链接
- **黄色背景 (RGB: 255,255,0)**: 需要关注或需要更新的关键假设或单元格

### 数字格式化标准

#### 必需的格式规则
- **年份**: 格式化为文本字符串（例如，"2024" 而非 "2,024"）
- **货币**: 使用 $#,##0 格式；始终在标题中指定单位（"收入 ($mm)"）
- **零**: 使用数字格式使所有零显示为 "-"，包括百分比（例如，"$#,##0;($#,##0);-"）
- **百分比**: 默认为 0.0% 格式（一位小数）
- **倍数**: 格式化为 0.0x 用于估值倍数（EV/EBITDA、P/E）
- **负数**: 使用括号 (123) 而非减号 -123

### 公式构建规则

#### 假设位置
- 将所有假设（增长率、利润率、倍数等）放在单独的假设单元格中
- 在公式中使用单元格引用而非硬编码值
- 示例：使用 =B5*(1+$B$6) 而非 =B5*1.05

#### 公式错误预防
- 验证所有单元格引用是否正确
- 检查范围中的偏移错误
- 确保所有预测期的公式一致
- 用边界情况测试（零值、负数）
- 验证无意外的循环引用

#### 硬编码文档要求
- 注释或在单元格旁边（如果在表末）。格式："来源: [系统/文档], [日期], [具体参考], [适用的 URL]"
- 示例：
  - "来源: 公司 10-K, FY2024, 第 45 页, 收入说明, [SEC EDGAR URL]"
  - "来源: 公司 10-Q, Q2 2025, 附表 99.1, [SEC EDGAR URL]"
  - "来源: 彭博终端, 2025年8月15日, AAPL US Equity"
  - "来源: FactSet, 2025年8月20日, 共识估计筛选"

# XLSX 创建、编辑和分析

## 概述

用户可能要求您创建、编辑或分析 .xlsx 文件的内容。您有不同的工具和工作流程可用于不同任务。

## 重要要求

**公式重新计算需要 LibreOffice**: 您可以假设已安装 LibreOffice，使用 `recalc.py` 脚本重新计算公式值。该脚本在首次运行时自动配置 LibreOffice

## 读取和分析数据

### 使用 pandas 进行数据分析
对于数据分析、可视化和基本操作，使用 **pandas**，它提供强大的数据操作功能：

```python
import pandas as pd

# 读取 Excel
df = pd.read_excel('file.xlsx')  # 默认：第一张工作表
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # 所有工作表作为字典

# 分析
df.head()      # 预览数据
df.info()      # 列信息
df.describe()  # 统计信息

# 写入 Excel
df.to_excel('output.xlsx', index=False)
```

## Excel 文件工作流程

## 关键：使用公式，而非硬编码值

**始终使用 Excel 公式而非在 Python 中计算值并硬编码。** 这确保电子表格保持动态和可更新。

### ❌ 错误 - 硬编码计算值
```python
# 错误：在 Python 中计算并硬编码结果
total = df['Sales'].sum()
sheet['B10'] = total  # 硬编码 5000

# 错误：在 Python 中计算增长率
growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth  # 硬编码 0.15

# 错误：Python 计算平均值
avg = sum(values) / len(values)
sheet['D20'] = avg  # 硬编码 42.5
```

### ✅ 正确 - 使用 Excel 公式
```python
# 正确：让 Excel 计算总和
sheet['B10'] = '=SUM(B2:B9)'

# 正确：增长率作为 Excel 公式
sheet['C5'] = '=(C4-C2)/C2'

# 正确：使用 Excel 函数计算平均值
sheet['D20'] = '=AVERAGE(D2:D19)'
```

这适用于所有计算 - 总计、百分比、比率、差值等。当源数据更改时，电子表格应该能够重新计算。

## 常见工作流程
1. **选择工具**: pandas 用于数据，openpyxl 用于公式/格式化
2. **创建/加载**: 创建新工作簿或加载现有文件
3. **修改**: 添加/编辑数据、公式和格式
4. **保存**: 写入文件
5. **重新计算公式（使用公式时强制要求）**: 使用 recalc.py 脚本
   ```bash
   python recalc.py output.xlsx
   ```
6. **验证和修复任何错误**:
   - 脚本返回带有错误详情的 JSON
   - 如果 `status` 为 `errors_found`，检查 `error_summary` 了解具体的错误类型和位置
   - 修复已识别的错误并重新计算
   - 需要修复的常见错误：
     - `#REF!`: 无效的单元格引用
     - `#DIV/0!`: 除以零
     - `#VALUE!`: 公式中的错误数据类型
     - `#NAME?`: 公式名称无法识别

### 创建新的 Excel 文件

```python
# 使用 openpyxl 处理公式和格式化
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# 添加数据
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# 添加公式
sheet['B2'] = '=SUM(A1:A10)'

# 格式化
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# 列宽
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

### 编辑现有 Excel 文件

```python
# 使用 openpyxl 保留公式和格式化
from openpyxl import load_workbook

# 加载现有文件
wb = load_workbook('existing.xlsx')
sheet = wb.active  # 或用于特定工作表的 wb['SheetName']

# 处理多个工作表
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"工作表: {sheet_name}")

# 修改单元格
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # 在位置 2 插入行
sheet.delete_cols(3)  # 删除第 3 列

# 添加新工作表
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```

## 重新计算公式

openpyxl 创建或修改的 Excel 文件包含公式字符串但不包含计算值。使用提供的 `recalc.py` 脚本重新计算公式：

```bash
python recalc.py <excel_file> [timeout_seconds]
```

示例：
```bash
python recalc.py output.xlsx 30
```

该脚本：
- 首次运行时自动设置 LibreOffice 宏
- 重新计算所有工作表中的所有公式
- 扫描所有单元格的 Excel 错误（#REF!、#DIV/0! 等）
- 返回带有详细错误位置和计数的 JSON
- 在 Linux 和 macOS 上均可工作

## 公式验证清单

确保公式正确工作的快速检查：

### 基本验证
- [ ] **测试 2-3 个样本引用**: 在构建完整模型前验证它们提取正确的值
- [ ] **列映射**: 确认 Excel 列匹配（例如，第 64 列 = BL，而非 BK）
- [ ] **行偏移**: 记住 Excel 行是 1 索引的（DataFrame 第 5 行 = Excel 第 6 行）

### 常见陷阱
- [ ] **NaN 处理**: 使用 `pd.notna()` 检查空值
- [ ] **最右侧列**: FY 数据通常在第 50+ 列
- [ ] **多重匹配**: 搜索所有出现，而不仅是最先出现的
- [ ] **除以零**: 在公式中使用 `/` 前检查分母（#DIV/0!）
- [ ] **错误引用**: 验证公式中引用的所有单元格都指向预期单元格（#REF!）
- [ ] **跨表引用**: 使用正确格式（Sheet1!A1）链接工作表

### 公式测试策略
- [ ] **从小开始**: 在广泛应用前测试 2-3 个单元格的公式
- [ ] **验证依赖项**: 检查公式中引用的所有单元格是否存在
- [ ] **测试边界情况**: 包括零、负数和非常大的值

### 解释 recalc.py 输出
脚本返回带有错误详情的 JSON：
```json
{
  "status": "success",           // 或 "errors_found"
  "total_errors": 0,              // 总错误计数
  "total_formulas": 42,           // 文件中的公式数量
  "error_summary": {              // 仅在发现错误时存在
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

## 最佳实践

### 库选择
- **pandas**: 最适合数据分析、批量操作和简单数据导出
- **openpyxl**: 最适合复杂格式化、公式和 Excel 特定功能

### 使用 openpyxl
- 单元格索引是 1 基的（row=1, column=1 指向单元格 A1）
- 使用 `data_only=True` 读取计算值：`load_workbook('file.xlsx', data_only=True)`
- **警告**: 如果用 `data_only=True` 打开并保存，公式将被值替换并永久丢失
- 对于大文件：读取时使用 `read_only=True` 或写入时使用 `write_only=True`
- 公式保留但不评估 - 使用 recalc.py 更新值

### 使用 pandas
- 指定数据类型以避免推断问题：`pd.read_excel('file.xlsx', dtype={'id': str})`
- 对于大文件，读取特定列：`pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- 正确处理日期：`pd.read_excel('file.xlsx', parse_dates=['date_column'])`

## 代码风格指南
**重要**: 生成 Excel 操作的 Python 代码时：
- 编写简洁、简洁的 Python 代码，避免不必要的注释
- 避免冗长的变量名和冗余操作
- 避免不必要的打印语句

**对于 Excel 文件本身**:
- 为包含复杂公式或重要假设的单元格添加注释
- 记录硬编码值的数据来源
- 为关键计算和模型部分包含注释