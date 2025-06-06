from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import threading
import requests
import logging
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from experimental_book_library import find_books_by_task

# ===========================================
# 异步任务管理
# ===========================================
# 全局任务存储，用于管理异步生成的推荐理由
async_tasks = {}
# 线程池执行器，用于处理异步LLM调用
executor = ThreadPoolExecutor(max_workers=3)

def cleanup_old_tasks():
    """
    清理超过1小时的旧任务，防止内存泄漏
    """
    current_time = time.time()
    tasks_to_remove = []
    
    for task_id, task in async_tasks.items():
        if current_time - task.get('created_at', 0) > 3600:  # 1小时
            tasks_to_remove.append(task_id)
    
    for task_id in tasks_to_remove:
        del async_tasks[task_id]
        logger.info(f"清理过期任务: {task_id}")

# 定期清理任务
def start_cleanup_timer():
    """
    启动定期清理定时器
    """
    cleanup_old_tasks()
    # 每30分钟清理一次
    timer = threading.Timer(1800, start_cleanup_timer)
    timer.daemon = True
    timer.start()

# ===========================================
# API 配置区域 - 在这里切换不同的后端API
# ===========================================
# 可选值: "spark" (星火API) 或 "qwen" (千问API) 或 "openai" (OpenAI API)
API_BACKEND = "spark"  # 修改这里来切换API

# 根据配置导入相应的API函数
if API_BACKEND == "spark":
    from spark import get_spark_suggestion as get_suggestion
    from spark import get_spark_books_with_reasons as get_books_with_reasons
    logger_name = "星火API"
elif API_BACKEND == "qwen":
    from qwen import get_qwen_suggestion as get_suggestion
    # from qwen import get_qwen_books_with_reasons as get_books_with_reasons  # 待实现
    logger_name = "千问API"
elif API_BACKEND == "openai":
    from openai import get_openai_suggestion as get_suggestion
    # from openai import get_openai_books_with_reasons as get_books_with_reasons  # 待实现
    logger_name = "OpenAI API"
else:
    raise ValueError(f"不支持的API后端: {API_BACKEND}，支持的选项: spark, qwen, openai")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info(f"当前使用的API后端: {logger_name}")

# Flask服务器，用于接收来自浏览器的请求
app = Flask(__name__)

# 配置CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://opac.jiangnan.edu.cn", "http://localhost:*", "http://127.0.0.1:*", "null"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# 添加CORS响应头
@app.after_request
def after_request(response):
    # 获取请求的Origin
    origin = request.headers.get('Origin')
    # 允许的origins列表
    allowed_origins = ['https://opac.jiangnan.edu.cn', 'null']
    # 如果Origin在允许列表中，或者是localhost/127.0.0.1，则设置对应的Origin
    if origin in allowed_origins or (origin and ('localhost' in origin or '127.0.0.1' in origin)):
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        # 默认允许null origin（用于本地文件测试）
        response.headers.add('Access-Control-Allow-Origin', 'null')
    
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# 在文件的开头添加一个全局变量来记录上次请求的时间
last_request_time = 0

# ===========================================
# 新增：数据契约定义 - 带推荐理由的书籍推荐 API
# ===========================================

