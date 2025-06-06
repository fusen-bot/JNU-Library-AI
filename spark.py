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

# ===========================================
# 新增：带推荐理由的书籍推荐功能
# ===========================================

def get_spark_books_with_reasons(user_query: str) -> dict:
    """
    调用星火API，返回带推荐理由的书籍推荐数据
    返回格式符合新的数据契约
    """
    logger.info(f"正在向星火API发送书籍推荐理由请求，用户输入: {user_query}")
    
    # 构建新的 Prompt（目前的提示词太长了以及返回的也是，能否缩减以减少延迟）
    system_prompt = """你是江南大学图书馆的资深图书推荐专家。你的任务是根据用户的检索词推荐3本相关书籍，并为每本书生成推荐理由。
    
请严格按照以下JSON格式返回结果，不要包含任何解释性文字，只返回一个完整的JSON对象：

{
  "recommendations": [
    {
      "book_title": "书名",
      "book_author": "作者姓名", 
      "logical_reason": {
        "user_query_intent": "你的检索意图",
        "book_core_concepts": ["本书核心概念1", "本书核心概念2"],
        "application_fields_match": ["应用领域匹配1", "应用领域匹配2"]
      },
      "social_reason": {
        "departments": [
          {"name": "计算机科学与工程学院", "rate": 0.15},
          {"name": "物联网工程学院", "rate": 0.72},
          {"name": "理学院", "rate": 0.31},
          {"name": "商学院", "rate": 0.12}
        ]
      }
    }
  ]
}

要求：
1. 推荐3本与用户检索词最相关的书籍
2. logical_reason要体现你的专业分析能力，包含用户意图、书籍核心概念和应用领域匹配。
3. social_reason中的departments要包含普通大学的学院名称，借阅率用0到1之间的小数，不包含趋势描述。"""

    user_prompt = f"用户检索词是：\"{user_query}\"。请为此推荐3本最相关的书籍并生成推荐理由。"
    
    payload = {
        "model": "generalv3",
        "messages": [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.3,  # 降低温度确保输出更稳定
        "max_tokens": 800   # 增加token限制支持更长的回复
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        logger.info(f"星火API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            raw_content = result['choices'][0]['message']['content']
            logger.info(f"星火API原始返回: {raw_content}")
            
            # 解析LLM返回的JSON
            parsed_data = parse_spark_json_response(raw_content, user_query)
            return parsed_data
            
        else:
            logger.error(f"星火API请求失败: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return create_error_response("API请求失败")
            
    except Exception as e:
        logger.error(f"调用星火API时发生错误: {str(e)}")
        return create_error_response(f"调用API时发生错误: {str(e)}")

def parse_spark_json_response(raw_content: str, user_query: str) -> dict:
    """
    解析星火API返回的JSON内容，转换为标准的数据契约格式
    """
    try:
        # 清理可能的多余字符
        content = raw_content.strip()
        
        # 尝试提取JSON部分
        if '```json' in content:
            # 处理包含代码块标记的情况
            json_start = content.find('```json') + 7
            json_end = content.find('```', json_start)
            if json_end != -1:
                content = content[json_start:json_end].strip()
        elif content.startswith('```') and content.endswith('```'):
            # 处理一般的代码块
            content = content[3:-3].strip()
        
        # 解析JSON
        llm_data = json.loads(content)
        logger.info("成功解析LLM返回的JSON")
        
        # 转换为标准数据契约格式
        if "recommendations" in llm_data and isinstance(llm_data["recommendations"], list):
            books = []
            
            for i, item in enumerate(llm_data["recommendations"][:3]):  # 最多取3本书
                try:
                    book = {
                        "title": item.get("book_title", f"未知书籍{i+1}"),
                        "author": item.get("book_author", "未知作者"),
                        "isbn": f"978711100000{i+1}",  # 模拟ISBN
                        "cover_url": f"https://example.com/cover{i+1}.jpg",  # 模拟封面URL
                        "logical_reason": item.get("logical_reason", create_default_logical_reason(user_query)),
                        "social_reason": item.get("social_reason", create_default_social_reason())
                    }
                    
                    # 验证数据完整性
                    if validate_book_data(book):
                        books.append(book)
                    else:
                        logger.warning(f"书籍{i+1}数据不完整，跳过")
                        
                except Exception as e:
                    logger.error(f"处理书籍{i+1}时发生错误: {e}")
                    continue
            
            if len(books) > 0:
                return {
                    "status": "success",
                    "user_query": user_query,
                    "books": books
                }
            else:
                return create_error_response("无法解析出有效的书籍数据")
        else:
            logger.error("LLM返回的JSON格式不正确")
            return create_fallback_response(user_query)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        logger.error(f"原始内容: {raw_content}")
        return create_fallback_response(user_query)
    except Exception as e:
        logger.error(f"解析LLM响应时发生错误: {e}")
        return create_fallback_response(user_query)

def validate_book_data(book: dict) -> bool:
    """验证书籍数据的完整性"""
    required_fields = ["title", "author", "logical_reason", "social_reason"]
    
    for field in required_fields:
        if field not in book:
            return False
    
    # 验证逻辑分析结构
    logical_fields = ["user_query_intent", "book_core_concepts", "application_fields_match"]
    for field in logical_fields:
        if field not in book["logical_reason"]:
            return False
    
    # 验证社交证据结构
    if "departments" not in book["social_reason"]:
        return False
    
    return True

def create_default_logical_reason(user_query: str) -> dict:
    """创建默认的逻辑分析"""
    return {
        "user_query_intent": f"用户搜索：{user_query}",
        "book_core_concepts": ["本书核心概念1", "本书核心概念2"],
        "application_fields_match": ["应用领域匹配1", "应用领域匹配2"]
    }

def create_default_social_reason() -> dict:
    """创建默认的社交证据"""
    return {
        "departments": [
            {"name": "计算机科学与工程学院", "rate": 0.6},
            {"name": "理学院", "rate": 0.3},
            {"name": "商学院", "rate": 0.2}
        ]
    }

def create_error_response(error_message: str) -> dict:
    """创建错误响应"""
    return {
        "status": "error",
        "error": error_message,
        "books": []
    }

def create_fallback_response(user_query: str) -> dict:
    """创建备用响应（当LLM解析失败时）"""
    logger.info("使用备用响应机制")
    fallback_books = [
        {
            "title": "相关主题推荐书籍1",
            "author": "专业作者",
            "isbn": "9787111000001", 
            "cover_url": "https://example.com/cover1.jpg",
            "logical_reason": create_default_logical_reason(user_query),
            "social_reason": create_default_social_reason()
        }
    ]
    
    return {
        "status": "success",
        "user_query": user_query,
        "books": fallback_books
    }

# ===========================================
# 原有函数保持不变
# ===========================================

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
                "content": "你是一个专业的图书专家，请根据用户输入的关键词介绍最相关的3本书籍和2个用户热门的问题。你必须严格按照以下格式输出（不要有任何额外文字）：\n书籍：《书名1》《书名2》《书名3》\n问题：问题1？问题2？"
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