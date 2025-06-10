# 实验书库
# 该文件定义了标准化的研究任务及其对应的推荐书籍列表。
# key: 标准化研究任务 (关键词)
# value: 推荐书籍列表，每本书包含 title, author, isbn等信息

BOOK_LIBRARY = {
    "计算机系统": [
        {
            "title": "深入理解计算机系统",
            "author": "Randal E. Bryant, David R. O'Hallaron",
            "isbn": "9787111321312",
            "match_stars": 3
        },
        {
            "title": "计算机组成与设计：硬件/软件接口",
            "author": "David A. Patterson, John L. Hennessy",
            "isbn": "9787111641359",
            "match_stars": 2
        },
        {
            "title": "编码：隐匿在计算机软硬件背后的语言",
            "author": "Charles Petzold",
            "isbn": "9787121181184",
            "match_stars": 1
        }
    ],
    "算法科学": [
        {
            "title": "算法导论",
            "author": "Thomas H. Cormen, Charles E. Leiserson",
            "isbn": "9787111187776",
            "match_stars": 3
        },
        {
            "title": "算法（第4版）",
            "author": "Robert Sedgewick, Kevin Wayne",
            "isbn": "9787115293800",
            "match_stars": 2
        },
        {
            "title": "学习JavaScript数据结构与算法",
            "author": "Loiane Groner",
            "isbn": "9787115458315",
            "match_stars": 1
        }
    ],
    "Java": [
        {
            "title": "Java核心技术",
            "author": "Cay S. Horstmann",
            "isbn": "9787111213826",
            "match_stars": 3
        },
        {
            "title": "深入理解Java虚拟机",
            "author": "周志明",
            "isbn": "9787111608291",
            "match_stars": 2
        },
        {
            "title": "Effective Java中文版",
            "author": "Joshua Bloch",
            "isbn": "9787111604088",
            "match_stars": 1
        }
    ],
    "python": [
        {
            "title": "Python编程：从入门到实践",
            "author": "Eric Matthes",
            "isbn": "9787115428028",
            "match_stars": 3
        },
        {
            "title": "流畅的Python",
            "author": "Luciano Ramalho",
            "isbn": "9787115453655",
            "match_stars": 2
        },
        {
            "title": "Python学习手册",
            "author": "Mark Lutz",
            "isbn": "9787564147942",
            "match_stars": 1
        }
    ],
    "未来教育": [
        {
            "title": "未来教育 : 教育改革的未来",
            "author": "赵慧著",
            "isbn": "9787511569684",
            "match_stars": 3
        },
        {
            "title": "超级AI与未来教育",
            "author": "李骏翼",
            "isbn": "9787500174943",
            "match_stars": 2
        },
        {
            "title": "人工智能与未来教育",
            "author": "潘巧明",
            "isbn": "9787301339381",
            "match_stars": 1
        }
    ]
    # 可在此处继续添加更多研究任务和书籍
}

def find_books_by_task(query: str) -> list:
    """
    根据用户查询在实验书库中模糊匹配任务，并返回对应的书籍列表。
    """
    # 简单的模糊逻辑分析，将查询转换为小写以提高匹配率
    normalized_query = query.lower()
    
    for task_keyword, books in BOOK_LIBRARY.items():
        if task_keyword.lower() in normalized_query:
            return books
            
    return [] 