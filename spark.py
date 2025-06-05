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
    # 测试函数
    test_input = "python编程"
    result = get_spark_suggestion(test_input)
    print(f"测试结果: {result}")