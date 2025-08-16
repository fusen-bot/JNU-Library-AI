# Docker 镜像迁移指南

## 镜像信息
- **Docker Hub仓库**: `sendevelopmentcoding/library-test`
- **可用标签**: `latest`, `v1.0`
- **本地导出文件**: `jnu-library-ai.tar` (1.2GB)
- **导出时间**: 2024年8月14日

## 在目标电脑上复刻环境

### 方法一：从Docker Hub拉取（推荐）

```bash
# 拉取最新版本
docker pull sendevelopmentcoding/library-test:latest

# 或者拉取特定版本
docker pull sendevelopmentcoding/library-test:v1.0

# 验证镜像是否拉取成功
docker images | grep library-test
```

### 方法二：使用本地导出文件

#### 1. 传输文件
将 `jnu-library-ai.tar` 文件传输到目标电脑。

#### 2. 导入Docker镜像
在目标电脑上执行以下命令：

```bash
# 导入Docker镜像
docker load -i jnu-library-ai.tar

# 验证镜像是否导入成功
docker images | grep jnu-library-ai
```

### 3. 运行容器

#### 如果使用Docker Hub镜像：
```bash
# 运行容器
docker run -d \
  --name jnu-library-ai \
  -p 5001:5001 \
  -v $(pwd)/interaction_stats:/app/interaction_stats \
  sendevelopmentcoding/library-test:latest
```

#### 如果使用本地镜像：
```bash
# 运行容器
docker run -d \
  --name jnu-library-ai \
  -p 5001:5001 \
  -v $(pwd)/interaction_stats:/app/interaction_stats \
  jnu-library-ai:latest
```

### 4. 使用docker-compose（推荐）
如果您有 `docker-compose.yml` 文件，也可以使用：

```bash
# 确保docker-compose.yml文件在同一目录
docker-compose up -d
```

## 验证部署
1. 访问 `http://localhost:5001` 检查应用是否正常运行
2. 检查容器状态：`docker ps`
3. 查看容器日志：`docker logs jnu-library-ai`

## 注意事项
- 确保目标电脑已安装Docker
- 端口5001需要在目标电脑上可用
- 如果需要持久化数据，请确保挂载了正确的卷
- 镜像大小约1.2GB，传输时请考虑网络带宽

## 故障排除
如果遇到问题，可以：
1. 检查Docker服务状态：`docker info`
2. 查看详细日志：`docker logs -f jnu-library-ai`
3. 进入容器调试：`docker exec -it jnu-library-ai /bin/bash`
