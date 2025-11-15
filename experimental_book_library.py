# 实验书库
# 该文件定义了标准化的研究任务及其对应的推荐书籍列表。
# key: 标准化研究任务 (关键词)
# value: 推荐书籍列表，每本书包含 title, author, isbn等信息

BOOK_LIBRARY = {
#旧实验组书籍：
    "未来教育": [
        {
            "title": "未来教育 : 教育改革的未来",
            "author": "赵慧著",
            "isbn": "9787511569684",
            "match_stars": 1,
            "role_type": "A",  # 正确高相关
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.89},
                    {"name": "人文学院", "rate": 0.72},
                    {"name": "商学院", "rate": 0.45},
                    {"name": "计算机科学与工程学院", "rate": 0.38}
                ],
                "trend": "教育改革理论前沿，在教育学硕士论文写作和教育政策研究期间借阅量突出，是教育工作者和研究者的重要参考。"
            }
        },
        {
            "title": "超级AI与未来教育",
            "author": "李骏翼",
            "isbn": "9787500174943",
            "match_stars": 3,
            "role_type": "B",  # 表面相关但有误：商业化包装/样例偏营销
            "fault_type": "commercialization",
            "trap_focus": "案例包装感强，证据链薄弱，适用性被夸大",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.81},
                    {"name": "计算机科学与工程学院", "rate": 0.74},
                    {"name": "人文学院", "rate": 0.53},
                    {"name": "数字媒体学院", "rate": 0.66}
                ],
                "trend": "AI教育应用的前站性研究，在智能教育技术相关课程和项目中广受关注。"
            }
        },
        {
            "title": "人工智能与未来教育",
            "author": "潘巧明",
            "isbn": "9787301339381",
            "match_stars": 4,
            "role_type": "C",  # 逻辑跳跃：从工具到教育效果的直接推断
            "fault_type": "goal_jump",
            "trap_focus": "从AI功能直接推导教育变革成效，缺少因果论证",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.51},
                    {"name": "计算机科学与工程学院", "rate": 0.39},
                    {"name": "人文学院", "rate": 0.28},
                    {"name": "商学院", "rate": 0.19}
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
            "match_stars": 1,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.92},
                    {"name": "人文学院", "rate": 0.68},
                    {"name": "商学院", "rate": 0.47},
                    {"name": "设计学院", "rate": 0.41}
                ],
                "trend": "教育学专业必读，在教育理论课程和学术研究中广受关注，特别是在教育改革相关论文写作期间。"
            }
        },
        {
            "title": "新科技革命背景下的工业设计教育变革",
            "author": "吴志军",
            "isbn": "9787569715507",
            "match_stars": 3,
            "role_type": "B",  # 领域局限：工业设计特定领域外推全局
            "fault_type": "domain_limitation",
            "trap_focus": "以工业设计个案外推到整体教育变革，边界不清",
            "social_reason": {
                "departments": [
                    {"name": "设计学院", "rate": 0.88},
                    {"name": "教育学院", "rate": 0.76},
                    {"name": "工业设计学院", "rate": 0.83},
                    {"name": "数字媒体学院", "rate": 0.61}
                ],
                "trend": "设计教育专业书籍，在设计理论和教育学课程中借阅量较高，适合研究新技术对设计教育影响的学者。"
            }
        },
        {   
            "title": "批判性媒体素养指南：媒体参与和教育变革",
            "author": "杰夫沙尔",
            "isbn": "9787559868848",
            "match_stars": 4,
            "role_type": "C",  # 逻辑跳跃：从媒体素养直接跳到广泛教育变革
            "fault_type": "goal_jump",
            "trap_focus": "以媒体素养提升直接推演系统层面变革，缺少中介环节",
            "social_reason": {
                "departments": [
                    {"name": "数字媒体学院", "rate": 0.59},
                    {"name": "教育学院", "rate": 0.44},
                    {"name": "人文学院", "rate": 0.52},
                    {"name": "商学院", "rate": 0.26}
                ],
                "trend": "媒体素养教育重要参考，在新媒体相关课程和批判性思维教育研究中广受欢迎。"
            }
        }
    ],

