from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置你的API密码（从讯飞星火平台控制台获取）
API_PASSWORD = "cySRZXOQXUWbCQqsKQAO:ShxaKdkJFfhrMQaxneXg"

# 请求头
headers = {
    "Authorization": f"Bearer {API_PASSWORD}",
    "Content-Type": "application/json"
}

# 请求地址
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

app = Flask(__name__)

# 配置CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://opac.jiangnan.edu.cn", "http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/input', methods=['POST', 'OPTIONS'])
def chat_handler():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        logger.info(f"收到请求数据: {data}")
        
        if not data or 'messages' not in data:
            return jsonify({"error": "无效输入，请求体必须包含 'messages' 字段"}), 400

        # 添加系统消息
        system_message = {
            "role": "system",
            "content": "你是一个专业的图书馆馆员，请根据用户输入的关键词介绍最相关的3本书籍和2个相关内容用户最常搜的问题。你必须严格按照以下格式输出（不要有任何额外文字）：\n书籍：《书名1》《书名2》《书名3》\n问题：问题1？问题2？"
        }
        
        # 将系统消息添加到消息列表的开头
        current_messages = [system_message] + data['messages']

        payload = {
            "model": "generalv3.5",
            "user": "test_user_001", 
            "messages": current_messages,
            "temperature": 0.7,
            "top_k": 4,
            "stream": False,
            "max_tokens": 1024,
            "presence_penalty": 0.5,
            "frequency_penalty": 0.5,
            "tools": [
                {
                    "type": "web_search",
                    "web_search": {
                        "enable": True,
                        "show_ref_label": True,
                        "search_mode": "normal"
                    }
                }
            ]
        }

        logger.info("正在发送请求到星火API...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        response_json = response.json()
        logger.info(f"星火API响应: {response_json}")
        
        if 'choices' not in response_json or not response_json['choices'] or \
           'message' not in response_json['choices'][0] or \
           'content' not in response_json['choices'][0]['message']:
            return jsonify({"error": "星火API响应格式错误或缺少必要字段"}), 500
            
        assistant_message = response_json['choices'][0]['message']['content']
        logger.info(f"处理后的返回内容: {assistant_message}")
        
        # 统一返回格式，使用suggestions字段（web_monitor.py也使用这个字段）
        return jsonify({
            "role": "assistant", 
            "content": assistant_message, 
            "suggestions": assistant_message
        })

    except requests.exceptions.HTTPError as http_err:
        error_message = f"请求星火API时发生HTTP错误: {http_err}"
        if 'response' in locals():
            error_message += f" - 响应内容: {response.text}"
        logger.error(error_message)
        return jsonify({"error": error_message}), response.status_code if 'response' in locals() else 500
    except requests.exceptions.RequestException as e:
        logger.error(f"请求星火API失败: {str(e)}")
        return jsonify({"error": f"请求星火API失败: {str(e)}"}), 500
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"处理星火API响应时出错: {str(e)}")
        return jsonify({"error": f"处理星火API响应时出错: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"发生未知错误: {str(e)}")
        return jsonify({"error": f"发生未知错误: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("启动Flask服务器...")
    app.run(host='0.0.0.0', port=5001, debug=False)