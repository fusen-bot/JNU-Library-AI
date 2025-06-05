#!/usr/bin/env python3
"""
测试脚本：调用 qwen.get_qwen_suggestion 并打印返回结果。
运行方式：python3 test_qwen.py
"""
from qwen import get_qwen_suggestion

def main():
    test_inputs = [
        "python编程",
        "机器学习",
        "数据科学",
    ]
    for input_text in test_inputs:
        print(f"输入：{input_text}")
        suggestion = get_qwen_suggestion(input_text)
        print(f"返回建议：{suggestion}\n{'-' * 40}")

if __name__ == '__main__':
    main() 