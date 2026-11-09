#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — 把 data.json 注入 HTML 模板，生成可交互的四级翻译批改报告。

用法：
    python3 scripts/build.py data.json out.html
    python3 scripts/build.py data.json out.html --shot      # 额外截一张图自检
    python3 scripts/build.py data.json --check              # 只校验不生成

退出码：0 成功；1 校验失败。
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
PLACEHOLDER = "/*__CET4_DATA__*/null"
TYPES = {"grammar", "spelling", "collocation", "word", "logic"}
REQUIRED_META = ["exam", "part", "title", "subtitle", "score", "verdict"]
REQUIRED_ERR = ["type", "bad", "good", "why", "src", "srcEn"]

warnings = []
errors = []


def warn(msg):
    warnings.append(msg)


def fail(msg):
    errors.append(msg)


def check_tags(text, where):
    """检查 <b> 与 </b>、<span> 与 </span> 是否成对。"""
    for tag in ("b", "span", "del", "i"):
        o = len(re.findall(r"<%s[ >]" % tag, text))
        c = len(re.findall(r"</%s>" % tag, text))
        if o != c:
            fail("%s：<%s> 开合不匹配（%d 开 / %d 闭）" % (where, tag, o, c))


def validate(data):
    for k in ("meta", "sentences", "errors", "transcript"):
        if k not in data:
            fail("缺少顶层字段：%s" % k)
    if errors:
        return

    meta = data["meta"]
    for k in REQUIRED_META:
        if k not in meta or str(meta[k]).strip() == "":
            fail("meta 缺少字段：%s" % k)
    try:
        score = float(meta.get("score", -1))
        maxs = float(meta.get("max", 15))
        if not (0 <= score <= maxs):
            fail("meta.score=%s 超出 0–%s" % (score, maxs))
    except (TypeError, ValueError):
        fail("meta.score 必须是数字")

    sents = data["sentences"]
    if not isinstance(sents, list) or not sents:
        fail("sentences 必须是非空数组")
        return

    for i, s in enumerate(sents, 1):
        for k in ("no", "zh", "ref", "tokens"):
            if k not in s:
                fail("第 %d 句缺少字段：%s" % (i, k))
        if not s.get("simple"):
            warn("第 %d 句没有 simple（简单版），页面会少一块对照" % i)
        toks = s.get("tokens") or []
        if not toks:
            fail("第 %d 句 tokens 为空" % i)
        for tk in toks:
            if "t" not in tk:
                fail("第 %d 句有 token 缺少 t 字段" % i)
        if not any(tk.get("e") for tk in toks):
            warn("第 %d 句没有任何错误标注（确认是有意为之？）" % i)

    errs = data["errors"]
    if not isinstance(errs, dict) or not errs:
        fail("errors 必须是非空对象")
        return

    for eid, e in errs.items():
        if not re.fullmatch(r"e\d+", eid):
            fail("错误编号格式应为 e1/e2…，实际：%s" % eid)
        for k in REQUIRED_ERR:
            if k not in e or str(e[k]).strip() == "":
                fail("%s 缺少字段：%s" % (eid, k))
        if e.get("type") not in TYPES:
            fail("%s 的 type=%s 不在 %s 中" % (eid, e.get("type"), sorted(TYPES)))
        for k in ("why", "srcEn"):
            if isinstance(e.get(k), str):
                check_tags(e[k], "%s.%s" % (eid, k))

    # 引用一致性
    refs = []
    for s in sents:
        for tk in s["tokens"]:
            if tk.get("e"):
                refs.append(tk["e"])
    for r in refs:
        if r not in errs:
            fail("token 引用了不存在的错误编号：%s" % r)
    for eid in errs:
        if eid not in refs:
            fail("%s 定义了但没有任何 token 引用，页面上不会出现" % eid)
    dup = {r for r in refs if refs.count(r) > 1}
    if dup:
        fail("同一个错误编号被多处引用（只能标一次）：%s" % ", ".join(sorted(dup)))

    # 编号顺序（可读性要求：按出现顺序递增）
    nums = [int(r[1:]) for r in refs]
    if nums != sorted(nums):
        warn("错误编号不是按出现顺序递增的，页面上的上标会显得跳跃")
    if nums and (nums[0] != 1 or nums != list(range(1, len(nums) + 1))):
        warn("错误编号建议从 e1 开始连续编号（当前：%s）" % ("e" + ", e".join(map(str, nums))))

    # 打分提示
    if len(errs) >= 15 and float(data["meta"]["score"]) >= 11:
        warn("错误数 %d 但给了 %s 分，档位可能偏高（11 分档通常 ≤8 处错误）"
             % (len(errs), data["meta"]["score"]))
    if len(errs) <= 3 and float(data["meta"]["score"]) <= 8:
        warn("错误只有 %d 处却给 %s 分，档位可能偏低" % (len(errs), data["meta"]["score"]))

    # 简单版自查
    for i, s in enumerate(sents, 1):
        sm = s.get("simple") or ""
        if sm and len(re.findall(r"\b\w+\b", sm)) > 35:
            warn("第 %d 句简单版超过 35 词，可能没按「拆句」处理" % i)
        if sm and re.search(r"\b(competitiveness|accounting for|utilization)\b", sm):
            warn("第 %d 句简单版里出现了高阶词，与「降级表述」的目标不符" % i)

    # 保底打法页
    method = data.get("method")
    if not method:
        warn("没有 method 字段，「保底打法」标签页会是空白 —— 建议从 example-data.json 整块复制")
    else:
        if not method.get("intro"):
            warn("method.intro 为空，保底页会缺总纲")
        for k in ("tricks", "splits", "steps"):
            if not method.get(k):
                warn("method.%s 为空，保底页会少一块" % k)
        for i, t in enumerate(method.get("tricks") or [], 1):
            if not t.get("title") or not t.get("desc"):
                warn("method.tricks 第 %d 条缺 title 或 desc" % i)
            for r in t.get("rows") or []:
                if not isinstance(r, list) or len(r) != 2:
                    fail("method.tricks 第 %d 条的 rows 元素必须是 [原文, 保底写法] 二元素数组" % i)
        for i, s in enumerate(method.get("splits") or [], 1):
            if not isinstance(s.get("en"), list) or not s.get("en"):
                fail("method.splits 第 %d 条的 en 必须是字符串数组（一行一句）" % i)
        for k in ("intro",):
            if isinstance(method.get(k), str):
                check_tags(method[k], "method." + k)
        for t in method.get("tricks") or []:
            if isinstance(t.get("desc"), str):
                check_tags(t["desc"], "method.tricks.desc")


