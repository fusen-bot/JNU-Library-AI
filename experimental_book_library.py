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
            "match_stars": 3,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.85},
                    {"name": "物联网工程学院", "rate": 0.72},
                    {"name": "理学院", "rate": 0.31},
                    {"name": "商学院", "rate": 0.12}
                ],
                "trend": "本书为我校工科类核心参考书，常年位居技术类书籍借阅榜首，尤其在考研和保研季借阅量激增，是计算机相关专业学生的必读经典。"
            }
        },
        {
            "title": "计算机组成与设计：硬件/软件接口",
            "author": "David A. Patterson, John L. Hennessy",
            "isbn": "9787111641359",
            "match_stars": 2,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.78},
                    {"name": "物联网工程学院", "rate": 0.65},
                    {"name": "理学院", "rate": 0.28},
                    {"name": "商学院", "rate": 0.08}
                ],
                "trend": "硬件架构经典教材，在计算机体系结构课程期间借阅量显著上升，是系统设计相关课程的重要参考书。"
            }
        },
        {
            "title": "编码：隐匿在计算机软硬件背后的语言",
            "author": "Charles Petzold",
            "isbn": "9787121181184",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.45},
                    {"name": "理学院", "rate": 0.32},
                    {"name": "设计学院", "rate": 0.18},
                    {"name": "商学院", "rate": 0.05}
                ],
                "trend": "计算机科普经典，适合初学者理解计算机基本原理，在新生入学季借阅较多。"
            }
        }
    ],
    "算法科学": [
        {
            "title": "算法导论",
            "author": "Thomas H. Cormen, Charles E. Leiserson",
            "isbn": "9787111187776",
            "match_stars": 3,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.91},
                    {"name": "数字媒体学院", "rate": 0.68},
                    {"name": "理学院", "rate": 0.45},
                    {"name": "物联网工程学院", "rate": 0.76}
                ],
                "trend": "该书是算法竞赛和技术面试的热门参考书，借阅量在每年春招和秋招季节达到峰值，深受编程爱好者和求职学生青睐。"
            }
        },
        {
            "title": "算法（第4版）",
            "author": "Robert Sedgewick, Kevin Wayne",
            "isbn": "9787115293800",
            "match_stars": 2,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.73},
                    {"name": "数字媒体学院", "rate": 0.54},
                    {"name": "理学院", "rate": 0.38},
                    {"name": "物联网工程学院", "rate": 0.62}
                ],
                "trend": "实用算法教材，适合快速掌握常用算法实现，在数据结构课程期间借阅量较高。"
            }
        },
        {
            "title": "学习JavaScript数据结构与算法",
            "author": "Loiane Groner",
            "isbn": "9787115458315",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "数字媒体学院", "rate": 0.67},
                    {"name": "计算机科学与工程学院", "rate": 0.42},
                    {"name": "设计学院", "rate": 0.25},
                    {"name": "商学院", "rate": 0.15}
                ],
                "trend": "前端开发必备，在Web开发相关课程和实习准备期间借阅火爆。"
            }
        }
    ],
    "Java": [
        {
            "title": "Java核心技术",
            "author": "Cay S. Horstmann",
            "isbn": "9787111213826",
            "match_stars": 3,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.83},
                    {"name": "商学院", "rate": 0.34},
                    {"name": "设计学院", "rate": 0.28},
                    {"name": "物联网工程学院", "rate": 0.67}
                ],
                "trend": "Java作为企业级开发的主流语言，这本书在实习季和毕业设计期间借阅火爆，是学生踏入软件开发行业的重要参考。"
            }
        },
        {
            "title": "深入理解Java虚拟机",
            "author": "周志明",
            "isbn": "9787111608291",
            "match_stars": 2,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.74},
                    {"name": "物联网工程学院", "rate": 0.58},
                    {"name": "理学院", "rate": 0.22},
                    {"name": "商学院", "rate": 0.08}
                ],
                "trend": "Java进阶必读，在技术面试准备期和高级开发课程中借阅量显著上升。"
            }
        },
        {
            "title": "Effective Java中文版",
            "author": "Joshua Bloch",
            "isbn": "9787111604088",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.65},
                    {"name": "物联网工程学院", "rate": 0.48},
                    {"name": "商学院", "rate": 0.18},
                    {"name": "理学院", "rate": 0.12}
                ],
                "trend": "Java编程最佳实践指南，深受有一定Java基础的学生欢迎，在代码质量要求较高的项目期间借阅较多。"
            }
        }
    ],
    "python": [
        {
            "title": "Python编程：从入门到实践",
            "author": "Eric Matthes",
            "isbn": "9787115428028",
            "match_stars": 3,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.89},
                    {"name": "数字媒体学院", "rate": 0.75},
                    {"name": "理学院", "rate": 0.68},
                    {"name": "商学院", "rate": 0.45}
                ],
                "trend": "Python入门首选教材，在新生程序设计课程和数据分析相关课程期间借阅量极高，是跨专业学生学习编程的热门选择。"
            }
        },
        {
            "title": "流畅的Python",
            "author": "Luciano Ramalho",
            "isbn": "9787115453655",
            "match_stars": 2,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.71},
                    {"name": "数字媒体学院", "rate": 0.58},
                    {"name": "理学院", "rate": 0.43},
                    {"name": "物联网工程学院", "rate": 0.56}
                ],
                "trend": "Python进阶经典，适合有一定基础的学生深入学习Python特性，在高级编程课程期间借阅较多。"
            }
        },
        {
            "title": "Python学习手册",
            "author": "Mark Lutz",
            "isbn": "9787564147942",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "计算机科学与工程学院", "rate": 0.52},
                    {"name": "理学院", "rate": 0.48},
                    {"name": "数字媒体学院", "rate": 0.35},
                    {"name": "商学院", "rate": 0.28}
                ],
                "trend": "Python全面参考手册，适合需要系统学习Python语法的学生，在考试复习期间借阅量上升。"
            }
        }
    ],
    "未来教育": [
        {
            "title": "未来教育 : 教育改革的未来",
            "author": "赵慧著",
            "isbn": "9787511569684",
            "match_stars": 3,
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.92},
                    {"name": "人文学院", "rate": 0.56},
                    {"name": "商学院", "rate": 0.34},
                    {"name": "计算机科学与工程学院", "rate": 0.28}
                ],
                "trend": "教育改革理论前沿，在教育学硕士论文写作和教育政策研究期间借阅量突出，是教育工作者和研究者的重要参考。"
            }
        },
        {
            "title": "超级AI与未来教育",
            "author": "李骏翼",
            "isbn": "9787500174943",
            "match_stars": 2,
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.78},
                    {"name": "计算机科学与工程学院", "rate": 0.65},
                    {"name": "人文学院", "rate": 0.42},
                    {"name": "数字媒体学院", "rate": 0.58}
                ],
                "trend": "AI教育应用的前站性研究，在智能教育技术相关课程和项目中广受关注。"
            }
        },
        {
            "title": "人工智能与未来教育",
            "author": "潘巧明",
            "isbn": "9787301339381",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.68},
                    {"name": "计算机科学与工程学院", "rate": 0.45},
                    {"name": "人文学院", "rate": 0.38},
                    {"name": "商学院", "rate": 0.22}
                ],
                "trend": "人工智能教育应用入门读物，适合初步了解AI教育融合的学生和教师。"
            }
        }
    ],
    "教育变革": [
        {
            "title": "澳门学校课程与教育变革",
            "author": "郭晓明",
            "isbn": "9787511569684",
            "match_stars": 2,
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.84},
                    {"name": "人文学院", "rate": 0.52},
                    {"name": "商学院", "rate": 0.38},
                    {"name": "设计学院", "rate": 0.31}
                ],
                "trend": "教育学专业必读，在教育理论课程和学术研究中广受关注，特别是在教育改革相关论文写作期间。"
            }
        },
        {
            "title": "新科技革命背景下的工业设计教育变革",
            "author": "吴志军",
            "isbn": "9787569715507",
            "match_stars": 2,
            "social_reason": {
                "departments": [
                    {"name": "设计学院", "rate": 0.91},
                    {"name": "教育学院", "rate": 0.63},
                    {"name": "工业设计学院", "rate": 0.87},
                    {"name": "数字媒体学院", "rate": 0.54}
                ],
                "trend": "设计教育专业书籍，在设计理论和教育学课程中借阅量较高，适合研究新技术对设计教育影响的学者。"
            }
        },
        {   
            "title": "批判性媒体素养指南：媒体参与和教育变革",
            "author": "杰夫沙尔",
            "isbn": "9787559868848",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "数字媒体学院", "rate": 0.76},
                    {"name": "教育学院", "rate": 0.58},
                    {"name": "人文学院", "rate": 0.65},
                    {"name": "商学院", "rate": 0.32}
                ],
                "trend": "媒体素养教育重要参考，在新媒体相关课程和批判性思维教育研究中广受欢迎。"
            }
        }
    ],
    "人工智能教育": [
        {
            "title": "人工智能+教育 : 人工智能时代, 未来学校教育的机遇、挑战与重塑路径",
            "author": "王立辉",
            "isbn": "9787515838960",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.88},
                    {"name": "计算机科学与工程学院", "rate": 0.56},
                    {"name": "人文学院", "rate": 0.43},
                    {"name": "管理学院", "rate": 0.37}
                ],
                "trend": "AI教育整合的全面指南，在教育技术相关研究和智能教育项目中广受参考。"
            }
        },
        {
            "title": "人工智能教育应用理论与实践",
            "author": "李福华",
            "isbn": "9787030799159",
            "match_stars": 3,
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.95},
                    {"name": "计算机科学与工程学院", "rate": 0.73},
                    {"name": "数字媒体学院", "rate": 0.62},
                    {"name": "人文学院", "rate": 0.48}
                ],
                "trend": "AI教育应用的权威教材，在智能教育系统开发和教育技术研究中频繁被引用，是相关专业的核心参考书。"
            }
        },
        {   
            "title": "AI教育基础：图形化编程的拓展应用",
            "author": "中国人民大学出版社",
            "isbn": "9787300305899",
            "match_stars": 1,
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.72},
                    {"name": "计算机科学与工程学院", "rate": 0.58},
                    {"name": "数字媒体学院", "rate": 0.51},
                    {"name": "设计学院", "rate": 0.34}
                ],
                "trend": "AI教育入门实践教材，适合初学者了解AI教育的基础原理和应用方法。"
            }
        }     
    ],
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