#实验组二书籍：
    "----": [
        {
            "title": "教育变革的理念与实践",
            "author": "刘明",
            "isbn": "9787301256724",
            "match_stars": 1,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.91},
                    {"name": "人文学院", "rate": 0.73},
                    {"name": "管理学院", "rate": 0.49},
                    {"name": "社会学院", "rate": 0.42}
                ],
                "trend": "系统性探讨教育变革的理论与实施路径，是现代教育改革课程的重要参考文献。"
            }
        },
        {
            "title": "教育系统重构：政策、技术与创新",
            "author": "苏伟",
            "isbn": "9787010194652",
            "match_stars": 3,
            "role_type": "B",
            "fault_type": "policy_biased",
            "trap_focus": "过度依赖政策指引，缺少基层案例分析",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.82},
                    {"name": "政策与管理学院", "rate": 0.67},
                    {"name": "公共管理学院", "rate": 0.58},
                    {"name": "信息学院", "rate": 0.38}
                ],
                "trend": "政策导向强烈的教育变革教材，适合教育管理及教育改革方向学习。"
            }
        },
        {
            "title": "课堂创新与未来学校",
            "author": "宋远",
            "isbn": "9787303221560",
            "match_stars": 4,
            "role_type": "C",
            "fault_type": "innovation_jump",
            "trap_focus": "直接从课堂创新嫁接到制度变革，过程论证不够",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.48},
                    {"name": "师范学院", "rate": 0.36},
                    {"name": "人文学院", "rate": 0.29},
                    {"name": "艺术设计学院", "rate": 0.18}
                ],
                "trend": "以课堂微观改革为核心切入未来教育实践，适合创新教学案例探讨。"
            }
        }
    ],
    "人工智能伦理": [
        {
            "title": "人工智能伦理困境与突破",
            "author": "周翔",
            "isbn": "9787576815535",
            "match_stars": 3,
            "role_type": "B",
            "fault_type": "insufficient_argument",
            "trap_focus": "伦理分析不足以支撑全面社会责任讨论",
            "social_reason": {
                "departments": [
                    {"name": "社会学院", "rate": 0.86},
                    {"name": "法学院", "rate": 0.74},
                    {"name": "计算机科学与工程学院", "rate": 0.57},
                    {"name": "教育学院", "rate": 0.46}
                ],
                "trend": "人工智能伦理在社会各领域中的应用与挑战，强调跨学科视角。"
            }
        },
        {
            "title": "人工智能传播伦理与治理",
            "author": "杨旦修",
            "isbn": "9787522839080",
            "match_stars": 1,
            "role_type": "A",  # 高相关
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "社会学院", "rate": 0.95},
                    {"name": "信息科学技术学院", "rate": 0.63},
                    {"name": "法学院", "rate": 0.51},
                    {"name": "教育学院", "rate": 0.39}
                ],
                "trend": "深度剖析人工智能在现实社会中引发的伦理议题，强调理论与实践结合。"
            }
        },
        {
            "title": "负责任的人工智能何以可能?",
            "author": "张明",
            "isbn": "9787313283603",
            "match_stars": 4,
            "role_type": "C",  # 法律视角局限，伦理宽泛
            "fault_type": "oversimplification",
            "trap_focus": "过于强调法律规制，伦理维度阐释不足",
            "social_reason": {
                "departments": [
                    {"name": "人文学院", "rate": 0.61},
                    {"name": "社会学院", "rate": 0.38},
                    {"name": "计算机科学与工程学院", "rate": 0.24},
                    {"name": "教育学院", "rate": 0.16}
                ],
                "trend": "法律政策路径主导，适合人工智能合规与伦理监管相关研究。"
            }
        }
    ],

    #旧实验组三：
    "智慧校园": [
        {
            "title": "智慧校园建设研究",
            "author": "李兆延",
            "isbn": "9787517076742",
            "match_stars": 3,
            "role_type": "B",
            "fault_type": "scope_limited",
            "trap_focus": "仅关注设施智能化，教学应用不足",
            "social_reason": {
                "departments": [
                    {"name": "教育技术学院", "rate": 0.78},
                    {"name": "信息学院", "rate": 0.65},
                    {"name": "管理学院", "rate": 0.42},
                    {"name": "艺术设计学院", "rate": 0.31}
                ],
                "trend": "强调智慧空间和物联网建设，数字基础布局讨论较多。"
            }
        },
        {
            "title": "数字化校园:理念、设计与实现",
            "author": "刘邦奇",
            "isbn": "9787312033926",
            "match_stars": 1,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "信息学院", "rate": 0.92},
                    {"name": "教育技术学院", "rate": 0.76},
                    {"name": "管理学院", "rate": 0.68},
                    {"name": "艺术设计学院", "rate": 0.44}
                ],
                "trend": "收录各地智慧校园落地案例，适合管理与技术融合方向。"
            }
        },
        {
            "title": "5G+智慧教育:重塑未来教育新图景",
            "author": "王红军",
            "isbn": "9787115589095",
            "match_stars": 4,
            "role_type": "C",
            "fault_type": "theory_bias",
            "trap_focus": "以技术预言为主，实际操作性弱",
            "social_reason": {
                "departments": [
                    {"name": "教育技术学院", "rate": 0.47},
                    {"name": "管理学院", "rate": 0.35},
                    {"name": "信息学院", "rate": 0.39},
                    {"name": "艺术设计学院", "rate": 0.22}
                ],
                "trend": "聚焦未来趋势预测，适合理论研究参考。"
            }
        }
    ],

    "教师能力": [
        {
            "title": "素养时代的教师专业成长",
            "author": "汪瑞林",
            "isbn": "9787576027679",
            "match_stars": 1,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.81},
                    {"name": "师范学院", "rate": 0.73},
                    {"name": "继续教育学院", "rate": 0.31},
                    {"name": "心理学院", "rate": 0.32}
                ],
                "trend": "关注教师基本素质与新技术融合能力培养。"
            }
        },
        {
            "title": "信息化教学技能实践与应用",
            "author": "王颖",
            "isbn": "9787513006170",
            "match_stars": 4,
            "role_type": "C",
            "fault_type": "goal_jump",
            "trap_focus": "混合了学生素养讨论，界限模糊",
            "social_reason": {
                "departments": [
                    {"name": "师范学院", "rate": 0.59},
                    {"name": "教育学院", "rate": 0.23},
                    {"name": "心理学院", "rate": 0.42},
                    {"name": "继续教育学院", "rate": 0.17}
                ],
                "trend": "对数字素养提及较多，但系统性略有欠缺。"
            }
        },
        {
            "title": "信息化教学技术与方法:",
            "author": "周效章",
            "isbn": "9787109271982",
            "match_stars": 3,
            "role_type": "B",
            "fault_type": "oversimplification",
            "trap_focus": "能力分类粗略，缺少具体发展路径",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.41},
                    {"name": "师范学院", "rate": 0.69},
                    {"name": "心理学院", "rate": 0.18},
                    {"name": "继续教育学院", "rate": 0.34}
                ],
                "trend": "探讨教师能力构成，但案例和实践辅证偏少。"
            }
        }
    ],
    #测试书籍检索住0：
    "人工智能教育": [
        {
            "title": "人工智能+教育 : 人工智能时代, 未来学校教育的机遇、挑战与重塑路径",
            "author": "王立辉",
            "isbn": "9787515838960",
            "match_stars": 4,
            "role_type": "C",  # 目标导向跳跃：宏大命题到实践路径缺证
            "fault_type": "goal_jump",
            "trap_focus": "从宏观愿景到落地方案之间论证不足",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.56},
                    {"name": "计算机科学与工程学院", "rate": 0.42},
                    {"name": "人文学院", "rate": 0.33},
                    {"name": "管理学院", "rate": 0.27},
                    {"name": "其他学院", "rate": 0.28}
                ],
                "trend": "AI教育整合的全面指南，在教育技术相关研究和智能教育项目中广受参考。"
            }
        },
        {
            "title": "人工智能教育应用理论与实践",
            "author": "李福华",
            "isbn": "9787030799159",
            "match_stars": 1,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.94},
                    {"name": "计算机科学与工程学院", "rate": 0.85},
                    {"name": "数字媒体学院", "rate": 0.71},
                    {"name": "人文学院", "rate": 0.58},
                    {"name": "其他学院", "rate": 0.57}
                ],
                "trend": "AI教育应用的权威教材，在智能教育系统开发和教育技术研究中频繁被引用，是相关专业的核心参考书。"
            }
        },
        {   
            "title": "AI教育基础：图形化编程的拓展应用",
            "author": "中国人民大学出版社",
            "isbn": "9787300305899",
            "match_stars": 3,
            "role_type": "B",  # 层次错配：入门材料外推高阶研究
            "fault_type": "layer_mismatch",
            "trap_focus": "以入门级图形化编程材料支撑高阶AI教育论断",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.79},
                    {"name": "计算机科学与工程学院", "rate": 0.68},
                    {"name": "数字媒体学院", "rate": 0.62},
                    {"name": "设计学院", "rate": 0.45},
                    {"name": "其他学院", "rate": 0.44}
                ],
                "trend": "AI教育入门实践教材，适合初学者了解AI教育的基础原理和应用方法。"
            }
        }     
    ],

    "AI教育": [
        {
            "title": "人工智能+教育 : 人工智能时代, 未来学校教育的机遇、挑战与重塑路径",
            "author": "王立辉",
            "isbn": "9787515838960",
            "match_stars": 4,
            "role_type": "C",  # 目标导向跳跃：宏大命题到实践路径缺证
            "fault_type": "goal_jump",
            "trap_focus": "从宏观愿景到落地方案之间论证不足",
            #上面这几个字段的作用是什么
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.54},
                    {"name": "计算机科学与工程学院", "rate": 0.41},
                    {"name": "人文学院", "rate": 0.31},
                    {"name": "管理学院", "rate": 0.25},
                    {"name": "其他学院", "rate": 0.26}
                ],
                "trend": "AI教育整合的全面指南，在教育技术相关研究和智能教育项目中广受参考。"
            }
        },
        {
            "title": "人工智能教育应用理论与实践",
            "author": "李福华",
            "isbn": "9787030799159",
            "match_stars": 1,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.93},
                    {"name": "计算机科学与工程学院", "rate": 0.84},
                    {"name": "数字媒体学院", "rate": 0.69},
                    {"name": "人文学院", "rate": 0.56},
                    {"name": "其他学院", "rate": 0.55}
                ],
                "trend": "AI教育应用的权威教材，在智能教育系统开发和教育技术研究中频繁被引用，是相关专业的核心参考书。"
            }
        },
        {   
            "title": "AI教育基础：图形化编程的拓展应用",
            "author": "中国人民大学出版社",
            "isbn": "9787300305899",
            "match_stars": 3,
            "role_type": "B",  # 层次错配：入门材料外推高阶研究
            "fault_type": "layer_mismatch",
            "trap_focus": "以入门级图形化编程材料支撑高阶AI教育论断",
            "social_reason": {
                "departments": [
                    {"name": "教育学院", "rate": 0.77},
                    {"name": "计算机科学与工程学院", "rate": 0.66},
                    {"name": "数字媒体学院", "rate": 0.59},
                    {"name": "设计学院", "rate": 0.43},
                    {"name": "其他学院", "rate": 0.42}
                ],
                "trend": "AI教育入门实践教材，适合初学者了解AI教育的基础原理和应用方法。"
            }
        }     
    ],


    #最终实验检索组1：职业发展与人生规划
    
    "职业发展": [
        {
            "title": "大学生创业基础",
            "author": "何云海",
            "isbn": "9787115320834",
            "match_stars": 3,
            "role_type": "B",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.60},
                    {"name": "人文学院", "rate": 0.62},
                    {"name": "商学院", "rate": 0.61},
                    {"name": "人工智能与计算机学院", "rate": 0.58},
                    {"name": "其他学院", "rate": 0.57}
                ],
                "trend": "大学生创业基础的权威教材，适合大学生创业和就业指导。"
            }
        },
        {
            "title": "大学生职业发展与就业指导",
            "author": "陈光耀",
            "isbn": "9787303152841",
            "match_stars": 4,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.60},
                    {"name": "人文学院", "rate": 0.58},
                    {"name": "商学院", "rate": 0.61},
                    {"name": "人工智能与计算机学院", "rate": 0.59},
                    {"name": "其他学院", "rate": 0.58}

                ],
                "trend": "大学生职业发展与就业指导的权威教材，适合大学生职业规划和就业指导。"
            }
        },
        {
            "title": "我的工作我做主",
            "author": "知墨",
            "isbn": "9787560969985",
            "match_stars": 3,
            "role_type": "C",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.60},
                    {"name": "人文学院", "rate": 0.62},
                    {"name": "商学院", "rate": 0.61},
                    {"name": "人工智能与计算机学院", "rate": 0.59},
                    {"name": "其他学院", "rate": 0.58}
                    
                ],
                "trend": "我的工作我做主的权威教材，适合大学生职业规划和就业指导。"
            }
        }

    ],

    #最终书籍检索组2：
    "高效学习": [
        {
            "title": "高效学习脑科学",
            "author": "张三",
            "isbn": "9787511569684",
            "match_stars": 4,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.89},
                    {"name": "人文学院", "rate": 0.93},
                    {"name": "商学院", "rate": 0.91},
                    {"name": "人工智能与计算机学院", "rate": 0.94},
                    {"name": "其他学院", "rate": 0.92}
                ],
                "trend": "高效学习脑科学的权威教材，适合大学生学习方法和学习指导。"
            }
        },
        {
            "title": "如何用Kindle高效学习",
            "author": "直树桑",
            "isbn": "9787111618430",
            "match_stars": 1,
            "role_type": "B",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.37},
                    {"name": "人文学院", "rate": 0.39},
                    {"name": "商学院", "rate": 0.41},
                    {"name": "人工智能与计算机学院", "rate": 0.39},
                    {"name": "其他学院", "rate": 0.38}

                ],
                "trend": "高效学习方法的权威教材，适合大学生学习方法和学习指导。"
            }
        },
        {
            "title": "学习天性",
            "author": "博勒",
            "isbn": "9787505753907",
            "match_stars": 2,
            "role_type": "C",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.28},
                    {"name": "人文学院", "rate": 0.29},
                    {"name": "商学院", "rate": 0.31},
                    {"name": "人工智能与计算机学院", "rate": 0.30},
                    {"name": "其他学院", "rate": 0.29}
                ],
                "trend": "高效学习方法的权威教材，适合大学生学习方法和学习指导。"
            }
        }
    ],
    #最终书籍检索组3：
    "心理健康": [
        {
            "title": "大学生心理健康",
            "author": "李俊晓",
            "isbn": "9787576512748",
            "match_stars": 4,
            "role_type": "B",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.20},
                    {"name": "人文学院", "rate": 0.22},
                    {"name": "商学院", "rate": 0.19},
                    {"name": "人工智能与计算机学院", "rate": 0.19},
                    {"name": "其他学院", "rate": 0.18}
                ],
                "trend": "适合大学生心理健康和学习方法和学习指导。"
            }
        },
        {
            "title": "境由心造:人生百态背后的心理真相",
            "author": "季龙妹",
            "isbn": "9787545820218",
            "match_stars": 1,
            "role_type": "B",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.87},
                    {"name": "人文学院", "rate": 0.92},
                    {"name": "商学院", "rate": 0.86},
                    {"name": "人工智能与计算机学院", "rate": 0.89},
                    {"name": "其他学院", "rate": 0.88}
                ],
                "trend": "适合大学生心理健康和学习方法和学习指导。"
            }
        },
        {
            "title": "心理健康教育改革",
            "author": "徐晓虹",
            "isbn": "9787551624886",
            "match_stars": 2,
            "role_type": "B",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.60},
                    {"name": "人文学院", "rate": 0.65},
                    {"name": "商学院", "rate": 0.61},
                    {"name": "人工智能与计算机学院", "rate": 0.59},
                    {"name": "其他学院", "rate": 0.58}
                ],
                "trend": "学习力的权威教材，适合大学生学习方法和学习指导。"
            }
        }

    ],
    #最终书籍检索组4：此组后面开始内容有陷阱设置
    "健康生活": [
        {
            "title": "健康生活处方",
            "author": "肖特",
            "isbn": "9787504695635",
            "match_stars": 3,
            "role_type": "C",
            "fault_type": "none",
            "trap_focus": "application_fields_match：个人日常体育运动项目、热门身体锻炼方式",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.60},
                    {"name": "人文学院", "rate": 0.62},
                    {"name": "商学院", "rate": 0.61},
                    {"name": "人工智能与计算机学院", "rate": 0.59},
                    {"name": "其他学院", "rate": 0.58}
                ],
                "trend": "适合大学生健康生活和学习方法和学习指导。"
            }
        },
        {
            "title": "健康生活方式",
            "author": "黄萌",
            "isbn": "9787521413151",
            "match_stars": 3,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.59},
                    {"name": "人文学院", "rate": 0.62},
                    {"name": "商学院", "rate": 0.53},
                    {"name": "人工智能与计算机学院", "rate": 0.61},
                    {"name": "其他学院", "rate": 0.60}
                ],
                "trend": "适合大学生健康生活和学习方法和学习指导。"
            }
        },
        {
            "title": "中国城市健康生活报告",
            "author": "黄钢",
            "isbn": "9787520170574",
            "match_stars": 3,
            "role_type": "C",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.59},
                    {"name": "人文学院", "rate": 0.62},
                    {"name": "商学院", "rate": 0.53},
                    {"name": "人工智能与计算机学院", "rate": 0.59},
                    {"name": "其他学院", "rate": 0.58}
                ],
                "trend": "适合大学生健康生活和学习方法和学习指导。"
            }
        }
    ],

    #最终书籍检索组5：
    "高情商沟通": [
        {
            "title": "10分钟读懂高情商对话",
            "author": "程国辉",
            "isbn": "9787515842530",
            "match_stars": 4,
            "role_type": "C",
            "fault_type": "none",
            "trap_focus": "book_core_concepts：高智商人群的特征、提升智商的日常训练方法",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.90},
                    {"name": "人文学院", "rate": 0.92},
                    {"name": "商学院", "rate": 0.91},
                    {"name": "人工智能与计算机学院", "rate": 0.98},
                    {"name": "其他学院", "rate": 0.97}
                ],
                "trend": "10分钟读懂高情商对话的权威教材，适合大学生高情商沟通和学习方法和学习指导。"
            }
        },
        {
            "title": "高情商说话",
            "author": "谷厚志",
            "isbn": "9787504695475",
            "match_stars": 2,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.50},
                    {"name": "人文学院", "rate": 0.52},
                    {"name": "商学院", "rate": 0.51},
                    {"name": "人工智能与计算机学院", "rate": 0.53},
                    {"name": "其他学院", "rate": 0.52}
                ],
                "trend": "适合大学生高情商沟通和学习方法和学习指导。"
            }
        },
        {
            "title": "情商:为什么情商比智商更重要",
            "author": "戈尔曼",
            "isbn": "9787521729788",
            "match_stars": 1,
            "role_type": "B",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.30},
                    {"name": "人文学院", "rate": 0.32},
                    {"name": "商学院", "rate": 0.31},
                    {"name": "人工智能与计算机学院", "rate": 0.35},
                    {"name": "其他学院", "rate": 0.34}
                ],
                "trend": "适合大学生高情商沟通和学习方法和学习指导。"
            }
        }
    ],

    #最终书籍检索组6：
    "创造力": [
        {
            "title": "创造力",
            "author": "陈钢林",
            "isbn": "none",
            "match_stars": 4,
            "role_type": "C",
            "fault_type": "none",
            "trap_focus": "book_core_concepts：创造世界所需的物质与力量、创造一切的源泉--application_fields_match：城市创造设计、企业房子创造的方法",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.27},
                    {"name": "人文学院", "rate": 0.32},
                    {"name": "商学院", "rate": 0.31},
                    {"name": "人工智能与计算机学院", "rate": 0.25},
                    {"name": "其他学院", "rate": 0.24}
                ],
                "trend": "适合大学生创造力培养和学习方法和学习指导。"
            }
        },
        {
            "title": "创造力:跳出盒子思考",
            "author": "兰德尔",
            "isbn": "9787313113184",
            "match_stars": 2,
            "role_type": "A",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.81},
                    {"name": "人文学院", "rate": 0.89},
                    {"name": "商学院", "rate": 0.88},
                    {"name": "人工智能与计算机学院", "rate": 0.90},
                    {"name": "其他学院", "rate": 0.89}
                ],
                "trend": "适合大学生创造力培养和学习方法和学习指导。"
            }
        },
        {
            "title": "创造的勇气",
            "author": "May, Rollo",
            "isbn": "9787300336947",
            "match_stars": 2,
            "role_type": "B",
            "fault_type": "none",
            "trap_focus": "none",
            "social_reason": {
                "departments": [
                    {"name": "食品学院", "rate": 0.61},
                    {"name": "人文学院", "rate": 0.59},
                    {"name": "商学院", "rate": 0.57},
                    {"name": "人工智能与计算机学院", "rate": 0.55},
                    {"name": "其他学院", "rate": 0.54}
                ],
                "trend": "适合大学生创造力培养和学习方法和学习指导。"
            }
        }
    ]
        
}

