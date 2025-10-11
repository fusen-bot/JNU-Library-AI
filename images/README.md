# 效果展示图片说明

这个文件夹用于存放项目的效果展示图片，帮助用户更好地理解系统功能。

## 需要的图片文件

### 1. 系统运行效果 (system-demo.png)
- **内容**: 浏览器运行时的完整界面截图
- **建议尺寸**: 1200x800 像素
- **说明**: 显示浏览器打开目标网页，可以看到输入框和系统运行状态

### 2. 智能建议界面 (suggestion-demo.png)
- **内容**: 用户输入时显示的智能建议弹窗
- **建议尺寸**: 600x400 像素
- **说明**: 展示AI生成的建议关键词和推荐理由

### 3. 交互统计面板 (stats-dashboard.png)
- **内容**: 数据分析面板的截图
- **建议尺寸**: 1200x600 像素
- **说明**: 显示用户交互统计、搜索历史等数据可视化界面

## 如何生成这些图片

### 方法1: 手动截图
1. 启动系统：`python web_monitor.py`
2. 在浏览器中进行以下操作：
   - 打开目标网页
   - 在搜索框输入关键词
   - 观察智能建议的显示
   - 访问交互统计面板
3. 使用系统截图工具保存图片到 `images/` 文件夹

### 方法2: 自动化截图脚本
可以使用Selenium自动化截图：

```python
from selenium import webdriver
import time

# 启动浏览器
driver = webdriver.Chrome()
driver.get("http://localhost:3000")

# 截图保存
driver.save_screenshot("images/system-demo.png")

# 输入内容触发建议
search_box = driver.find_element_by_id("search-input")
search_box.send_keys("机器学习")
time.sleep(2)  # 等待建议生成
driver.save_screenshot("images/suggestion-demo.png")

driver.quit()
```

### 方法3: 使用专业工具
- **LICEcap**: 制作GIF动图展示交互过程
- **OBS Studio**: 录制演示视频
- **Snagit**: 专业截图和标注工具

## 图片优化建议

1. **压缩图片**: 使用工具如 `tinypng.com` 压缩图片大小
2. **统一风格**: 保持截图的风格一致，使用相同的浏览器主题
3. **添加标注**: 可以在图片上添加箭头或文字说明重点功能
4. **多语言支持**: 如果需要支持多语言，可以准备不同语言版本的截图

## 注意事项

- 确保截图中的内容不包含敏感信息
- 图片文件名使用英文，避免中文字符
- 建议同时提供PNG和WebP格式以提高加载速度
- 定期更新截图以反映最新的界面变化
