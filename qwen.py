from http import HTTPStatus
import dashscope
import logging
import json
import concurrent.futures
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===========================================
# 第二阶段重构：为单本书生成推荐理由
# ===========================================

def get_reason_for_single_book(book: dict, user_query: str, max_retries: int = 5, timeout: int = 20) -> dict:
    """
    调用千问API，为单本书生成推荐理由。
    使用新的、轻量级的、解耦的提示词。
    添加智能重试机制：最多5次重试，总超时20秒。
    """
    book_title = book.get('title', '未知书籍')
    book_author = book.get('author', '未知作者')
    
    # 重试等待时间配置：递增延迟，首次快速重试，后续逐渐增加，而且如果收到返回值后立刻暂停重试以及后续的内容传递，就只传递除初次返回的
    # 0.5秒 → 1秒 → 1.5秒 → 2秒 → 2.5秒，总计7.5秒
    retry_delays = [0.5, 1, 1.5, 2, 2.5]
    start_time = time.time()
    
    logger.info(f"为书籍《{book_title}》生成推荐理由 (用户查询: {user_query})")

    # 新版系统提示词 (来自Modification_Best_Practices.md)
    system_prompt = """你是江南大学图书馆的资深图书推荐专家。你的任务是为一本指定的书籍生成精准、吸引人的推荐理由。

请严格按照以下JSON格式返回结果，不要包含任何解释性文字，只返回一个完整的JSON对象：

{
  "logical_reason": {
    "user_query_intent": "检索'{用户输入}' ➡️ {意图分析} ➡️ 推荐{书籍类型}书籍",
    "book_core_concepts": ["本书的核心概念1", "本书的核心概念2"],
    "application_fields_match": ["本书与哪些应用领域匹配1", "本书与哪些应用领域匹配2"]
  },

}

注意：user_query_intent字段必须严格按照"检索'关键词' ➡️ 意图 ➡️ 推荐类型"的格式，简洁明了。"""
  
    # 新版用户提示词
    user_prompt = f'用户检索词是："{user_query}"。请为书籍《{book_title}》（作者：{book_author}）生成推荐理由。'
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # 开始重试循环
    for attempt in range(max_retries + 1):
        # 检查总超时时间
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            logger.error(f"为《{book_title}》生成理由超时（{timeout}秒），已尝试{attempt}次")
            break
        
        # 如果不是第一次尝试，等待后重试
        if attempt > 0:
            wait_time = retry_delays[attempt - 1] if attempt <= len(retry_delays) else retry_delays[-1]
            logger.warning(f"为《{book_title}》重试第{attempt}次，等待{wait_time}秒...")
            time.sleep(wait_time)
        
        try:
            logger.debug(f"为《{book_title}》发起API调用（尝试 {attempt + 1}/{max_retries + 1}）")
            
            response = dashscope.Generation.call(
                model="qwen-turbo-2025-07-15",
                api_key="sk-0cc8e5c849604b5c9704113abc77be7d",
                messages=messages,
                stream=False,  # 使用非流式调用简化处理
                result_format='message',
                top_p=0.8,
                temperature=0.3,  # 降低温度，让输出更稳定
                enable_search=False
            )
            
            if response.status_code == HTTPStatus.OK:
                raw_content = response.output.choices[0].message.content
                
                # 清理和解析JSON
                # 尝试提取JSON部分
                if '```json' in raw_content:
                    json_start = raw_content.find('```json') + 7
                    json_end = raw_content.find('```', json_start)
                    content = raw_content[json_start:json_end].strip()
                else:
                    content = raw_content.strip()

                reason_data = json.loads(content)
                logger.info(f"✅ 成功为《{book_title}》生成并解析推荐理由（尝试{attempt + 1}次）")
                return reason_data
                
            elif response.status_code == 429:
                # 429限流错误，可以重试
                logger.warning(f"⚠️ 《{book_title}》遇到429限流错误（尝试{attempt + 1}次）")
                if attempt < max_retries:
                    continue  # 继续重试
                else:
                    logger.error(f"❌ 《{book_title}》达到最大重试次数，429错误未解决")
                    break
            else:
                # 其他HTTP错误，不重试
                logger.error(f"❌ 《{book_title}》API请求失败: {response.status_code}, request_id={response.request_id}")
                logger.error(f"错误详情: code={response.code}, message={response.message}")
                break
                
        except json.JSONDecodeError as e:
            # JSON解析失败，可以重试
            logger.error(f"⚠️ 《{book_title}》JSON解析失败（尝试{attempt + 1}次）: {str(e)}")
            if 'content' in locals():
                logger.error(f"原始返回内容: {content[:200]}...")  # 只记录前200字符
            if attempt < max_retries:
                continue  # 继续重试
            else:
                logger.error(f"❌ 《{book_title}》达到最大重试次数，JSON解析仍失败")
                break
                
        except Exception as e:
            # 其他异常，可以重试
            logger.error(f"⚠️ 《{book_title}》发生异常（尝试{attempt + 1}次）: {type(e).__name__} - {str(e)}")
            if attempt < max_retries:
                continue  # 继续重试
            else:
                logger.error(f"❌ 《{book_title}》达到最大重试次数，仍有异常")
                break
    
    # 所有重试都失败，返回默认值
    logger.error(f"❌ 《{book_title}》所有重试失败，返回默认错误值")
    return create_default_reasons(user_query, book_title)

