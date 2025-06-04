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

# 星火API配置
API_PASSWORD = "cySRZXOQXUWbCQqsKQAO:ShxaKdkJFfhrMQaxneXg"


# 请求头
headers = {
    "Authorization": f"Bearer {API_PASSWORD}",
    "Content-Type": "application/json"
}

# 请求地址
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

app = Flask(__name__)



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
        # 只取用户输入内容
        user_input = data['messages'][0]['content'] if data['messages'] and 'content' in data['messages'][0] else ''
        assistant_message = get_spark_suggestion(user_input)
        logger.info(f"处理后的返回内容: {assistant_message}")
        return jsonify({
            "role": "assistant",
            "content": assistant_message,
            "suggestions": assistant_message
        })
    except Exception as e:
        logger.error(f"发生未知错误: {str(e)}")
        return jsonify({"error": f"发生未知错误: {str(e)}"}), 500

def get_spark_suggestion(user_input: str) -> str:
    """
    调用星火API，返回推荐书籍和问题建议。
    """
    logger.info(f"正在向星火API发送请求，用户输入: {user_input}")
    
    payload = {
        "model": "generalv3",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的图书专家，请根据用户输入的关键词介绍最相关的3本书籍和2个用户最常搜的问题。你必须严格按照以下格式输出（不要有任何额外文字）：\n书籍：《书名1》《书名2》《书名3》\n问题：问题1？问题2？"
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
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        logger.info(f"星火API响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            suggestion = result['choices'][0]['message']['content']
            logger.info(f"星火API返回建议: {suggestion}")
            return suggestion
        else:
            logger.error(f"星火API请求失败: {response.status_code}")
            return ""
    except Exception as e:
        logger.error(f"调用星火API时发生错误: {str(e)}")
        return ""

if __name__ == '__main__':
    logger.info("启动Flask服务器...")
    app.run(host='0.0.0.0', port=5001, debug=False)