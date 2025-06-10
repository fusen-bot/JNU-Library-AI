# 📚 书籍搜索跳转功能测试指南

## 🎯 功能概述

新增的书籍搜索跳转功能允许用户：
1. **悬停查看详情** - 鼠标悬停在推荐书籍上查看详细推荐理由
2. **点击跳转搜索** - 点击书籍直接在图书馆系统中搜索该书籍
3. **自动测试收集** - 全程记录用户交互和系统响应用于优化

## 🚀 如何开始测试

### 第一步：启动系统
```bash
# 在项目根目录执行
./start_services.sh
```

### 第二步：访问图书馆网站
打开浏览器，访问 `https://opac.jiangnan.edu.cn/#/Home`

### 第三步：输入搜索关键词
在搜索框中输入任意关键词（如"计算机"、"数据结构"等）

## 🧪 测试功能说明

### 自动测试工具
系统自动加载了测试脚本，提供以下全局函数：

#### 基础测试函数
```javascript
// 1. 检测页面元素
testPageElements()

// 2. 模拟点击书籍（随机选择）
testBookClick()

// 3. 模拟点击指定书籍
testBookClick("计算机系统")

// 4. 测试搜索功能
testSearchFunction("算法导论")

// 5. 生成测试报告
getTestReport()

// 6. 清除测试数据
clearTestData()
```

#### 快捷键操作
- **Ctrl + Shift + T**: 执行完整测试套件
- **Ctrl + Shift + R**: 生成并显示测试报告
- **Ctrl + Shift + C**: 清除所有测试数据

### 手动测试步骤

#### 1. 基础功能测试
1. 在搜索框输入关键词（至少3个字符）
2. 等待推荐书籍显示
3. 观察书籍项是否显示🔍图标
4. 鼠标悬停书籍项，查看是否显示"点击搜索"提示

#### 2. 悬停详情测试
1. 将鼠标悬停在任意推荐书籍上
2. 检查是否显示详细推荐理由面板
3. 验证面板包含：
   - 🧠 推荐依据部分
   - 👥 借阅热度部分
   - 📊 各学院借阅率

#### 3. 点击跳转测试
1. 点击任意推荐书籍
2. 观察浏览器控制台输出
3. 检查是否触发搜索操作
4. 验证推荐面板是否自动隐藏

## 📊 测试数据收集

### 事件记录
系统会自动记录以下事件：
- 📚 书籍点击事件
- 🔍 搜索尝试事件
- ✅ 搜索成功事件
- ❌ 搜索失败事件
- 🌐 URL跳转事件

### 查看测试数据
在浏览器控制台执行：
```javascript
// 查看所有收集的事件
console.table(window.__testSearchEvents)

// 生成详细报告
const report = getTestReport()
console.log(report)
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 书籍不可点击
**症状**: 鼠标悬停无🔍图标，点击无反应
**解决**: 
```javascript
// 检查页面元素
testPageElements()
// 查看 bookItems 部分是否有数据
```

#### 2. 搜索跳转失败
**症状**: 点击书籍后无搜索动作
**解决**:
```javascript
// 检查搜索函数
debugLibraryElements()
// 查看是否找到搜索输入框和按钮
```

#### 3. 推荐理由不显示
**症状**: 悬停无详情面板
**解决**: 检查书籍数据是否包含 `logical_reason` 和 `social_reason`

## 📈 测试报告分析

### 报告结构
```javascript
{
  testSession: {
    startTime: "开始时间",
    endTime: "结束时间", 
    duration: "测试时长"
  },
  summary: {
    totalTestActions: "总测试动作数",
    totalSearchEvents: "总搜索事件数",
    clickTests: "点击测试次数",
    errors: "错误次数"
  },
  recommendations: [
    // 改进建议
  ]
}
```

### 关键指标
- **点击成功率** = 成功搜索次数 / 总点击次数
- **搜索响应率** = 找到搜索按钮次数 / 搜索尝试次数
- **用户交互率** = 有交互的书籍数 / 总推荐书籍数

## 🎨 UI交互效果

### 视觉反馈
1. **悬停效果**: 书籍项向上浮起，显示阴影
2. **点击反馈**: 短暂缩放动画 + 绿色闪烁
3. **加载状态**: 旋转loading图标
4. **完成状态**: 绿色对勾图标

### 用户提示
- 🔍 搜索图标（悬停时显示）
- "点击搜索" 文字提示
- 详细推荐理由面板

## 🚨 注意事项

### 浏览器兼容性
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ⚠️ IE 不支持

### 性能考虑
- 搜索防抖: 500ms
- 面板隐藏延迟: 100ms
- 自动测试间隔: 30秒

### 数据隐私
- 测试数据仅存储在浏览器内存中
- 页面刷新后自动清除
- 不向外部发送个人数据

## 📞 技术支持

### 调试指令
```javascript
// 启用详细日志
window.__debugMode = true

// 查看当前状态
console.log({
  testEvents: window.__testSearchEvents?.length || 0,
  hasSearchFunction: typeof window.searchBookInLibrary === 'function',
  bookItems: document.querySelectorAll('.book-item').length
})
```

### 联系方式
如遇到技术问题或需要功能改进建议，请：
1. 生成测试报告: `getTestReport()`
2. 截图保存控制台输出
3. 记录复现步骤

---

🎉 **测试愉快！您的反馈将帮助我们不断改进用户体验！** 