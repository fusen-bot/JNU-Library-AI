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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask服务器，用于接收来自浏览器的请求
app = Flask(__name__)

# 配置CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://opac.jiangnan.edu.cn"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# 添加CORS响应头
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://opac.jiangnan.edu.cn')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# 星火API配置
API_PASSWORD = "vxtIbOIsNUPnvaVGhyrc:DbrpVfWvipRzHeFyRlGb"
API_URL = "https://spark-api-open.xf-yun.com/v1/chat/completions"

# 在文件的开头添加一个全局变量来记录上次请求的时间
last_request_time = 0

def get_spark_suggestion(user_input):
    logger.info(f"正在向星火API发送请求，用户输入: {user_input}")
    
    headers = {
        "Authorization": f"Bearer {API_PASSWORD}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "generalv3.5",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的图书馆馆员，请根据用户输入的关键词介绍最相关的4本书籍和2个用户最常搜的问题。你必须严格按照以下格式输出（不要有任何额外文字）：\n书籍：《书名1》《书名2》《书名3》《书名4》\n问题：问题1？问题2？"
            },
            {
                "role": "user",
                "content": f"用户输入的词是: '{user_input}'。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        logger.info(f"星火API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            suggestion = result['choices'][0]['message']['content']
            logger.info(f"星火API返回建议: {suggestion}")
            return suggestion
        else:
            logger.error(f"星火API请求失败: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"调用星火API时发生错误: {str(e)}")
        return None

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
            return jsonify({"status": "success", "suggestions": []})
        
        # 当输入超过4个字符时调用星火API
        if len(cleaned_input) >= 4:
            logger.info("输入长度超过4个字符，开始调用星火API")
            # 更新上次请求时间
            last_request_time = current_time
            # 添加延迟以模拟API处理时间
            time.sleep(1)
            suggestion = get_spark_suggestion(cleaned_input)
            if suggestion:
                logger.info(f"星火API返回建议: {suggestion}")
                return jsonify({"status": "success", "suggestions": suggestion})
            else:
                logger.error("星火API返回空建议")
                return jsonify({"status": "error", "error": "获取建议失败"})
        
        logger.info("输入长度不足2个字符，不调用API")
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
        
        console.log('初始化输入监控系统');
        
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
                defaultText.textContent = '正在为你查找相应推荐书籍和热门问题';
                defaultText.style.textAlign = 'center';
                displayArea.innerHTML = '';
                displayArea.appendChild(defaultText);
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
                    questionsTitle.textContent = '热门问题';
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
            const now = Date.now();
            if (now - lastRequestTime < REQUEST_DELAY) {
                console.log('请求过于频繁，等待中...');
                await new Promise(resolve => setTimeout(resolve, REQUEST_DELAY));
            }
            lastRequestTime = now;
            
            try {
                const response = await fetch('http://localhost:5001/input', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        messages: [{
                            role: "user",
                            content: inputValue
                        }]
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('服务器响应:', data);
                
                if (data.content) {
                    updateDisplay(data.content, false);
                } else {
                    const displayArea = document.getElementById('suggestion-display');
                    if (displayArea) hideDisplayArea(displayArea);
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
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001, debug=True))
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