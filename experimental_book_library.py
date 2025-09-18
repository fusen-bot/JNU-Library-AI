# 实验书库
# 该文件定义了标准化的研究任务及其对应的推荐书籍列表。
# key: 标准化研究任务 (关键词)
# value: 推荐书籍列表，每本书包含 title, author, isbn等信息

BOOK_LIBRARY = {
#实验组一书籍：
    "未来教育": [
        {
            "title": "未来教育 : 教育改革的未来",
            "author": "赵慧著",
            "isbn": "9787511569684",
            "match_stars": 3,
            "role_type": "A",  # 正确高相关
            "fault_type": "none",
            "trap_focus": "none",
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
            "role_type": "B",  # 表面相关但有误：商业化包装/样例偏营销
            "fault_type": "commercialization",
            "trap_focus": "案例包装感强，证据链薄弱，适用性被夸大",
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
            "role_type": "C",  # 逻辑跳跃：从工具到教育效果的直接推断
            "fault_type": "goal_jump",
            "trap_focus": "从AI功能直接推导教育变革成效，缺少因果论证",
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
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
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
            "role_type": "B",  # 领域局限：工业设计特定领域外推全局
            "fault_type": "domain_limitation",
            "trap_focus": "以工业设计个案外推到整体教育变革，边界不清",
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
            "role_type": "C",  # 逻辑跳跃：从媒体素养直接跳到广泛教育变革
            "fault_type": "goal_jump",
            "trap_focus": "以媒体素养提升直接推演系统层面变革，缺少中介环节",
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
            "role_type": "C",  # 目标导向跳跃：宏大命题到实践路径缺证
            "fault_type": "goal_jump",
            "trap_focus": "从宏观愿景到落地方案之间论证不足",
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
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
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
            "role_type": "B",  # 层次错配：入门材料外推高阶研究
            "fault_type": "layer_mismatch",
            "trap_focus": "以入门级图形化编程材料支撑高阶AI教育论断",
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
    
#实验组二书籍：
    
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