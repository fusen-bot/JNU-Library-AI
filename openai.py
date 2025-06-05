import openai
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenAI API配置
# 请将以下API密钥替换为你的实际密钥
OPENAI_API_KEY = "your-openai-api-key-here"
OPENAI_BASE_URL = "https://api.openai.com/v1"  # 可以修改为其他兼容的API端点

# 初始化OpenAI客户端
openai.api_key = OPENAI_API_KEY
if OPENAI_BASE_URL != "https://api.openai.com/v1":
    openai.api_base = OPENAI_BASE_URL

def get_openai_suggestion(user_input: str) -> str:
    """
    调用OpenAI API，返回推荐书籍和问题建议。
    """
    logger.info(f"正在向OpenAI API发送请求，用户输入: {user_input}")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 可以改为 gpt-4 或其他模型
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的图书专家，请根据用户输入的关键词介绍最相关的3本书籍和2个用户最常搜的问题。你必须严格按照以下格式输出（不要有任何额外文字）：\n书籍：《书名1》《书名2》《书名3》\n问题：问题1？问题2？"
                },
                {
                    "role": "user", 
                    "content": f"用户输入的词是: '{user_input}'。"
                }
            ],
            temperature=0.7,
            max_tokens=100,
            timeout=10  # 10秒超时
        )
        
        suggestion = response.choices[0].message.content.strip()
        logger.info(f"OpenAI API返回建议: {suggestion}")
        return suggestion
        
    except openai.error.AuthenticationError:
        logger.error("OpenAI API认证失败，请检查API密钥")
        return ""
    except openai.error.RateLimitError:
        logger.error("OpenAI API请求超过限制")
        return ""
    except openai.error.APIConnectionError:
        logger.error("OpenAI API连接失败")
        return ""
    except openai.error.Timeout:
        logger.error("OpenAI API请求超时")
        return ""
    except Exception as e:
        logger.error(f"调用OpenAI API时发生错误: {str(e)}")
        return ""

def test_openai_connection():
    """
    测试OpenAI API连接
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        logger.error(f"OpenAI API连接测试失败: {str(e)}")
        return False

if __name__ == '__main__':
    # 测试API连接
    if test_openai_connection():
        logger.info("OpenAI API连接测试成功")
        
        # 测试建议功能
        test_input = "python编程"
        result = get_openai_suggestion(test_input)
        print(f"测试结果: {result}")
    else:
        logger.error("OpenAI API连接测试失败，请检查配置") 