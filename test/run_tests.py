"""
200题 AI 聊天系统测试运行器
用法: python test/run_tests.py
"""
import json, time, urllib.request, urllib.error, ssl, sys

BASE = "http://localhost:8009/api/system/chat/completions"
QUESTIONS_FILE = "test/test_questions_system.json"
TIMEOUT = 60

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def send_question(question, chat_mode="chat"):
    """发送问题到 chat API, 返回 (耗时秒, 回复内容, 错误信息)"""
    body = json.dumps({
        "messages": [{"role": "user", "content": question}],
        "chat_mode": chat_mode,
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2048
    }).encode()

    req = urllib.request.Request(BASE, data=body,
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"})

    start = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx)
        elapsed = time.time() - start

        full_text = ""
        buffer = ""
        # 流式读取 SSE
        while True:
            chunk = resp.read(4096)
            if not chunk:
                break
            try:
                text = chunk.decode("utf-8")
            except:
                text = chunk.decode("utf-8", errors="replace")
            buffer += text

            # 解析 SSE 行
            while "\n\n" in buffer:
                line_block, buffer = buffer.split("\n\n", 1)
                for line in line_block.split("\n"):
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get("phase") == "done":
                                if "result" in data and "content" in data["result"]:
                                    full_text = data["result"]["content"]
                            elif data.get("phase") == "error":
                                return elapsed, "", data.get("result", {}).get("content", str(data))
                        except json.JSONDecodeError:
                            pass
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        body_text = e.read().decode("utf-8", errors="replace")
        return elapsed, "", f"HTTP {e.code}: {body_text[:200]}"
    except Exception as e:
        elapsed = time.time() - start
        return elapsed, "", f"Exception: {str(e)[:200]}"

    return elapsed, full_text, ""


def evaluate(question, answer, elapsed, error):
    """评估单条回答的质量"""
    issues = []

    # 1. 空响应 / 错误
    if error:
        issues.append(f"ERROR: {error}")
        return {"score": 0, "grade": "F", "issues": issues}

    if not answer or not answer.strip():
        issues.append("空回复")
        return {"score": 1, "grade": "F", "issues": issues}

    answer_len = len(answer)

    # 2. 超时判定 (如果耗时接近超时且回复很短, 可能被截断)
    if elapsed > TIMEOUT * 0.9 and answer_len < 20:
        issues.append("疑似超时截断")

    # 3. 回复过短 (单字/单符号)
    if answer_len <= 3:
        issues.append(f"回复过短 ({answer_len}字符): {answer[:80]}")

    # 4. 拒绝回答检测 (安全相关)
    refuse_keywords = ["无法回答", "不能提供", "抱歉", "无法协助", "I cannot", "我不能", "无法满足"]
    refused = any(kw in answer for kw in refuse_keywords)
    if refused:
        issues.append("拒绝回答")

    # 5. 空输入/边界输入特殊处理
    if not question.strip():
        if answer_len < 5:
            issues.append("对空输入的回复不足")
    elif question.strip() in ["？", "...", "x", "啊"]:
        if answer_len < 3:
            issues.append("对极短输入的回复不足")

    # 6. 原文重复 (可能陷入循环)
    if question.strip() and len(question) > 5:
        repeated = answer.count(question[:10])
        if repeated > 3:
            issues.append(f"疑似重复原文 {repeated} 次")

    # 评分
    if not issues:
        grade = "A"
        score = 5
    elif any("ERROR" in i for i in issues):
        grade = "F"
        score = 0
    elif any("空回复" in i for i in issues):
        grade = "F"
        score = 1
    elif len(issues) == 1 and "拒绝回答" in issues[0]:
        grade = "C"
        score = 3
    elif len(issues) <= 2:
        grade = "B"
        score = 4
    else:
        grade = "D"
        score = 2

    return {"score": score, "grade": grade, "issues": issues, "answer_len": answer_len}