from typing import Any, Dict, List, Optional, Tuple
import jieba


def _tokenize_to_set(text: str) -> set[str]:
    """
    使用 jieba 对文本分词，并去除空字符、纯空白等无效 token。
    返回去重后的 token 集合，便于做顺序无关的匹配。
    """
    tokens: set[str] = set()
    for token in jieba.cut(text):
        stripped: str = token.strip()
        if not stripped:
            continue
        tokens.add(stripped)
    return tokens


def _chars_to_set(text: str) -> set[str]:
    """
    将文本拆成单字符集合，去掉空白字符。
    用于在分词不稳定或词序打乱时，通过字符级重合度做补充匹配。
    """
    return {ch for ch in text if not ch.isspace()}


def find_books_by_task(query: str) -> List[Dict[str, Any]]:
    """
    根据用户查询在实验书库中模糊匹配任务，并返回对应的书籍列表。
    使用 jieba 分词 + 相似度打分进行更灵活、鲁棒的匹配：
    - 结合分词重叠程度（覆盖率 + Jaccard 相似度）
    - 同时考虑任务关键词与原始查询之间的子串包含关系
    - 选取得分最高且超过阈值的任务对应书籍
    """
    query = query.strip()
    # 查询过短时不进行自动匹配，避免仅输入 1～2 个字就“秒出结果”，
    # 让上游模型继续引导用户补充意图。
    if not query:
        return []

    MIN_QUERY_LEN_CHARS: int = 3
    if len(query) < MIN_QUERY_LEN_CHARS:
        return []

    normalized_query: str = query.lower()
    normalized_query_words: set[str] = _tokenize_to_set(normalized_query)
    normalized_query_chars: set[str] = _chars_to_set(normalized_query)

    best_score: float = 0.0
    best_books: Optional[List[Dict[str, Any]]] = None

    for task_keyword, books in BOOK_LIBRARY.items():
        task_keyword_lower: str = task_keyword.lower()
        task_keyword_words: set[str] = _tokenize_to_set(task_keyword_lower)
        task_keyword_chars: set[str] = _chars_to_set(task_keyword_lower)

        if not task_keyword_words and not task_keyword_chars:
            continue

        # 分词重叠（词级）
        overlap_words: set[str] = normalized_query_words & task_keyword_words

        # 字符级重叠，用于词序打乱或分词不稳定时的补充
        overlap_chars: set[str] = normalized_query_chars & task_keyword_chars

        if (
            not overlap_words
            and not overlap_chars
            and task_keyword_lower not in normalized_query
            and normalized_query not in task_keyword_lower
        ):
            # 完全没有词/字符重合且不存在子串关系，认为相似度很低
            continue

        union_words: set[str] = normalized_query_words | task_keyword_words
        # 任务关键词被命中的程度
        coverage: float = len(overlap_words) / len(task_keyword_words) if task_keyword_words else 0.0
        # 用户查询中有多少部分被任务关键词“解释”掉（词级覆盖），尽量让每个词都参与匹配
        query_coverage: float = (
            len(overlap_words) / len(normalized_query_words) if normalized_query_words else 0.0
        )
        jaccard: float = len(overlap_words) / len(union_words) if union_words else 0.0

        # 字符级覆盖率：处理“字符顺序打乱但组成相近”的情况
        char_coverage: float = (
            len(overlap_chars) / len(task_keyword_chars) if task_keyword_chars else 0.0
        )
        char_query_coverage: float = (
            len(overlap_chars) / len(normalized_query_chars) if normalized_query_chars else 0.0
        )

        # 子串包含给予一个额外的加分
        substring_boost: float = 0.0
        if task_keyword_lower in normalized_query or normalized_query in task_keyword_lower:
            substring_boost = 0.2

        # 综合得分：优先保证任务关键词和查询双方的覆盖率，再考虑整体相似度；
        # 同时引入字符级覆盖，增强对“词序乱了但用词接近”的鲁棒性。
        score: float = (
            0.35 * coverage
            + 0.15 * query_coverage
            + 0.20 * jaccard
            + 0.15 * char_coverage
            + 0.15 * char_query_coverage
            + substring_boost
        )

        if score > best_score:
            best_score = score
            best_books = books

    # 设置一个最低阈值，避免误匹配；阈值可按实验效果再微调
    MIN_SCORE_THRESHOLD: float = 0.30
    if best_books is not None and best_score >= MIN_SCORE_THRESHOLD:
        return best_books

    return []