def get_mock_books_with_reasons(user_query):
    """
    返回模拟的包含推荐理由的书籍数据
    这是新功能的数据契约定义
    """
    mock_data = {
        "status": "success",
        "user_query": user_query,
        "books": [
            {
                "title": "深入理解计算机系统",
                "author": "Randal E. Bryant, David R. O'Hallaron",
                "isbn": "9787111321312",
                "cover_url": "https://example.com/cover1.jpg",
                "logical_reason": {
                    "user_query_recap": f"用户搜索：{user_query}",
                    "ai_understanding": "用户希望深入理解计算机底层原理，包括硬件与软件的交互机制、内存管理和性能优化策略。",
                    "keyword_match": "本书通过详细讲解处理器架构、虚拟内存系统和系统级I/O，完美契合了用户对计算机底层机制的探索需求。"
                },
                "social_reason": {
                    "departments": [
                        {"name": "计算机科学与工程学院", "rate": 0.85},
                        {"name": "物联网工程学院", "rate": 0.72},
                        {"name": "理学院", "rate": 0.31},
                        {"name": "商学院", "rate": 0.12}
                    ],
                    "trend": "本书为我校工科类核心参考书，常年位居技术类书籍借阅榜首，尤其在考研和保研季借阅量激增，是计算机相关专业学生的必读经典。"
                }
            },
            {
                "title": "算法导论",
                "author": "Thomas H. Cormen, Charles E. Leiserson",
                "isbn": "9787111187776",
                "cover_url": "https://example.com/cover2.jpg",
                "logical_reason": {
                    "user_query_recap": f"用户搜索：{user_query}",
                    "ai_understanding": "用户需要系统性地学习算法设计与分析方法，提升编程思维和问题解决能力。",
                    "keyword_match": "作为算法领域的权威教材，本书提供了完整的算法理论体系和实践指导，与用户的学习目标高度匹配。"
                },
                "social_reason": {
                    "departments": [
                        {"name": "计算机科学与工程学院", "rate": 0.91},
                        {"name": "数字媒体学院", "rate": 0.68},
                        {"name": "理学院", "rate": 0.45},
                        {"name": "物联网工程学院", "rate": 0.76}
                    ],
                    "trend": "该书是算法竞赛和技术面试的热门参考书，借阅量在每年春招和秋招季节达到峰值，深受编程爱好者和求职学生青睐。"
                }
            },
            {
                "title": "Java核心技术",
                "author": "Cay S. Horstmann",
                "isbn": "9787111213826",
                "cover_url": "https://example.com/cover3.jpg",
                "logical_reason": {
                    "user_query_recap": f"用户搜索：{user_query}",
                    "ai_understanding": "用户想要掌握Java编程语言的核心概念和企业级开发技能，为就业或项目开发做准备。",
                    "keyword_match": "本书涵盖了Java语言的完整特性和最佳实践，为用户提供了从基础到高级的系统性学习路径。"
                },
                "social_reason": {
                    "departments": [
                        {"name": "计算机科学与工程学院", "rate": 0.83},
                        {"name": "商学院", "rate": 0.34},
                        {"name": "设计学院", "rate": 0.28},
                        {"name": "物联网工程学院", "rate": 0.67}
                    ],
                    "trend": "Java作为企业级开发的主流语言，这本书在实习季和毕业设计期间借阅火爆，是学生踏入软件开发行业的重要参考。"
                }
            }
        ]
    }
    return mock_data

# ===========================================
# 异步理由生成函数
# ===========================================

def generate_reasons_async(task_id, matched_books, user_query):
    """
    异步生成推荐理由的函数，在后台线程中运行
    """
    try:
        logger.info(f"任务 {task_id}: 开始异步生成推荐理由")
        # 更新任务状态为处理中
        async_tasks[task_id]['status'] = 'processing'
        async_tasks[task_id]['progress'] = '正在生成推荐理由...'
        
        # 调用原有的并行LLM生成理由函数
        response_data = get_books_with_reasons(matched_books, user_query)
        
        # 将结果存储到任务中
        async_tasks[task_id]['status'] = 'completed'
        async_tasks[task_id]['result'] = response_data
        async_tasks[task_id]['progress'] = '推荐理由生成完成'
        logger.info(f"任务 {task_id}: 推荐理由生成完成")
        
    except Exception as e:
        logger.error(f"任务 {task_id}: 生成推荐理由时发生错误: {str(e)}")
        async_tasks[task_id]['status'] = 'error'
        async_tasks[task_id]['error'] = str(e)
        async_tasks[task_id]['progress'] = '生成推荐理由失败'

