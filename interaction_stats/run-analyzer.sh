#!/bin/bash

# 江南大学图书馆交互数据分析工具启动脚本
# 用于快速启动独立的可视化分析面板

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="江南大学图书馆交互数据分析工具"
DEFAULT_PORT=8081
BROWSER_OPEN=true

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_info() {
    print_message $BLUE "[信息] $1"
}

print_success() {
    print_message $GREEN "[成功] $1"
}

print_warning() {
    print_message $YELLOW "[警告] $1"
}

print_error() {
    print_message $RED "[错误] $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查运行环境..."
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "未找到 Python 环境，请安装 Python 3.6+"
        exit 1
    fi
    
    print_success "Python 环境检查通过: $($PYTHON_CMD --version)"
    
    # 检查 Node.js (可选，用于构建)
    if command -v node &> /dev/null; then
        print_success "Node.js 环境检查通过: $(node --version)"
        HAS_NODE=true
    else
        print_warning "未找到 Node.js 环境，将使用简化模式运行"
        HAS_NODE=false
    fi
}

# 构建应用 (如果有 Node.js)
build_app() {
    if [ "$HAS_NODE" = true ] && [ -f "$SCRIPT_DIR/package.json" ]; then
        print_info "检测到 Node.js 环境，开始构建应用..."
        
        cd "$SCRIPT_DIR"
        
        # 检查是否已安装依赖
        if [ ! -d "node_modules" ]; then
            print_info "安装 Node.js 依赖..."
            npm install
        fi
        
        # 构建应用
        print_info "构建 TypeScript 文件..."
        npm run build:bundle 2>/dev/null || {
            print_warning "构建失败，将使用预构建版本"
            return 1
        }
        
        print_success "应用构建完成"
    else
        print_info "使用预构建版本运行"
    fi
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 1
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -an | grep ":$port " | grep LISTEN >/dev/null 2>&1; then
            return 1
        fi
    fi
    return 0
}

# 查找可用端口
find_available_port() {
    local port=$DEFAULT_PORT
    while ! check_port $port; do
        print_warning "端口 $port 已被占用，尝试下一个端口..."
        ((port++))
        if [ $port -gt 9000 ]; then
            print_error "无法找到可用端口 (尝试范围: $DEFAULT_PORT-9000)"
            exit 1
        fi
    done
    echo $port
}

# 启动服务器
start_server() {
    local port=$(find_available_port)
    
    print_info "启动 HTTP 服务器在端口 $port..."
    
    cd "$SCRIPT_DIR"
    
    # 创建服务器启动命令
    local server_cmd="$PYTHON_CMD -m http.server $port"
    
    print_success "服务器启动成功!"
    print_info "访问地址: http://localhost:$port"
    print_info "数据文件目录: $SCRIPT_DIR/sessions/"
    print_info ""
    print_info "使用说明:"
    print_info "1. 在浏览器中打开上述地址"
    print_info "2. 点击'上传会话文件'按钮"
    print_info "3. 选择 sessions/ 目录下的 .jsonl 文件"
    print_info "4. 开始分析交互数据"
    print_info ""
    print_warning "按 Ctrl+C 停止服务器"
    
    # 尝试自动打开浏览器
    if [ "$BROWSER_OPEN" = true ]; then
        sleep 2
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:$port" 2>/dev/null &
        elif command -v open &> /dev/null; then
            open "http://localhost:$port" 2>/dev/null &
        elif command -v start &> /dev/null; then
            start "http://localhost:$port" 2>/dev/null &
        else
            print_info "请手动在浏览器中打开: http://localhost:$port"
        fi
    fi
    
    # 启动服务器
    exec $server_cmd
}

# 显示帮助信息
show_help() {
    cat << EOF
$PROJECT_NAME 启动脚本

用法: $0 [选项]

选项:
  -p, --port PORT     指定服务器端口 (默认: $DEFAULT_PORT)
  -n, --no-browser    不自动打开浏览器
  -h, --help          显示此帮助信息
  --build-only        仅构建，不启动服务器
  --check-only        仅检查环境，不启动服务器

示例:
  $0                  # 使用默认设置启动
  $0 -p 8090          # 在端口 8090 启动
  $0 -n               # 启动但不打开浏览器
  $0 --build-only     # 仅构建应用

环境要求:
  - Python 3.6+ (必需)
  - Node.js 16+ (可选，用于构建)

数据文件:
  将 .jsonl 格式的会话文件放在 sessions/ 目录下，
  然后通过 Web 界面上传进行分析。

EOF
}

# 清理函数
cleanup() {
    print_info "正在清理..."
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            DEFAULT_PORT="$2"
            shift 2
            ;;
        -n|--no-browser)
            BROWSER_OPEN=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 主流程
main() {
    print_success "=== $PROJECT_NAME ==="
    print_info "工作目录: $SCRIPT_DIR"
    echo
    
    # 检查依赖
    check_dependencies
    echo
    
    if [ "$CHECK_ONLY" = true ]; then
        print_success "环境检查完成"
        exit 0
    fi
    
    # 构建应用
    build_app
    echo
    
    if [ "$BUILD_ONLY" = true ]; then
        print_success "构建完成"
        exit 0
    fi
    
    # 启动服务器
    start_server
}

# 运行主流程
main