def build(template_text, data):
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if PLACEHOLDER not in template_text:
        sys.exit("模板里找不到占位符 %s，模板可能被改坏了" % PLACEHOLDER)
    return template_text.replace(PLACEHOLDER, payload)


def shot(html_path, png_path):
    for exe in ("chromium", "chromium-browser", "google-chrome"):
        try:
            subprocess.run(
                [exe, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                 "--window-size=1280,1700", "--virtual-time-budget=3000",
                 "--screenshot=" + str(png_path), "file://" + str(Path(html_path).resolve()) + "#static"],
                check=True, capture_output=True, timeout=90)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
    return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        sys.exit(1)

    data_path = Path(args[0])
    if not data_path.exists():
        sys.exit("找不到数据文件：%s" % data_path)
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("JSON 解析失败（第 %d 行第 %d 列）：%s" % (e.lineno, e.colno, e.msg))

    validate(data)

    for w in warnings:
        print("  [warn] " + w)
    for e in errors:
        print("  [FAIL] " + e)

    if errors:
        print("\n校验未通过：%d 个错误，%d 个警告" % (len(errors), len(warnings)))
        sys.exit(1)

    print("校验通过：%d 句、%d 处标注、%d 个警告"
          % (len(data["sentences"]), len(data["errors"]), len(warnings)))

    if "--check" in flags:
        sys.exit(0)

    out = Path(args[1]) if len(args) > 1 else Path("report.html")
    html = build(TEMPLATE.read_text(encoding="utf-8"), data)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("已生成：%s（%.1f KB）" % (out, out.stat().st_size / 1024))

    if "--shot" in flags:
        png = out.with_suffix(".png")
        if shot(out, png):
            print("自检截图：%s" % png)
        else:
            print("（未找到 chromium，跳过截图；请手动打开检查）")


if __name__ == "__main__":
    main()
