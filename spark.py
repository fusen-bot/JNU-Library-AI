from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time
import logging
import concurrent.futures

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
# 第二阶段重构：为单本书生成推荐理由
# ===========================================

def get_reason_for_single_book(book: dict, user_query: str) -> dict:
    """
    调用星火API，为单本书生成推荐理由。
    使用新的、轻量级的、解耦的提示词。
    """
    book_title = book.get('title', '未知书籍')
    book_author = book.get('author', '未知作者')
    
    logger.info(f"为书籍《{book_title}》生成推荐理由 (用户查询: {user_query})")

    # 新版系统提示词 (来自Modification_Best_Practices.md)
    system_prompt = """你是江南大学图书馆的资深图书推荐专家。你的任务是为一本指定的书籍生成精准、吸引人的推荐理由。

请严格按照以下JSON格式返回结果，不要包含任何解释性文字，只返回一个完整的JSON对象：

{
  "logical_reason": {
    "user_query_intent": "对用户检索意图的分析",
    "book_core_concepts": ["本书的核心概念1", "本书的核心概念2"],
    "application_fields_match": ["本书与哪些应用领域匹配1", "本书与哪些应用领域匹配2"]
  }
}

注意：不需要生成借阅热度信息(social_reason)，只专注于推荐依据(logical_reason)的生成。"""

    # 新版用户提示词
    user_prompt = f'用户检索词是："{user_query}"。请为书籍《{book_title}》（作者：{book_author}）生成推荐理由。'
    
    payload = {
        "model": "generalv3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "extra_body": {"enable_thinking": False},
        "max_tokens": 400  # 减少token，因为任务更简单
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            raw_content = result['choices'][0]['message']['content']
            
            # 清理和解析JSON
            # 尝试提取JSON部分
            if '```json' in raw_content:
                json_start = raw_content.find('```json') + 7
                json_end = raw_content.find('```', json_start)
                content = raw_content[json_start:json_end].strip()
            else:
                content = raw_content.strip()

            reason_data = json.loads(content)
            logger.info(f"成功为《{book_title}》生成并解析推荐理由")
            return reason_data
            
        else:
            logger.error(f"为《{book_title}》生成理由时API请求失败: {response.status_code}")
            return create_default_reasons(user_query, book_title)
            
    except Exception as e:
        logger.error(f"为《{book_title}》生成理由时发生错误: {str(e)}")
        return create_default_reasons(user_query, book_title)

# ===========================================
# 重构旧函数，改为并行调用
# ===========================================

def get_spark_books_with_reasons(books: list, user_query: str) -> dict:
    """
    调用星火API，为多本书并行生成推荐理由。
    这是重构后的函数，输入为书籍列表。
    """
    logger.info(f"开始为 {len(books)} 本书并行生成推荐理由")
    
    final_books = []
    
    # 使用线程池并行处理API请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(books)) as executor:
        # 为每本书提交一个任务
        future_to_book = {executor.submit(get_reason_for_single_book, book, user_query): book for book in books}
        
        for future in concurrent.futures.as_completed(future_to_book):
            book = future_to_book[future]
            try:
                # 获取AI生成的推荐理由
                reason_data = future.result()
                
                # 组合书籍信息和推荐理由
                book_with_reason = book.copy() # 复制基础信息
                book_with_reason.update(reason_data) # 添加理由
                book_with_reason["cover_url"] = f"https://example.com/cover{len(final_books)+1}.jpg" # 模拟封面
                # 确保星级数据被保留
                if 'match_stars' not in book_with_reason:
                    book_with_reason["match_stars"] = book.get('match_stars', 0)
                
                # 必须使用书籍数据中的自定义借阅热度，如果没有则使用默认值
                if 'social_reason' in book and book['social_reason']:
                    book_with_reason["social_reason"] = book['social_reason']
                else:
                    book_with_reason["social_reason"] = create_default_social_reason()
                
                final_books.append(book_with_reason)
                
            except Exception as exc:
                logger.error(f"处理书籍《{book.get('title')}》时产生异常: {exc}")
                # 即使单个请求失败，也添加带有默认理由的书籍，保证返回数量
                book_with_reason = book.copy()
                book_with_reason.update(create_default_reasons(user_query, book.get('title')))
                book_with_reason["cover_url"] = f"https://example.com/cover{len(final_books)+1}.jpg"
                # 确保星级数据被保留
                if 'match_stars' not in book_with_reason:
                    book_with_reason["match_stars"] = book.get('match_stars', 0)
                
                # 必须使用书籍数据中的自定义借阅热度，如果没有则使用默认值
                if 'social_reason' in book and book['social_reason']:
                    book_with_reason["social_reason"] = book['social_reason']
                else:
                    book_with_reason["social_reason"] = create_default_social_reason()
                
                final_books.append(book_with_reason)

    logger.info(f"已完成所有书籍的推荐理由生成")
    return {
        "status": "success",
        "user_query": user_query,
        "books": final_books
    }


def create_default_reasons(user_query, book_title):
    """为单个书籍创建默认的推荐理由"""
    return {
        "logical_reason": {
            "user_query_intent": f"分析用户查询 '{user_query}' 的意图时出错。",
            "book_core_concepts": ["无法生成核心概念"],
            "application_fields_match": ["无法生成应用领域匹配"]
        },
        "social_reason": {
            "departments": [{"name": "理学院", "rate": 0.1}]
        }
    }


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
    required_fields = ["title", "author", "logical_reason"]
    
    for field in required_fields:
        if field not in book:
            return False
    
    # 验证推荐依据结构
    logical_fields = ["user_query_intent", "book_core_concepts", "application_fields_match"]
    for field in logical_fields:
        if field not in book["logical_reason"]:
            return False
    
    # 注意：不再验证social_reason，因为它将由预定义数据提供
    
    return True

def create_default_logical_reason(user_query: str) -> dict:
    """创建默认的推荐依据"""
    return {
        "user_query_intent": f"用户搜索：{user_query}",
        "book_core_concepts": ["本书核心概念1", "本书核心概念2"],
        "application_fields_match": ["应用领域匹配1", "应用领域匹配2"]
    }

def create_default_social_reason() -> dict:
    """创建默认的借阅热度"""
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
# 原有函数保持不变 (但现在不再直接被新流程调用)
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
