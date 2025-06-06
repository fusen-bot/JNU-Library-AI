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

@app.route('/api/books_with_reasons', methods=['POST'])
def get_books_with_reasons_api():
    """
    新的API端点：返回带推荐理由的书籍推荐
    现在使用真实的LLM调用
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
        
        # 调用真实的LLM API
        if API_BACKEND == "spark":
            llm_response = get_books_with_reasons(user_query)
            logger.info(f"星火API返回数据，状态: {llm_response.get('status')}")
        else:
            # 对于其他API后端，暂时使用模拟数据
            logger.warning(f"API后端 {API_BACKEND} 的书籍推荐功能尚未实现，使用模拟数据")
            llm_response = get_mock_books_with_reasons(user_query)
        
        return jsonify(llm_response)
        
    except Exception as e:
        logger.error(f"处理书籍推荐请求时发生错误: {str(e)}")
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
    monitor_script = """
    (function() {
        // 保证脚本只初始化一次的标志
        if (window.__inputMonitorInitialized) return;
        window.__inputMonitorInitialized = true;
        
        // 添加请求状态追踪变量及加载定时器句柄
        window.__suggestionsInFlight = false;
        window.__lastSuggestionsContent = '';
        window.__loadingTimer = null;
        
        console.log('🚀 初始化输入监控系统 - 集成新版推荐理由UI');
        
        // ================================
        // 新版书籍推荐理由UI组件 - 内联版本
        // ================================
        function showBooksWithReasonsInline(apiData) {
            console.log("🎨 使用真实环境新版推荐理由UI组件");
            console.log("📊 API数据:", apiData);
            
            const displayArea = document.getElementById('suggestion-display');
            if (!displayArea) return;
            
            // 清除加载动画
            if (displayArea._blinkInterval) {
                clearInterval(displayArea._blinkInterval);
                displayArea._blinkInterval = null;
            }
            
            if (apiData.status !== 'success' || !apiData.books || apiData.books.length === 0) {
                showErrorMessageInline(displayArea, "暂无推荐结果");
                return;
            }
            
            // 清空并重新创建内容
            displayArea.innerHTML = '';
            createBooksReasonContainerInline(displayArea, apiData.books);
            showDisplayArea(displayArea);
        }
        
        function createBooksReasonContainerInline(container, books) {
            // 创建标题
            const titleElement = document.createElement('div');
            titleElement.style.cssText = `
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 12px;
                color: #333;
                text-align: center;
                padding-bottom: 8px;
                border-bottom: 2px solid #05a081;
            `;
            titleElement.textContent = '🤖 AI智能推荐理由';
            container.appendChild(titleElement);
            
            // 限制最多显示3本书
            const maxBooks = Math.min(books.length, 3);
            
            for (let i = 0; i < maxBooks; i++) {
                const book = books[i];
                createBookReasonCardInline(container, book, i);
            }
        }
        
        function createBookReasonCardInline(container, book, index) {
            // 创建书籍卡片容器
            const bookCard = document.createElement('div');
            bookCard.style.cssText = `
                margin-bottom: 16px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: linear-gradient(135deg, #f8fffe 0%, #f0f7f5 100%);
                overflow: hidden;
                transition: all 0.3s ease;
            `;
            
            // 书籍标题栏
            const bookHeader = document.createElement('div');
            bookHeader.style.cssText = `
                padding: 12px 15px;
                background: linear-gradient(90deg, #05a081 0%, #048068 100%);
                color: white;
                font-weight: bold;
                font-size: 13px;
                display: flex;
                align-items: center;
                gap: 8px;
            `;
            
            // 书籍序号
            const bookNumber = document.createElement('span');
            bookNumber.style.cssText = `
                background: rgba(255,255,255,0.2);
                width: 20px;
                height: 20px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                flex-shrink: 0;
            `;
            bookNumber.textContent = index + 1;
            
            // 书籍标题
            const bookTitle = document.createElement('span');
            bookTitle.style.cssText = `
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            `;
            bookTitle.textContent = `《${book.title}》`;
            
            // 作者信息
            const bookAuthor = document.createElement('span');
            bookAuthor.style.cssText = `
                font-size: 11px;
                opacity: 0.9;
                font-weight: normal;
            `;
            bookAuthor.textContent = `- ${book.author}`;
            
            bookHeader.appendChild(bookNumber);
            bookHeader.appendChild(bookTitle);
            bookHeader.appendChild(bookAuthor);
            
            // 推荐理由块容器
            const reasonsContainer = document.createElement('div');
            reasonsContainer.style.cssText = `
                padding: 15px;
                display: flex;
                gap: 1px;
                background: #f8f8f8;
            `;
            
            // 创建逻辑分析块
            const logicalBlock = createReasonBlockInline(
                '🧠 逻辑分析',
                book.logical_reason,
                '#4a90e2',  // 蓝色主题
                '#e8f2ff'
            );
            
            // 创建社交证据块
            const socialBlock = createReasonBlockInline(
                '👥 社交证据', 
                book.social_reason,
                '#7b68ee',  // 紫色主题
                '#f0ecff'
            );
            
            reasonsContainer.appendChild(logicalBlock);
            reasonsContainer.appendChild(socialBlock);
            
            bookCard.appendChild(bookHeader);
            bookCard.appendChild(reasonsContainer);
            container.appendChild(bookCard);
            
            // 添加卡片悬停效果
            bookCard.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 12px rgba(5,160,129,0.15)';
            });
            
            bookCard.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
            });
        }
        
        function createReasonBlockInline(title, reasonData, themeColor, bgColor) {
            const block = document.createElement('div');
            block.style.cssText = `
                flex: 1;
                background: ${bgColor};
                border-radius: 6px;
                padding: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                border: 2px solid transparent;
            `;
            
            // 标题
            const blockTitle = document.createElement('div');
            blockTitle.style.cssText = `
                font-weight: bold;
                font-size: 12px;
                color: ${themeColor};
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 6px;
            `;
            blockTitle.textContent = title;
            
            // 简要内容（默认显示）
            const briefContent = document.createElement('div');
            briefContent.style.cssText = `
                font-size: 11px;
                color: #666;
                line-height: 1.4;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
            `;
            
            // 详细内容（悬停展开）
            const detailContent = document.createElement('div');
            detailContent.style.cssText = `
                font-size: 11px;
                color: #555;
                line-height: 1.5;
                margin-top: 8px;
                opacity: 0;
                max-height: 0;
                overflow: hidden;
                transition: all 0.3s ease;
                background: rgba(255,255,255,0.5);
                border-radius: 4px;
                padding: 0;
            `;
            
            // 根据理由类型填充内容
            if (title.includes('逻辑分析')) {
                briefContent.textContent = reasonData.ai_understanding;
                
                const detailHTML = `
                    <div style="padding: 8px;">
                        <div style="margin-bottom: 6px;"><strong>🎯 查询理解:</strong> ${reasonData.user_query_recap}</div>
                        <div style="margin-bottom: 6px;"><strong>🤖 AI分析:</strong> ${reasonData.ai_understanding}</div>
                        <div><strong>🔗 匹配逻辑:</strong> ${reasonData.keyword_match}</div>
                    </div>
                `;
                detailContent.innerHTML = detailHTML;
                
            } else if (title.includes('社交证据')) {
                briefContent.textContent = reasonData.trend;
                
                let departmentsHTML = '<div style="margin-bottom: 6px;"><strong>📊 各学院借阅率:</strong></div>';
                reasonData.departments.forEach(dept => {
                    const percentage = Math.round(dept.rate * 100);
                    const barWidth = dept.rate * 100;
                    departmentsHTML += `
                        <div style="margin: 4px 0; font-size: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis;">${dept.name}</span>
                                <span style="font-weight: bold; color: ${themeColor};">${percentage}%</span>
                            </div>
                            <div style="background: #ddd; height: 3px; border-radius: 2px; margin-top: 2px;">
                                <div style="background: ${themeColor}; height: 100%; width: ${barWidth}%; border-radius: 2px; transition: width 0.3s ease;"></div>
                            </div>
                        </div>
                    `;
                });
                
                const detailHTML = `
                    <div style="padding: 8px;">
                        ${departmentsHTML}
                        <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #eee;">
                            <strong>📈 趋势分析:</strong> ${reasonData.trend}
                        </div>
                    </div>
                `;
                detailContent.innerHTML = detailHTML;
            }
            
            block.appendChild(blockTitle);
            block.appendChild(briefContent);
            block.appendChild(detailContent);
            
            // 悬停展开效果
            block.addEventListener('mouseenter', function() {
                this.style.border = `2px solid ${themeColor}`;
                this.style.background = '#ffffff';
                briefContent.style.opacity = '0.7';
                detailContent.style.opacity = '1';
                detailContent.style.maxHeight = '200px';
                detailContent.style.padding = '0';
            });
            
            block.addEventListener('mouseleave', function() {
                this.style.border = '2px solid transparent';
                this.style.background = bgColor;
                briefContent.style.opacity = '1';
                detailContent.style.opacity = '0';
                detailContent.style.maxHeight = '0';
                detailContent.style.padding = '0';
            });
            
            return block;
        }
        
        function showErrorMessageInline(container, message) {
            // 清除加载动画
            if (container._blinkInterval) {
                clearInterval(container._blinkInterval);
                container._blinkInterval = null;
            }
            
            container.innerHTML = '';
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = `
                padding: 20px;
                text-align: center;
                color: #e74c3c;
                background: #ffe6e6;
                border-radius: 8px;
                border: 1px solid #f5c6cb;
                font-style: italic;
            `;
            errorDiv.textContent = message;
            container.appendChild(errorDiv);
        }
        
        // ================================
        // 原有监听脚本继续
        // ================================
        
        const targetSelector = '.ant-select-search__field';
        let lastRequestTime = 0;
        const REQUEST_DELAY = 2000; 
        const MAX_RETRIES = 3;
        const RETRY_DELAY = 2000; 
        
        // 创建显示区域
        function createDisplayArea() {
            // 先检查是否已存在
            let displayDiv = document.getElementById('suggestion-display');
            if (displayDiv) return displayDiv;
            
            const inputElement = document.querySelector(targetSelector);
            if (!inputElement) return null;
            
            const parent = inputElement.parentElement;
            displayDiv = document.createElement('div');
            displayDiv.id = 'suggestion-display';
            displayDiv.style.cssText = `
                position: absolute;
                left: 0;
                top: 100%;
                width: 100%;
                background-color: #fff;
                padding: 12px 15px;
                border-radius: 4px;
                border: 1px solid #05a081;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                z-index: 9999;
                font-size: 14px;
                max-height: 500px;
                min-height: 50px;
                overflow-y: auto;
                margin-top: 4px;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.15s ease;
                display: none;
                line-height: 1.6;
                color: #333;
                user-select: text;
                -webkit-user-select: text;
            `;
            parent.style.position = 'relative'; // 保证绝对定位基于输入框父元素
            parent.appendChild(displayDiv);
            return displayDiv;
        }
        
        function showDisplayArea(displayArea) {
            if (!displayArea) return;
            displayArea.style.display = 'block';
            setTimeout(() => {
                displayArea.style.opacity = '1';
                displayArea.style.pointerEvents = 'auto';
            }, 10);
        }
        
        function hideDisplayArea(displayArea) {
            if (!displayArea) return;
            displayArea.style.opacity = '0';
            displayArea.style.pointerEvents = 'none';
            setTimeout(() => {
                displayArea.style.display = 'none';
            }, 300);
        }
        
        function updateDisplay(text, isInput = true, isError = false) {
            // 在请求中且已有旧建议且等待时间小于阈值，则保留旧建议
            if (!text && window.__suggestionsInFlight && window.__lastSuggestionsContent && (Date.now() - lastRequestTime < REQUEST_DELAY)) {
                return;
            }
            const displayArea = document.getElementById('suggestion-display');
            if (!displayArea) return;
            
            if (!text) {
                // 这个逻辑应该是当检测到用户输入时候和当返回值暂时没有内容时显示默认提示
                showDisplayArea(displayArea);
                const defaultText = document.createElement('div');
                defaultText.style.marginBottom = '8px';
                defaultText.style.padding = '8px';
                defaultText.style.backgroundColor = '#f8f9fa';
                defaultText.style.borderRadius = '4px';
                defaultText.style.cursor = 'text';
                defaultText.style.color = '#666';
                // 改进的加载状态显示
                displayArea.innerHTML = '';
                
                // 创建加载容器
                const loadingContainer = document.createElement('div');
                loadingContainer.style.cssText = `
                    padding: 20px;
                    text-align: center;
                    background: linear-gradient(135deg, #f8fffe 0%, #f0f7f5 100%);
                    border-radius: 8px;
                    border: 2px solid #05a081;
                `;
                
                // 加载标题
                const loadingTitle = document.createElement('div');
                loadingTitle.style.cssText = `
                    font-weight: bold;
                    color: #05a081;
                    margin-bottom: 12px;
                    font-size: 14px;
                `;
                loadingTitle.textContent = '🤖 AI正在分析您的查询...';
                
                // 加载动画点
                const loadingDots = document.createElement('div');
                loadingDots.style.cssText = `
                    color: #666;
                    font-size: 13px;
                    line-height: 1.5;
                `;
                loadingDots.innerHTML = `
                    <div style="margin-bottom: 8px;">🔍 理解查询意图</div>
                    <div style="margin-bottom: 8px;">📚 搜索相关书籍</div>
                    <div style="margin-bottom: 8px;">🧠 生成推荐理由</div>
                    <div style="color: #05a081; font-weight: bold;">⏳ 预计需要15-30秒...</div>
                `;
                
                loadingContainer.appendChild(loadingTitle);
                loadingContainer.appendChild(loadingDots);
                displayArea.appendChild(loadingContainer);
                
                // 添加闪烁动画
                let opacity = 1;
                const blinkInterval = setInterval(() => {
                    opacity = opacity === 1 ? 0.6 : 1;
                    loadingTitle.style.opacity = opacity;
                }, 800);
                
                // 存储interval ID以便后续清除
                displayArea._blinkInterval = blinkInterval;
                return;
            }
            
            // 只在有实际内容时显示
            if (text && !isInput && !isError) {
                showDisplayArea(displayArea);
                displayArea.innerHTML = '';
                
                console.log("处理建议内容:", text); // 调试日志
                
                // 分割处理书籍和问题部分
                let booksPart = '';
                let questionsPart = '';
                
                // 更严格的格式检查，支持多种格式
                // 1. 尝试匹配"书籍："和"问题："分隔的标准格式
                const standardFormat = /书籍[:：](.+?)问题[:：](.+?)$/is;
                const standardMatch = text.match(standardFormat);
                
                if (standardMatch && standardMatch.length >= 3) {
                    booksPart = standardMatch[1].trim();
                    questionsPart = standardMatch[2].trim();
                } else {
                    // 2. 尝试分别匹配书籍和问题部分
                    const booksMatch = text.match(/书籍[:：](.+?)(?=问题[:：]|$)/is);
                    const questionsMatch = text.match(/问题[:：](.+?)$/is);
                    
                    if (booksMatch && booksMatch[1]) {
                        booksPart = booksMatch[1].trim();
                    }
                    
                    if (questionsMatch && questionsMatch[1]) {
                        questionsPart = questionsMatch[1].trim();
                    }
                }
                
                console.log("解析结果 - 书籍部分:", booksPart);
                console.log("解析结果 - 问题部分:", questionsPart);
                
                // 如果无法识别格式，则原样显示
                if (!booksPart && !questionsPart) {
                    const defaultContainer = document.createElement('div');
                    defaultContainer.style.marginBottom = '8px';
                    defaultContainer.style.padding = '8px';
                    defaultContainer.style.backgroundColor = '#f8f9fa';
                    defaultContainer.style.borderRadius = '4px';
                    defaultContainer.style.cursor = 'text';
                    defaultContainer.textContent = text;
                    displayArea.appendChild(defaultContainer);
                    return;
                }
                
                // 创建书籍部分
                if (booksPart) {
                    // 创建标题
                    const booksTitle = document.createElement('div');
                    booksTitle.style.fontWeight = 'bold';
                    booksTitle.style.marginBottom = '6px';
                    booksTitle.style.fontSize = '13px';
                    booksTitle.style.color = '#333';
                    booksTitle.textContent = '推荐书籍';
                    displayArea.appendChild(booksTitle);
                    
                    // 创建书籍内容容器
                    const booksContainer = document.createElement('div');
                    booksContainer.style.marginBottom = '15px'; // 增加间距
                    booksContainer.style.padding = '0';
                    booksContainer.style.display = 'flex';
                    booksContainer.style.flexWrap = 'wrap';
                    booksContainer.style.gap = '8px';
                    
                    // 尝试分割多本书
                    const books = booksPart.match(/《[^《》]+》/g) || [booksPart];
                    
                    // 限制最多显示3本书
                    const maxBooks = Math.min(books.length, 3);
                    
                    for (let i = 0; i < maxBooks; i++) {
                        const book = books[i];
                        // 创建独立的书籍项容器
                        const bookItem = document.createElement('div');
                        bookItem.style.flex = '1';
                        bookItem.style.minWidth = '30%';
                        bookItem.style.backgroundColor = '#e8f4f2';
                        bookItem.style.borderRadius = '4px';
                        bookItem.style.padding = '8px';
                        bookItem.style.cursor = 'pointer';
                        bookItem.style.color = '#2a6a5c';
                        bookItem.style.border = '1px solid #d0e6e2';
                        bookItem.style.transition = 'all 0.2s ease';
                        bookItem.setAttribute('data-item-type', 'book');
                        bookItem.setAttribute('data-item-index', i.toString());
                        
                        // 添加悬停效果
                        bookItem.addEventListener('mouseover', function() {
                            this.style.backgroundColor = '#d4ebe7';
                            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                        });
                        
                        bookItem.addEventListener('mouseout', function() {
                            this.style.backgroundColor = '#e8f4f2';
                            this.style.boxShadow = 'none';
                        });
                        
                        // 内容布局
                        const bookContent = document.createElement('div');
                        bookContent.style.display = 'flex';
                        bookContent.style.alignItems = 'center';
                        
                        // 添加序号圆圈
                        const bookIndex = document.createElement('span');
                        bookIndex.style.minWidth = '18px';
                        bookIndex.style.height = '18px';
                        bookIndex.style.backgroundColor = '#05a081';
                        bookIndex.style.color = '#fff';
                        bookIndex.style.borderRadius = '50%';
                        bookIndex.style.fontSize = '10px';
                        bookIndex.style.display = 'flex';
                        bookIndex.style.alignItems = 'center';
                        bookIndex.style.justifyContent = 'center';
                        bookIndex.style.marginRight = '8px';
                        bookIndex.style.flexShrink = '0';
                        bookIndex.textContent = (i + 1).toString();
                        
                        // 添加文本
                        const bookText = document.createElement('span');
                        bookText.style.overflow = 'hidden';
                        bookText.style.textOverflow = 'ellipsis';
                        bookText.style.wordBreak = 'break-word'; // 允许在任何字符间断行
                        bookText.textContent = book.trim();
                        
                        bookContent.appendChild(bookIndex);
                        bookContent.appendChild(bookText);
                        bookItem.appendChild(bookContent);
                        booksContainer.appendChild(bookItem);
                    }
                    
                    displayArea.appendChild(booksContainer);
                }
                
                // 创建问题部分
                if (questionsPart) {
                    // 创建标题
                    const questionsTitle = document.createElement('div');
                    questionsTitle.style.fontWeight = 'bold';
                    questionsTitle.style.marginBottom = '6px';
                    questionsTitle.style.fontSize = '13px';
                    questionsTitle.style.color = '#333';
                    questionsTitle.textContent = '热门话题';
                    displayArea.appendChild(questionsTitle);
                    
                    // 创建问题内容容器
                    const questionsContainer = document.createElement('div');
                    questionsContainer.style.display = 'flex';
                    questionsContainer.style.flexDirection = 'column';
                    questionsContainer.style.gap = '8px';
                    
                    // 处理问题部分
                    let questions = [];
                    if (questionsPart.includes('？') || questionsPart.includes('?')) {
                        // 尝试分割多个问题 (按问号分割)
                        questions = questionsPart.split(/[？?]/).filter(q => q.trim());
                    } else {
                        // 如果没有问号，则将整个文本作为一个问题
                        questions = [questionsPart];
                    }
                    
                    // 限制最多显示2个问题
                    const maxQuestions = Math.min(questions.length, 2);
                    
                    for (let i = 0; i < maxQuestions; i++) {
                        if (!questions[i].trim()) continue;
                        
                        // 创建独立的问题项容器
                        const questionItem = document.createElement('div');
                        questionItem.style.backgroundColor = '#f0f2f7';
                        questionItem.style.borderRadius = '4px';
                        questionItem.style.padding = '8px';
                        questionItem.style.cursor = 'pointer';
                        questionItem.style.color = '#3a5ca8';
                        questionItem.style.border = '1px solid #dce1ec';
                        questionItem.style.transition = 'all 0.2s ease';
                        questionItem.setAttribute('data-item-type', 'question');
                        questionItem.setAttribute('data-item-index', i.toString());
                        
                        // 添加悬停效果
                        questionItem.addEventListener('mouseover', function() {
                            this.style.backgroundColor = '#e4e8f3';
                            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                        });
                        
                        questionItem.addEventListener('mouseout', function() {
                            this.style.backgroundColor = '#f0f2f7';
                            this.style.boxShadow = 'none';
                        });
                        
                        // 内容布局
                        const questionContent = document.createElement('div');
                        questionContent.style.display = 'flex';
                        questionContent.style.alignItems = 'center';
                        
                        // 添加序号圆圈
                        const questionIndex = document.createElement('span');
                        questionIndex.style.minWidth = '18px';
                        questionIndex.style.height = '18px';
                        questionIndex.style.backgroundColor = '#4671d5';
                        questionIndex.style.color = '#fff';
                        questionIndex.style.borderRadius = '50%';
                        questionIndex.style.fontSize = '10px';
                        questionIndex.style.display = 'flex';
                        questionIndex.style.alignItems = 'center';
                        questionIndex.style.justifyContent = 'center';
                        questionIndex.style.marginRight = '8px';
                        questionIndex.style.flexShrink = '0';
                        questionIndex.textContent = (i + 1).toString();
                        
                        // 添加文本
                        const questionText = document.createElement('span');
                        questionText.style.overflow = 'hidden';
                        questionText.style.textOverflow = 'ellipsis';
                        questionText.style.wordBreak = 'break-word'; // 允许在任何字符间断行
                        
                        // 只有在不是原始文本结尾处的问题才添加问号
                        if (i < questions.length - 1 || questionsPart.endsWith('？') || questionsPart.endsWith('?')) {
                            questionText.textContent = questions[i].trim() + '？';
                        } else {
                            questionText.textContent = questions[i].trim();
                        }
                        
                        questionContent.appendChild(questionIndex);
                        questionContent.appendChild(questionText);
                        questionItem.appendChild(questionContent);
                        questionsContainer.appendChild(questionItem);
                    }
                    
                    displayArea.appendChild(questionsContainer);
                }
            } else {
                hideDisplayArea(displayArea);
            }
        }
        
        async function sendToServer(inputValue, retryCount = 0) {
            // 标记请求开始，并设置加载延迟定时器
            window.__suggestionsInFlight = true;
            // 清除上一轮加载定时器
            if (window.__loadingTimer) clearTimeout(window.__loadingTimer);
            // 等待超时后显示默认提示
            window.__loadingTimer = setTimeout(() => {
                if (window.__suggestionsInFlight) {
                    updateDisplay('', false);
                }
            }, REQUEST_DELAY);
            const now = Date.now();
            if (now - lastRequestTime < REQUEST_DELAY) {
                console.log('请求过于频繁，等待中...');
                await new Promise(resolve => setTimeout(resolve, REQUEST_DELAY));
            }
            lastRequestTime = now;
            
            try {
                const response = await fetch('http://localhost:5001/api/books_with_reasons', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: inputValue })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('🔍 服务器响应（新API）:', data);
                
                // 处理新的API响应格式 - 使用新版UI组件
                if (data.status === 'success' && data.books && data.books.length > 0) {
                    // ✨ 使用新版推荐理由UI组件
                    showBooksWithReasonsInline(data);
                    
                    // 更新状态
                    window.__lastSuggestionsContent = JSON.stringify(data);
                    clearTimeout(window.__loadingTimer);
                    window.__suggestionsInFlight = false;
                    
                    // 在控制台详细打印推荐理由
                    console.log('📋 推荐详情:');
                    data.books.forEach((book, index) => {
                        console.log(`📚 书籍${index + 1}: ${book.title} (${book.author})`);
                        console.log("  🧠 逻辑分析:", book.logical_reason);
                        console.log("  👥 社交证据:", book.social_reason);
                        console.log("  ---");
                    });
                } else {
                    console.warn('⚠️ 新API返回格式异常:', data);
                    const displayArea = document.getElementById('suggestion-display');
                    if (displayArea) {
                        showErrorMessageInline(displayArea, data.error || '暂无推荐结果');
                        showDisplayArea(displayArea);
                    }
                    // 请求失败或无建议，清除加载定时器并重置请求状态
                    clearTimeout(window.__loadingTimer);
                    window.__suggestionsInFlight = false;
                }
            } catch (error) {
                console.error('请求失败:', error);
                if (retryCount < MAX_RETRIES) {
                    const retryDelay = RETRY_DELAY * Math.pow(2, retryCount);
                    console.log(`重试中... (${retryCount + 1}/${MAX_RETRIES}), 等待 ${retryDelay}ms`);
                    await new Promise(resolve => setTimeout(resolve, retryDelay));
                    return sendToServer(inputValue, retryCount + 1);
                }
            }
        }
        
        // 去除旧的事件监听(防止重复绑定)
        function removeOldListeners() {
            const inputs = document.querySelectorAll(targetSelector);
            inputs.forEach(input => {
                if (input.hasAttribute('data-monitored')) {
                    const oldHandler = input._inputHandler;
                    if (oldHandler) {
                        input.removeEventListener('input', oldHandler);
                    }
                    input.removeAttribute('data-monitored');
                }
            });
        }
        
        function handleInput(event) {
            const inputValue = event.target.value.trim();
            if (!inputValue) {
                const displayArea = document.getElementById('suggestion-display');
                if (displayArea) hideDisplayArea(displayArea);
                return;
            }
            
            console.log('捕获到输入:', inputValue);
            
            if (inputValue.length >= 1) {
                // 显示默认提示
                updateDisplay('');
                if (inputValue.length > 3) {
                    // 发送请求获取建议
                    sendToServer(inputValue);
                }
            } else {
                const displayArea = document.getElementById('suggestion-display');
                if (displayArea) hideDisplayArea(displayArea);
            }
        }

        // 监听动态加载的输入框
        function setupMonitor() {
            // 先清除旧的监听器
            removeOldListeners();
            
            const inputElement = document.querySelector(targetSelector);
            if (inputElement && !inputElement.hasAttribute('data-monitored')) {
                console.log('找到输入框，设置监听器');
                inputElement.setAttribute('data-monitored', 'true');
                // 存储处理函数的引用以便后续移除
                inputElement._inputHandler = handleInput;
                inputElement.addEventListener('input', inputElement._inputHandler);
                // 重新创建显示区域
                createDisplayArea();
            }
        }

        // 创建观察器监听DOM变化
        const observer = new MutationObserver((mutations) => {
            setupMonitor();
        });

        // 开始观察整个文档
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // 监听路由变化(前进/后退)
        window.addEventListener('popstate', function() {
            console.log('检测到路由变化(popstate)，重新设置监听器');
            // 等待DOM更新完成再重新绑定
            setTimeout(setupMonitor, 500);
        });
        
        // 监听hash变化(如果网站使用hash路由)
        window.addEventListener('hashchange', function() {
            console.log('检测到hash变化，重新设置监听器');
            // 等待DOM更新完成再重新绑定
            setTimeout(setupMonitor, 500);
        });
        
        // 定时检查保证监听器正常工作
        setInterval(setupMonitor, 1000);

        // 初始检查
        setupMonitor();
        
        console.log('监听脚本加载完成，等待输入框出现');
    })();
    """
    
    try:
        driver.execute_script(monitor_script)
        logger.info("监听脚本注入成功")
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
        driver.quit() 