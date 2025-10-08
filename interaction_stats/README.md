# 江南大学图书馆交互数据分析工具

这是一个独立的可视化分析工具，用于分析江南大学图书馆OPAC系统的用户交互数据。支持全局连续的被试ID管理和实验数据分析。

## 功能特性

- 📊 **多维度数据分析**: 支持单会话和多会话汇总分析
- 📈 **丰富的可视化图表**: 饼图、柱状图、时间线图表
- 📁 **文件上传支持**: 直接上传JSONL格式的会话文件
- 🔄 **实时数据处理**: 动态解析和分析交互事件
- 📱 **响应式界面**: 支持桌面和移动设备
- 🚀 **独立运行**: 无需复杂配置，开箱即用
- 🆔 **全局连续ID**: 支持被试_001, 被试_002等全局连续ID格式
- 👤 **被试管理**: 支持被试姓名和实验描述管理

## 快速开始

### 方法一：使用启动脚本（推荐）

```bash
# 进入工具目录
cd interaction_stats

# 运行启动脚本
./run-analyzer.sh

# 或者指定端口
./run-analyzer.sh -p 8081
```

启动脚本会自动：
- 检查运行环境
- 构建应用（如果有Node.js）
- 启动HTTP服务器
- 打开浏览器

### 方法二：手动启动

```bash
# 进入工具目录
cd interaction_stats

# 启动HTTP服务器
python -m http.server 8081

# 在浏览器中访问
open http://localhost:8081
```

### 方法三：使用Node.js（开发环境）

```bash
# 安装依赖
npm install

# 构建并启动
npm run dev
```

## 使用说明

### 1. 数据收集

#### 手动控制实验会话

使用终端控制器管理被试实验：

```bash
# 开始被试实验
python session_controller.py start "张三" "研究机器学习相关书籍"

# 结束被试实验
python session_controller.py end "实验完成"

# 查看当前状态
python session_controller.py status

# 重置全局计数器（谨慎使用）
python session_controller.py reset
```

#### ID生成规则

- **全局连续ID**: `被试_001`, `被试_002`, `被试_003`...
- **跨天连续**: 不管哪天，ID都连续递增，不会重置
- **自动分配**: 每次开始新实验时自动分配下一个可用ID

### 2. 上传数据文件

1. 在浏览器中打开分析工具
2. 点击"上传会话文件"按钮
3. 选择 `sessions/` 目录下的 `.jsonl` 文件
4. 支持同时上传多个文件
5. 支持新的被试ID格式和传统格式

### 3. 分析模式

#### 单会话分析
- 查看单个会话的详细交互数据
- 包含完整的时间线和事件详情
- 适合深入分析特定用户行为

#### 多会话汇总
- 汇总所有已上传会话的统计数据
- 展示整体用户行为趋势
- 适合宏观数据分析

### 4. 功能面板

#### 会话管理
- 查看所有已加载的会话
- 快速切换和选择会话
- 显示会话基本信息

#### 数据总览
- 核心统计指标卡片
- 事件类型分布图
- 热门图书交互图表

#### 图书交互
- 已点击图书列表
- 详细交互统计表格
- 悬停时间和点击数据

#### 时间线
- 交互事件时间序列图
- 详细事件列表
- 用户行为流程分析

## 数据格式

工具支持标准的JSONL格式会话文件，每行包含一个JSON事件：

### 新的被试实验格式

```json
{
  "session_id": "被试_001",
  "event_type": "participant_experiment_start",
  "timestamp": "2025-01-15T14:17:37.544Z",
  "timestamp_since_session_start": 0,
  "participant_id": "被试_001",
  "participant_name": "张三",
  "experiment_description": "研究机器学习相关书籍",
  "search_id": "experiment_1705316257544_abc123"
}
```

### 传统交互格式

```json
{
  "session_id": "交互_01_20250928",
  "event_type": "book_clicked",
  "timestamp": "2025-09-28T14:17:37.544Z",
  "timestamp_since_session_start": 13070,
  "book_title": "人工智能与未来教育",
  "book_author": "潘巧明",
  "book_isbn": "9787301339381"
}
```

### 支持的事件类型

#### 被试实验事件
- `participant_experiment_start` - 被试实验开始
- `participant_experiment_end` - 被试实验结束
- `manual_search_session_start` - 手动搜索会话开始
- `manual_search_session_end` - 手动搜索会话结束

#### 传统交互事件
- `session_start` - 会话开始
- `session_end` - 会话结束
- `book_hover_start` - 开始悬停图书
- `book_hover_end` - 结束悬停图书
- `book_clicked` - 点击图书
- `page_hidden` - 页面隐藏
- `page_visible` - 页面显示
- `heartbeat` - 心跳检测

## 技术架构