@app.route('/api/books_with_reasons', methods=['POST'])
def get_books_with_reasons_api():
    """
    新的API端点：立即返回基本书籍信息，异步生成推荐理由
    第三阶段：快速响应 + 后台异步处理
    """
    try:
        data = request.json
        user_query = data.get('query', '')
        logger.info(f"收到书籍推荐请求: {user_query}")
        
        if not user_query or len(user_query.strip()) < 2:
            return jsonify({
                "status": "error", 
                "error": "查询内容不能为空且至少包含2个字符"
            }), 400
        
        # 第一步：从本地实验书库匹配书籍（快速）
        logger.info(f"在本地书库中搜索匹配: {user_query}")
        matched_books = find_books_by_task(user_query)
        
        if matched_books:
            logger.info(f"本地书库匹配成功，找到 {len(matched_books)} 本书")
            
            # 生成唯一任务ID
            task_id = str(uuid.uuid4())
            
            # 构建基本书籍信息（立即返回）
            basic_books = []
            for i, book in enumerate(matched_books):
                basic_book = {
                    "title": book.get('title', f'未知书籍{i+1}'),
                    "author": book.get('author', '未知作者'),
                    "isbn": book.get('isbn', f'978711100000{i+1}'),
                    "cover_url": f"https://example.com/cover{i+1}.jpg",
                    "reasons_loading": True  # 标记理由正在加载
                }
                basic_books.append(basic_book)
            
            # 存储任务信息
            async_tasks[task_id] = {
                'status': 'pending',
                'progress': '正在启动异步任务...',
                'user_query': user_query,
                'books': matched_books,
                'created_at': time.time()
            }
            
            # 在后台异步启动LLM理由生成
            logger.info(f"启动异步任务 {task_id} 生成推荐理由")
            executor.submit(generate_reasons_async, task_id, matched_books, user_query)
            
            # 立即返回基本信息
            response = {
                "status": "success",
                "user_query": user_query,
                "books": basic_books,
                "task_id": task_id,
                "reasons_loading": True,
                "message": "书籍基本信息已加载，推荐理由正在后台生成中..."
            }
            
            logger.info(f"立即返回基本书籍信息，任务ID: {task_id}")
            return jsonify(response)
            
        else:
            logger.info("本地书库未找到匹配")
            return jsonify({
                "status": "success",
                "user_query": user_query,
                "books": [],
                "message": "未找到匹配的书籍"
            })
        
    except Exception as e:
        logger.error(f"处理书籍推荐请求时发生错误: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/api/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    新的API端点：获取异步任务的状态和结果
    """
    try:
        if task_id not in async_tasks:
            return jsonify({
                "status": "error",
                "error": "任务ID不存在"
            }), 404
        
        task = async_tasks[task_id]
        
        response = {
            "task_id": task_id,
            "status": task['status'],
            "progress": task['progress']
        }
        
        if task['status'] == 'completed' and 'result' in task:
            # 任务完成，返回完整的推荐理由
            result_data = task['result']
            # 确保任务状态不被结果数据覆盖
            response['status'] = 'completed'  # 保持任务完成状态
            response['user_query'] = result_data.get('user_query', '')
            response['books'] = result_data.get('books', [])
            response['reasons_loading'] = False
            
            # 可选：清理已完成的任务（避免内存泄漏）
            # del async_tasks[task_id]
            
        elif task['status'] == 'error':
            response['error'] = task.get('error', '未知错误')
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"获取任务状态时发生错误: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500

# ===========================================
# 原有的 /input 端点保持不变
# ===========================================

def is_valid_input(text):
    
    return True, text

@app.route('/input', methods=['POST'])
def handle_input():
    global last_request_time
    try:
        data = request.json
        input_value = data.get('value', '')
        logger.info(f"收到前端输入: {input_value}")
        
        # 验证输入
        is_valid, cleaned_input = is_valid_input(input_value)
        if not is_valid:
            logger.info("输入包含无效字符（非中文或英文），忽略请求")
            return jsonify({"status": "success", "suggestions": []})
        
        current_time = time.time()
        # 检查当前时间与上次请求时间的差值
        if current_time - last_request_time < 2:
            logger.info("请求过于频繁，2秒内不再请求")
            #请求的时机应该设置更加合理
            return jsonify({"status": "success", "suggestions": []})
        
        # 当输入超过3个字符时调用星火API
        if len(cleaned_input) >= 3:
            logger.info(f"输入长度超过4个字符，开始调用{logger_name}")
            # 更新上次请求时间
            last_request_time = current_time
            # 添加延迟以模拟API处理时间
            time.sleep(1)
            suggestion = get_suggestion(cleaned_input)
            if suggestion:
                logger.info(f"{logger_name}返回建议: {suggestion}")
                return jsonify({"status": "success", "suggestions": suggestion})
            else:
                logger.error(f"{logger_name}返回空建议")
                return jsonify({"status": "error", "error": "获取建议失败"})
        
        logger.info("输入长度不足4个字符，不调用API")
        return jsonify({"status": "success", "suggestions": []})
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500

def inject_monitor_script(driver):
    monitor_script = ""
    try:
        # 读取两个核心JS文件的内容
        with open('show_books_with_reasons.js', 'r', encoding='utf-8') as f:
            monitor_script += f.read()
        
        with open('suggestion_display.js', 'r', encoding='utf-8') as f:
            monitor_script += f.read()
            
        driver.execute_script(monitor_script)
        logger.info("成功注入组合的外部JS脚本")

    except FileNotFoundError as e:
        logger.error(f"JS文件未找到: {e}, 请确保 show_books_with_reasons.js 和 suggestion_display.js 在同一目录下。")
        raise
    except Exception as e:
        logger.error(f"注入监听脚本时发生错误: {str(e)}")
        raise

def start_browser():
    try:
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 设置ChromeDriver路径
        service = Service()
        
        logger.info("正在初始化Chrome浏览器...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome浏览器初始化成功")
        
        logger.info("正在访问目标网页...")
        driver.get("https://opac.jiangnan.edu.cn/#/Home")
        
        logger.info("浏览器已启动，正在等待页面加载...")
        time.sleep(3)  # 给React应用足够的加载时间
        
        logger.info("注入监听脚本...")
        inject_monitor_script(driver)
        logger.info("监听脚本注入完成")
        
        return driver
    except Exception as e:
        logger.error(f"启动浏览器时发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("启动监控系统...")
    
    # 启动任务清理定时器
    start_cleanup_timer()
    logger.info("任务清理定时器已启动")
    
    # 启动Flask服务
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001, debug=False))
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("Flask服务器已启动在 http://localhost:5001")
    
    # 启动浏览器
    driver = start_browser()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("正在关闭系统...")
        # 关闭线程池
        executor.shutdown(wait=False)
        driver.quit() 