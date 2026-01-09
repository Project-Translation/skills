---
name: webapp-testing
description: 使用 Playwright 与本地 Web 应用交互和测试的工具包。支持验证前端功能、调试 UI 行为、捕获浏览器截图和查看浏览器日志。
license: LICENSE.txt 中的完整条款
---

# Web 应用测试

要测试本地 Web 应用，请编写原生 Python Playwright 脚本。

**可用的辅助脚本**：
- `scripts/with_server.py` - 管理服务器生命周期（支持多个服务器）

**始终首先使用 `--help` 运行脚本** 以查看用法。除非您尝试运行脚本后发现绝对需要自定义解决方案，否则不要阅读源代码。这些脚本可能非常大，从而污染您的上下文窗口。它们的存在是为了作为黑盒脚本直接调用，而不是被吸收到您的上下文窗口中。

## 决策树：选择您的方法

```
用户任务 → 是否是静态 HTML？
    ├─ 是 → 直接读取 HTML 文件以识别选择器
    │         ├─ 成功 → 使用选择器编写 Playwright 脚本
    │         └─ 失败/不完整 → 视为动态（如下）
    │
    └─ 否（动态 Web 应用）→ 服务器是否已在运行？
        ├─ 否 → 运行：python scripts/with_server.py --help
        │        然后使用辅助工具 + 编写简化的 Playwright 脚本
        │
        └─ 是 → 侦察然后行动：
            1. 导航并等待网络空闲
            2. 截图或检查 DOM
            3. 从渲染状态识别选择器
            4. 使用发现的选择器执行操作
```

## 示例：使用 with_server.py

要启动服务器，首先运行 `--help`，然后使用辅助工具：

**单个服务器**：
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**多个服务器（例如，后端 + 前端）**：
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

要创建自动化脚本，仅包含 Playwright 逻辑（服务器会自动管理）：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # 始终以无头模式启动 chromium
    page = browser.new_page()
    page.goto('http://localhost:5173') # 服务器已运行并就绪
    page.wait_for_load_state('networkidle') # 至关重要：等待 JS 执行
    # ... 您的自动化逻辑
    browser.close()
```

## 侦察然后行动模式

1. **检查渲染的 DOM**：
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **从检查结果中识别选择器**

3. **使用发现的选择器执行操作**

## 常见陷阱

❌ **不要** 在动态应用上等待 `networkidle` 之前检查 DOM
✅ **应该** 在检查之前等待 `page.wait_for_load_state('networkidle')`

## 最佳实践

- **将捆绑脚本用作黑盒** - 为了完成任务，请考虑 `scripts/` 中可用的脚本是否可以提供帮助。这些脚本处理常见的复杂工作流，无需使上下文窗口混乱即可可靠地运行。使用 `--help` 查看用法，然后直接调用。
- 在同步脚本中使用 `sync_playwright()`
- 完成后始终关闭浏览器
- 使用描述性选择器：`text=`、`role=`、CSS 选择器或 ID
- 添加适当的等待：`page.wait_for_selector()` 或 `page.wait_for_timeout()`

## 参考文件

- **examples/** - 展示常见模式的示例：
  - `element_discovery.py` - 发现页面上的按钮、链接和输入
  - `static_html_automation.py` - 为本地 HTML 使用 file:// URL
  - `console_logging.py` - 在自动化期间捕获控制台日志