### 前端技术栈
- **React 18**: 现代化UI框架
- **TypeScript**: 类型安全
- **Recharts**: 数据可视化
- **Tailwind CSS**: 响应式样式
- **Lucide React**: 图标库

### 数据处理
- **SessionDataLoader**: 会话数据解析器
- **实时分析**: 动态统计计算
- **内存缓存**: 高效数据管理

### 构建工具
- **ESBuild**: 快速构建
- **TypeScript编译**: 类型检查
- **模块化架构**: 易于维护

## 开发指南

### 项目结构

```
interaction_stats/
├── index.html              # 主页面
├── standalone-app.tsx      # 应用入口
├── interaction-dashboard.tsx # 主面板组件
├── session-data-loader.ts  # 数据加载器
├── styles.css              # 样式文件
├── package.json            # 项目配置
├── tsconfig.json           # TypeScript配置
├── run-analyzer.sh         # 启动脚本
├── README.md               # 说明文档
└── sessions/               # 会话数据目录
    ├── 被试_001.jsonl      # 新的全局连续ID格式
    ├── 被试_002.jsonl
    ├── 被试_003.jsonl
    ├── 交互_01_20250928.jsonl  # 传统格式（向后兼容）
    ├── 交互_02_20250928.jsonl
    └── ...
```

### 本地开发

```bash
# 克隆项目
git clone <repository-url>
cd interaction_stats

# 安装依赖
npm install

# 类型检查
npm run type-check

# 构建应用
npm run build

# 启动开发服务器
npm run dev
```

### 添加新功能

1. **扩展事件类型**: 在 `SessionEvent` 接口中添加新字段
2. **添加图表类型**: 在面板组件中增加新的可视化图表
3. **增强数据分析**: 在 `SessionDataLoader` 中添加新的统计方法
4. **优化UI组件**: 使用 Tailwind CSS 快速开发响应式界面
5. **支持新ID格式**: 确保分析工具支持新的被试ID格式

## 部署说明

### 生产环境部署

1. **构建应用**:
```bash
npm run build
```

2. **部署文件**:
将整个 `interaction_stats` 目录部署到Web服务器

3. **配置服务器**:
确保服务器支持静态文件服务和JSONL文件类型

### Docker部署

```dockerfile
FROM nginx:alpine
COPY interaction_stats/ /usr/share/nginx/html/
EXPOSE 80
```

## 性能优化

- **懒加载**: 大文件分批处理
- **虚拟化**: 大列表虚拟滚动
- **缓存策略**: 智能数据缓存
- **响应式设计**: 移动端优化

## 故障排除

### 常见问题

1. **上传文件失败**
   - 检查文件格式是否为JSONL
   - 确认文件大小不超过浏览器限制
   - 验证JSON格式是否正确
   - 确认ID格式支持（被试_001 或 交互_XX_YYYYMMDD）

2. **图表显示异常**
   - 刷新页面重新加载
   - 检查数据是否包含必要字段
   - 确认浏览器支持现代JavaScript
   - 验证事件类型是否被正确识别

3. **性能问题**
   - 减少同时加载的会话数量
   - 使用Chrome开发者工具分析性能
   - 考虑数据分批处理

4. **ID格式问题**
   - 确认使用正确的ID格式：`被试_001` 或 `交互_XX_YYYYMMDD`
   - 检查文件名是否与session_id匹配
   - 验证全局计数器是否正确递增

### 调试模式

在浏览器控制台中启用调试：

```javascript
// 查看加载的会话数据
console.log(window.sessionDataLoader?.getAllSessions());

// 查看组合统计
console.log(window.sessionDataLoader?.getCombinedStats());

// 查看被试实验数据
console.log(window.sessionDataLoader?.getAllSessions().filter(s => s.sessionInfo.sessionId.startsWith('被试_')));
```

### 实验管理

#### 使用终端控制器

```bash
# 查看帮助
python session_controller.py help

# 开始被试实验
python session_controller.py start "张三" "研究机器学习相关书籍"

# 查看当前状态
python session_controller.py status

# 结束实验
python session_controller.py end "实验完成"

# 重置计数器（谨慎使用）
python session_controller.py reset
```

#### 浏览器控制台调试

```javascript
// 查看当前会话状态
getCurrentSessionStatus()

// 手动开始被试实验
manualStartParticipantSession('张三', '研究机器学习相关书籍')

// 手动结束实验
manualEndParticipantSession('实验完成')

// 重置全局计数器
resetGlobalParticipantCounter()
```

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交Pull Request

## 许可证

MIT License - 详见 LICENSE 文件

## 联系我们

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues Page]
- 技术支持: 江南大学图书馆技术团队

---

**注意**: 本工具仅用于教育和研究目的，请确保遵守相关数据隐私和使用政策。
