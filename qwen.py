from http import HTTPStatus
import dashscope
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_qwen_suggestion(user_input: str) -> str:
    """
    调用千问API，返回推荐书籍和问题建议。
    基于原有的call_with_messages逻辑进行适配
    """
    logger.info(f"正在向千问API发送请求，用户输入: {user_input}")
    
    # 使用与原函数相同的消息格式，但替换用户输入
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的图书专家，请根据用户输入的关键词介绍最相关的 3 本书籍和 2 个用户最常搜的问题。你必须严格按照以下格式输出（不要有任何额外文字）：\\n 书籍：《书名 1》《书名 2》《书名 3》\\n 问题：问题 1？问题 2？"
        },
        {
            "role": "user",
            "content": "hi wold"
        },
        {
            "role": "assistant", 
            "content": "书籍：《你不知道的故事背后的秘密》《世界尽头的奇迹》《环球旅行指南》\n问题：这本书主要讲了什么内容？这本书适合哪些读者阅读？"
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    try:
        # 使用原有的API调用配置
        responses = dashscope.Generation.call(
            model="qwen-max",
            api_key="sk-0cc8e5c849604b5c9704113abc77be7d",
            messages=messages,
            stream=True,
            result_format='message',  # 将返回结果格式设置为 message
            top_p=0.8,
            temperature=0.7,
            enable_search=False
        )

        # 收集流式响应的完整内容
        full_content = ""
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                # 从流式响应中提取内容
                if hasattr(response.output, 'choices') and response.output.choices:
                    delta = response.output.choices[0].get('delta', {})
                    if 'content' in delta:
                        full_content += delta['content']
            else:
                logger.error(f'千问API请求失败: Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error message: {response.message}')
                return ""

        if full_content:
            logger.info(f"千问API返回建议: {full_content}")
            return full_content
        else:
            logger.error("千问API返回空内容")
            return ""
            
    except Exception as e:
        logger.error(f"调用千问API时发生错误: {str(e)}")
        return ""

def call_with_messages():
    messages = [{"role":"system","content":"你是一个专业的图书专家，请根据用户输入的关键词介绍最相关的 3 本书籍和 2 个用户最常搜的问题。你必须严格按照以下格式输出（不要有任何额外文字）：\\n 书籍：《书名 1》《书名 2》《书名 3》\\n 问题：问题 1？问题 2？"},
                {"role":"user","content":"hi wold"},
                {"role":"assistant","content":"书籍：《你不知道的故事背后的秘密》《世界尽头的奇迹》《环球旅行指南》\n问题：这本书主要讲了什么内容？这本书适合哪些读者阅读？"},
                {"role":"user",
                 "content":""}]

    responses = dashscope.Generation.call(
        model="qwen-max",
        api_key="sk-0cc8e5c849604b5c9704113abc77be7d",
        messages=messages,
        stream=True,
        result_format='message',  # 将返回结果格式设置为 message
        top_p=0.8,
        temperature=0.7,
        enable_search=False
    )

    for response in responses:
        if response.status_code == HTTPStatus.OK:
            print(response)
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))


if __name__ == '__main__':
    call_with_messages()