# ===========================================
# 重构旧函数，改为并行调用
# ===========================================

def get_qwen_books_with_reasons(books: list, user_query: str) -> dict:
    """
    调用千问API，为多本书并行生成推荐理由。
    这是重构后的函数，输入为书籍列表。
    """
    logger.info(f"开始为 {len(books)} 本书并行生成推荐理由")
    
    final_books = []
    
    # 使用线程池并行处理API请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(books), 3)) as executor:  # 限制并发数
        # 为每本书提交一个任务
        future_to_book = {executor.submit(get_reason_for_single_book, book, user_query): book for book in books}
        
        for future in concurrent.futures.as_completed(future_to_book):
            book = future_to_book[future]
            try:
                # 获取AI生成的推荐理由
                reason_data = future.result()

                # 应用 trap_focus 覆盖（如果存在）
                reason_data = _apply_trap_focus_override(book, reason_data)
                
                # 组合书籍信息和推荐理由
                book_with_reason = book.copy() # 复制基础信息
                book_with_reason.update(reason_data) # 添加理由
                book_with_reason["cover_url"] = f"https://example.com/cover{len(final_books)+1}.jpg" # 模拟封面
                # 确保星级数据被保留
                if 'match_stars' not in book_with_reason:
                    book_with_reason["match_stars"] = book.get('match_stars', 0)
                
                # 优先使用书籍数据中的自定义借阅热度
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

def get_qwen_books_with_reasons_progressive(books: list, user_query: str, task_id: str, async_tasks: dict) -> dict:
    """
    调用千问API，为多本书并行生成推荐理由。
    支持渐进式更新：每完成一本书就通过回调更新任务状态
    """
    logger.info(f"开始为 {len(books)} 本书并行生成推荐理由（渐进式）")
    
    final_books = []
    
    # 使用线程池并行处理API请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(books), 3)) as executor:
        # 为每本书提交一个任务
        future_to_book = {executor.submit(get_reason_for_single_book, book, user_query): book for book in books}
        
        for future in concurrent.futures.as_completed(future_to_book):
            book = future_to_book[future]
            isbn = book.get('isbn', '')
            
            try:
                # 获取AI生成的推荐理由
                reason_data = future.result()
                
                # 应用 trap_focus 覆盖（如果存在）
                reason_data = _apply_trap_focus_override(book, reason_data)
                
                # 组合书籍信息和推荐理由
                book_with_reason = book.copy() # 复制基础信息
                book_with_reason.update(reason_data) # 添加理由
                book_with_reason["cover_url"] = f"https://example.com/cover{len(final_books)+1}.jpg" # 模拟封面
                # 确保星级数据被保留
                if 'match_stars' not in book_with_reason:
                    book_with_reason["match_stars"] = book.get('match_stars', 0)
                
                # 优先使用书籍数据中的自定义借阅热度
                if 'social_reason' in book and book['social_reason']:
                    book_with_reason["social_reason"] = book['social_reason']
                else:
                    book_with_reason["social_reason"] = create_default_social_reason()
                
                final_books.append(book_with_reason)
                
                # 🔧 关键：实时更新任务状态
                if task_id and task_id in async_tasks:
                    async_tasks[task_id]['completed_books'].append(book_with_reason)
                    async_tasks[task_id]['books_status'][isbn] = {
                        'status': 'completed',
                        'title': book.get('title', '未知书籍')
                    }
                    completed_count = len(async_tasks[task_id]['completed_books'])
                    total_count = async_tasks[task_id]['total_books']
                    async_tasks[task_id]['progress'] = f'正在生成推荐理由... ({completed_count}/{total_count})'
                    logger.info(f"✅ 任务 {task_id}: 《{book.get('title')}》完成 ({completed_count}/{total_count})")
                
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
                
                # 更新失败的书籍状态
                if task_id and task_id in async_tasks:
                    async_tasks[task_id]['completed_books'].append(book_with_reason)
                    async_tasks[task_id]['books_status'][isbn] = {
                        'status': 'failed',
                        'title': book.get('title', '未知书籍')
                    }
                    completed_count = len(async_tasks[task_id]['completed_books'])
                    total_count = async_tasks[task_id]['total_books']
                    async_tasks[task_id]['progress'] = f'正在生成推荐理由... ({completed_count}/{total_count})'

    logger.info(f"已完成所有书籍的推荐理由生成（渐进式）")
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
        "social_reason": create_default_social_reason()
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