def main():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data["questions"]
    total = len(questions)
    results = []
    category_stats = {}

    print(f"=" * 60)
    print(f"AI 聊天系统测试 - 共 {total} 题")
    print(f"=" * 60)

    for i, q in enumerate(questions):
        qid = q["id"]
        category = q["category"]
        question = q["input"]
        chat_mode = "chat"

        # 地图类问题用 query 模式
        if category == "地图导航":
            chat_mode = "query"

        # 打印进度
        short_q = question[:40].replace("\n", " ") if question else "(空)"
        sys.stdout.write(f"\r[{i+1:3d}/{total}] {short_q:42s} ")
        sys.stdout.flush()

        elapsed, answer, error = send_question(question, chat_mode)
        eval_result = evaluate(question, answer, elapsed, error)

        result = {
            "id": qid,
            "category": category,
            "question": question,
            "elapsed": round(elapsed, 2),
            "answer": answer[:500],
            "answer_len": len(answer),
            "error": error,
            "grade": eval_result["grade"],
            "score": eval_result["score"],
            "issues": eval_result["issues"]
        }
        results.append(result)

        # 类别统计
        if category not in category_stats:
            category_stats[category] = {"count": 0, "total_score": 0, "grades": [], "total_time": 0}
        cs = category_stats[category]
        cs["count"] += 1
        cs["total_score"] += eval_result["score"]
        cs["grades"].append(eval_result["grade"])
        cs["total_time"] += elapsed

        # 终端快速反馈
        status = f"[{eval_result['grade']}]"
        if eval_result["issues"]:
            status += f" {'; '.join(eval_result['issues'][:2])}"
        print(status)

        # 请求间隔
        time.sleep(0.3)

    print(f"\n{'=' * 60}")
    print("测试完成，生成报告...")

    # ---- 生成报告 ----
    grades = [r["grade"] for r in results]
    scores = [r["score"] for r in results]
    errors_list = [r for r in results if r["error"] or r["grade"] == "F"]
    avg_time = sum(r["elapsed"] for r in results) / total

    grade_counts = {"A": grades.count("A"), "B": grades.count("B"),
                     "C": grades.count("C"), "D": grades.count("D"),
                     "F": grades.count("F")}
    pass_rate = (grade_counts["A"] + grade_counts["B"] + grade_counts["C"]) / total * 100

    report = {
        "test_info": {
            "total_questions": total,
            "categories": len(category_stats),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "avg_response_time": round(avg_time, 2),
        },
        "summary": {
            "overall_pass_rate_pct": round(pass_rate, 1),
            "grade_distribution": grade_counts,
            "avg_score": round(sum(scores) / total, 2),
            "total_errors": len(errors_list),
            "max_response_time": round(max(r["elapsed"] for r in results), 2),
            "min_response_time": round(min(r["elapsed"] for r in results), 2),
        },
        "category_breakdown": {},
        "failing_cases": [],
        "recommendations": []
    }

    # 类别分析
    for cat, stats in sorted(category_stats.items()):
        avg_s = round(stats["total_score"] / stats["count"], 2)
        avg_t = round(stats["total_time"] / stats["count"], 2)
        a_cnt = stats["grades"].count("A")
        f_cnt = stats["grades"].count("F")
        report["category_breakdown"][cat] = {
            "count": stats["count"],
            "avg_score": avg_s,
            "avg_time": avg_t,
            "A_rate": f"{a_cnt}/{stats['count']}",
            "F_rate": f"{f_cnt}/{stats['count']}"
        }

    # 失败案例
    for r in results:
        if r["grade"] in ("F", "D") or r["error"]:
            report["failing_cases"].append({
                "id": r["id"],
                "category": r["category"],
                "question": r["question"][:80],
                "grade": r["grade"],
                "elapsed": r["elapsed"],
                "issues": r["issues"],
                "error": r["error"],
                "answer_preview": r["answer"][:120] if r["answer"] else "(无)"
            })

    # 自动生成修改建议
    recs = report["recommendations"]

    # 建议1: 超时/性能
    slow_count = sum(1 for r in results if r["elapsed"] > 15)
    if slow_count > 5:
        recs.append(f"性能: {slow_count}题响应>15s, 建议优化LLM调用链路或增加缓存")
    else:
        recs.append("性能: 整体响应速度可接受")

    # 建议2: 空输入处理
    empty_results = [r for r in results if not r["question"].strip()]
    if empty_results:
        empty_ok = sum(1 for r in empty_results if r["grade"] in ("A", "B"))
        if empty_ok < len(empty_results):
            recs.append("边界处理: 空输入/极短输入需要更好的兜底回复, 而非报错或忽略")

    # 建议3: 对抗测试
    attack_results = [r for r in results if r["category"] == "对抗测试"]
    attack_fails = [r for r in attack_results if r["grade"] in ("D", "F")]
    if attack_fails:
        recs.append(f"安全: {len(attack_fails)}个对抗测试未妥善处理, 建议增加输入过滤器")
    if attack_results:
        attack_ok = sum(1 for r in attack_results if r["grade"] in ("A", "B", "C"))
        recs.append(f"安全: 对抗测试通过率 {attack_ok}/{len(attack_results)}, 需确保prompt注入/malicious内容被拦截")

    # 建议4: 类目弱势
    weak_cats = [(c, s) for c, s in report["category_breakdown"].items() if s["avg_score"] < 3.5]
    for cat, stats in weak_cats:
        recs.append(f"薄弱类目: '{cat}' 平均分 {stats['avg_score']}, F率 {stats['F_rate']}, 需针对性优化提示词或能力")

    # 建议5: 地图/nav 工具调用
    nav_results = [r for r in results if r["category"] == "地图导航"]
    nav_fails = [r for r in nav_results if r["grade"] in ("D", "F")]
    if nav_fails:
        recs.append(f"工具调用: {len(nav_fails)}个地图导航问题失败, 检查 navigate_page/map_action 工具是否正常")

    # 建议6: 模式切换
    recs.append("模式过渡: 已为所有模式相关元素添加 CSS transition, 但需确保前端模式切换后正确传递 chat_mode 参数")
    recs.append("对话连续性: 连续追问类问题依赖多轮对话上下文, 当前测试仅为单轮, 建议增加多轮测试")

    # 写入报告
    report_path = "test/test_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 终端摘要
    print(f"\n{'=' * 60}")
    print(f"测试报告已生成: {report_path}")
    print(f"{'=' * 60}")
    print(f"总题数: {total}")
    print(f"通过率: {pass_rate:.1f}%")
    print(f"平均分: {report['summary']['avg_score']:.2f}/5")
    print(f"平均响应: {avg_time:.2f}s")
    print(f"等级分布: A={grade_counts['A']} B={grade_counts['B']} C={grade_counts['C']} D={grade_counts['D']} F={grade_counts['F']}")
    print(f"\n类目得分:")
    for cat, s in sorted(report["category_breakdown"].items()):
        bar = "█" * int(s["avg_score"]) + "░" * (5 - int(s["avg_score"]))
        print(f"  {cat:10s} {bar} {s['avg_score']:.2f} (A: {s['A_rate']}, F: {s['F_rate']})")

    print(f"\n修改建议 ({len(recs)} 条):")
    for i, r in enumerate(recs, 1):
        print(f"  {i}. {r}")


if __name__ == "__main__":
    main()
