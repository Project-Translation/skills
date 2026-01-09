from playwright.sync_api import sync_playwright

# 示例：浏览器自动化期间捕获控制台日志

url = 'http://localhost:5173'  # 替换为您的 URL

console_logs = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})

    # 设置控制台日志捕获
    def handle_console_message(msg):
        console_logs.append(f"[{msg.type}] {msg.text}")
        print(f"控制台: [{msg.type}] {msg.text}")

    page.on("console", handle_console_message)

    # 导航到页面
    page.goto(url)
    page.wait_for_load_state('networkidle')

    # 与页面交互（触发控制台日志）
    page.click('text=仪表板')
    page.wait_for_timeout(1000)

    browser.close()

# 将控制台日志保存到文件
with open('/mnt/user-data/outputs/console.log', 'w') as f:
    f.write('\n'.join(console_logs))

print(f"\n捕获到 {len(console_logs)} 条控制台消息")
print(f"日志已保存到: /mnt/user-data/outputs/console.log")