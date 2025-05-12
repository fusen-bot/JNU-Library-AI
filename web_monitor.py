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
                "content": "你是一个专业的图书馆馆员，请根据用户输入的关键词介绍最相关的4本书籍和2个用户最常搜的问题。注意事项：不要解释，只回复找到的书籍名和相关问题，不要其他字词和文颜字。模板示例：书籍：《红楼梦》《水浒传》《西游记》问题：xx？xx？"
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

@app.route('/input', methods=['POST'])
def handle_input():
    global last_request_time
    try:
        data = request.json
        input_value = data.get('value', '')
        logger.info(f"收到前端输入: {input_value}")
        
        current_time = time.time()
        # 检查当前时间与上次请求时间的差值
        if current_time - last_request_time < 5:
            logger.info("请求过于频繁，5秒内不再请求")
            return jsonify({"status": "success", "suggestions": []})
        
        # 当输入超过6个字符时调用星火API
        if len(input_value) >= 6:
            logger.info("输入长度超过6个字符，开始调用星火API")
            # 更新上次请求时间
            last_request_time = current_time
            # 添加延迟以模拟API处理时间
            time.sleep(1)
            suggestion = get_spark_suggestion(input_value)
            if suggestion:
                logger.info(f"星火API返回建议: {suggestion}")
                return jsonify({"status": "success", "suggestions": suggestion})
            else:
                logger.error("星火API返回空建议")
                return jsonify({"status": "error", "error": "获取建议失败"})
        
        logger.info("输入长度不足6个字符，不调用API")
        return jsonify({"status": "success", "suggestions": []})
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500

def inject_monitor_script(driver):
    monitor_script = """
    function initInputMonitor() {
        const targetSelector = '.ant-select-search__field';
        let lastRequestTime = 0;
        const REQUEST_DELAY = 2000; // 2秒延迟
        const MAX_RETRIES = 3;
        const RETRY_DELAY = 1000; // 1秒重试延迟
        
        // 创建显示区域
        function createDisplayArea() {
            const inputElement = document.querySelector(targetSelector);
            if (!inputElement) return null;
            const parent = inputElement.parentElement;
            const displayDiv = document.createElement('div');
            displayDiv.id = 'suggestion-display';
            displayDiv.style.cssText = `
                position: absolute;
                left: 0;
                top: 100%;
                width: 100%;
                background-color: #fff;
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #05a081;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                z-index: 9999;
                font-size: 14px;
                max-height: 400px;
                overflow-y: auto;
                margin-top: 4px;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.3s cubic-bezier(0.4,0,0.2,1);
                display: none;
            `;
            parent.style.position = 'relative'; // 保证绝对定位基于输入框父元素
            parent.appendChild(displayDiv);
            return displayDiv;
        }
        
        const displayArea = createDisplayArea();
        
        function showDisplayArea() {
            displayArea.style.display = 'block';
            setTimeout(() => {
                displayArea.style.opacity = '1';
                displayArea.style.pointerEvents = 'auto';
            }, 10);
        }
        function hideDisplayArea() {
            displayArea.style.opacity = '0';
            displayArea.style.pointerEvents = 'none';
            setTimeout(() => {
                displayArea.style.display = 'none';
            }, 300);
        }
        
        function updateDisplay(text, isInput = true, isError = false) {
            if (!text) {
                hideDisplayArea();
                return;
            }
            
            // 仅在非输入内容且非获取建议提示时显示
            if (isInput || (!isInput && !isError && text === '正在获取建议...')) {
                return;
            }
            
            showDisplayArea();
            const prefix = isError ? '错误: ' : '';
            const newLine = document.createElement('div');
            newLine.style.marginBottom = '5px';
            newLine.style.color = isError ? 'red' : 'black';
            newLine.textContent = prefix + text;
            // 将新内容插入到顶部
            displayArea.insertBefore(newLine, displayArea.firstChild);
            // 保持最新的3条记录
            while (displayArea.children.length > 3) {
                displayArea.removeChild(displayArea.lastChild);
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
                // 不显示"正在获取建议..."消息
                // updateDisplay('正在获取建议...', false);
                
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
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    hideDisplayArea();
                }
            } catch (error) {
                console.error('请求失败:', error);
                if (retryCount < MAX_RETRIES) {
                    const retryDelay = RETRY_DELAY * Math.pow(2, retryCount); // 指数退避
                    console.log(`重试中... (${retryCount + 1}/${MAX_RETRIES}), 等待 ${retryDelay}ms`);
                    updateDisplay(`请求失败，正在重试 (${retryCount + 1}/${MAX_RETRIES})...`, false, true);
                    await new Promise(resolve => setTimeout(resolve, retryDelay));
                    return sendToServer(inputValue, retryCount + 1);
                } else {
                    updateDisplay('请求失败: ' + error.message, false, true);
                }
            }
        }
        
        function handleInput(event) {
            const inputValue = event.target.value.trim();
            if (!inputValue) {
                hideDisplayArea();
                return;
            }
            
            console.log('捕获到输入:', inputValue);
            // 不再显示用户输入
            // updateDisplay(inputValue, true);
            
            if (inputValue.length >= 6) {
                sendToServer(inputValue);
            } else {
                hideDisplayArea();
            }
        }

        // 监听动态加载的输入框
        function setupMonitor() {
            const inputElement = document.querySelector(targetSelector);
            if (inputElement && !inputElement.hasAttribute('data-monitored')) {
                console.log('找到输入框，设置监听器');
                inputElement.setAttribute('data-monitored', 'true');
                inputElement.addEventListener('input', handleInput);
            }
        }

        // 创建观察器监听DOM变化
        const observer = new MutationObserver((mutations) => {
            setupMonitor();
        });

        // 开始观察
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // 初始检查
        setupMonitor();
    }
    
    // 初始化监听器
    initInputMonitor();
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
        time.sleep(5)  # 给React应用足够的加载时间
        
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