def _apply_trap_focus_override(book: dict, reason_data: dict):
    """
    如果设置了 trap_focus，则用其内容覆盖 reason_data 中的相应字段。
    """
    trap_focus = book.get("trap_focus")
    # 如果 trap_focus 不存在或是 "none"，则直接返回原始数据
    if not trap_focus or trap_focus.lower() == "none":
        return reason_data

    logger.info(f"检测到书籍《{book.get('title')}》的 trap_focus，应用覆盖...")

    # 确保 logical_reason 键存在
    if "logical_reason" not in reason_data:
        reason_data["logical_reason"] = {}

    # 解析 trap_focus 字符串
    # 格式支持 "key：value" 或 "key1：value1--key2：value2"
    parts = trap_focus.split('--')
    for part in parts:
        if '：' in part:
            key, value = part.split('：', 1)
            key = key.strip()
            value = value.strip()
            
            # 将值按'、'分割成列表
            values_list = [v.strip() for v in value.split('、')]
            
            if key == "book_core_concepts":
                reason_data["logical_reason"]["book_core_concepts"] = values_list
                logger.info(f"  > [trap] 覆盖 book_core_concepts: {values_list}")
            elif key == "application_fields_match":
                reason_data["logical_reason"]["application_fields_match"] = values_list
                logger.info(f"  > [trap] 覆盖 application_fields_match: {values_list}")

    return reason_data

# ===========================================
# 原有函数保持不变 (保持向后兼容性)
# ===========================================

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
    # 调试：打印完整请求消息
    logger.debug(f"千问API请求消息: {messages}")
    try:
        # 使用原有的API调用配置，获取流式响应迭代器
        responses_iter = dashscope.Generation.call(
            model="qwen-max",
            api_key="sk-0cc8e5c849604b5c9704113abc77be7d",
            messages=messages,
            stream=True,
            result_format='message',  # 将返回结果格式设置为 message
            top_p=0.8,
            temperature=0.7,
            enable_search=False
        )
        # 收集流式响应的完整内容并打印调试信息
        full_content = ""
        responses_list = []
        for response in responses_iter:
            # 保存响应对象以便后续分析
            responses_list.append(response)
            # 调试：打印每个流式响应的原始内容
            logger.debug(
                f"流式响应: request_id={response.request_id}, status={response.status_code}, code={response.code}, message={response.message}, output={response.output}"
            )
            if response.status_code == HTTPStatus.OK and hasattr(response.output, 'choices') and response.output.choices:
                # 从流式响应中提取内容，兼容 delta 或 message.content
                choice = response.output.choices[0]
                content_chunk = None
                # OpenAI Delta 风格
                if isinstance(choice, dict):
                    delta = choice.get('delta', {})
                    if 'content' in delta:
                        content_chunk = delta['content']
                # dashscope message 风格
                if content_chunk is None and hasattr(choice, 'message'):
                    msg = choice.message
                    if isinstance(msg, dict):
                        content_chunk = msg.get('content')
                    else:
                        content_chunk = getattr(msg, 'content', None)
                if content_chunk:
                    full_content += content_chunk
        if full_content:
            logger.info(f"千问API返回建议: {full_content}")
            return full_content
        else:
            # 调试：打印所有流式响应列表
            logger.error(f"千问API返回空内容，流式响应详情: {responses_list}")
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
    # 测试新的接口
    test_books = [
        {"title": "Python编程从入门到实践", "author": "埃里克·马瑟斯"},
        {"title": "算法导论", "author": "托马斯·科尔曼"},
        {"title": "深度学习", "author": "伊恩·古德费洛"}
    ]
    
    print("🧪 测试单本书推荐理由生成...")
    single_result = get_reason_for_single_book(test_books[0], "python编程")
    print(f"单本书测试结果: {single_result}")
    
    print("\n🧪 测试多本书并行推荐理由生成...")
    multiple_result = get_qwen_books_with_reasons(test_books, "编程学习")
    print(f"多本书测试结果: {multiple_result}")