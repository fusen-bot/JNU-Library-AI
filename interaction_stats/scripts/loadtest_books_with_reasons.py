import time
import json
import random
import string
from typing import List, Tuple

import requests

BASE_URL: str = "http://localhost:5001"
ENDPOINT: str = f"{BASE_URL}/api/books_with_reasons"


def gen_variants(base: str) -> List[str]:
    tails = ["", " 的", " 书籍", " shu", " shu ji", " 的书籍", " 相关", " 推荐", " de", " d"]
    return [f"{base}{t}" for t in tails]


def send_query(q: str) -> Tuple[int, dict]:
    resp = requests.post(
        ENDPOINT,
        json={"query": q, "session_id": "loadtest_session"},
        timeout=5,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"status": "error", "error": f"non-json: {resp.text[:200]}"}
    return resp.status_code, data


def run_once(base_query: str, delay_ms: int = 120):
    variants = gen_variants(base_query)
    random.shuffle(variants)
    seen_task_ids = set()
    reused = 0
    created = 0
    ok = 0
    for i, q in enumerate(variants):
        code, data = send_query(q)
        ok += int(code == 200 and data.get("status") == "success")
        task_id = data.get("task_id")
        if task_id:
            if task_id in seen_task_ids:
                reused += 1
            else:
                created += 1
                seen_task_ids.add(task_id)
        time.sleep(delay_ms / 1000.0)
    return {
        "ok": ok,
        "created_task_ids": created,
        "reused_task_ids": reused,
        "unique_task_ids": list(seen_task_ids),
    }


def main():
    base_query = "搜索一本人工智能教育"
    rounds = 3
    summary = []
    print(f"Load test against {ENDPOINT}")
    for r in range(rounds):
        res = run_once(base_query, delay_ms=120)
        summary.append(res)
        print(f"Round {r+1}: {json.dumps(res, ensure_ascii=False)}")
        time.sleep(0.5)
    # 统计总体唯一 task 数量
    all_task_ids = set()
    for s in summary:
        all_task_ids.update(s["unique_task_ids"])
    print("-----")
    print(f"Total rounds: {rounds}")
    print(f"Total unique task_ids: {len(all_task_ids)} (expect small, ideally 1)")
    print(f"All unique task_ids: {list(all_task_ids)}")


if __name__ == "__main__":
    main()


