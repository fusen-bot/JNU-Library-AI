# Docker部署指南

## 🐳 Docker部署步骤【目前暂未启用】

### 1. 准备API密钥
首先，你需要准备相应的API密钥：

```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，填入你的API密钥
nano .env
```

### 2. 构建并启动服务

#### 方式一：使用Docker Compose（推荐）
```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d --build
```

#### 方式二：使用Docker命令
```bash
# 构建镜像
docker build -t jnu-library-ai .

# 运行容器
docker run -d \
  --name jnu-library-ai \
  -p 5001:5001 \
  --shm-size=2g \
  --cap-add=SYS_ADMIN \
  --security-opt seccomp=unconfined \
  -e DASHSCOPE_API_KEY=your_api_key_here \
  -v $(pwd)/interaction_stats:/app/interaction_stats \
  jnu-library-ai
```

### 3. 验证服务
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试API
curl http://localhost:5001/input -X POST \
  -H "Content-Type: application/json" \
  -d '{"value":"计算机"}'
```

## 🔧 配置说明

### 环境变量
- `API_BACKEND`: 选择API后端 (qwen/spark/openai)
- `DASHSCOPE_API_KEY`: 千问API密钥
- `OPENAI_API_KEY`: OpenAI API密钥  
- `SPARK_APP_ID/SPARK_API_KEY/SPARK_API_SECRET`: 星火API配置

### 端口映射
- 容器内端口：5001
- 主机端口：5001
- 访问地址：http://localhost:5001

### 数据持久化
- `./interaction_stats` 目录会被挂载到容器中，用于保存交互统计数据

## 🐛 故障排除

### Chrome相关问题
如果遇到Chrome启动问题，可以尝试：
```bash
# 增加共享内存
docker run --shm-size=2g ...

# 添加必要权限
docker run --cap-add=SYS_ADMIN --security-opt seccomp=unconfined ...
```

### 网络问题
如果无法访问外部网站：
```bash
# 检查网络连接
docker exec -it jnu-library-ai curl -I https://opac.jiangnan.edu.cn
```

### 查看详细日志
```bash
# 实时查看日志
docker-compose logs -f jnu-library-ai

# 进入容器调试
docker exec -it jnu-library-ai /bin/bash
```

## 📝 注意事项

1. **API密钥安全**：请妥善保管你的API密钥，不要提交到代码仓库
2. **资源消耗**：Chrome浏览器会消耗较多内存，建议至少分配2GB内存
3. **网络访问**：确保容器能访问目标网站和API服务
4. **权限设置**：Chrome需要特殊权限才能在容器中正常运行
