#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阿里云百炼 Token Plan 图像生成调用脚本。

支持 qwen-image-3.0-pro / qwen-image-2.0-pro / wan2.7-image 等套餐内模型。
仅使用 Python 标准库，无需 pip install。

API Key 读取优先级：
  1. --api-key（不推荐，会留在命令行历史里）
  2. 环境变量 ANTHROPIC_AUTH_TOKEN（官方约定）
  3. 环境变量 TOKEN_PLAN_API_KEY
  4. 本技能目录下的 .env 文件
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = "https://token-plan.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
DEFAULT_MODEL = "qwen-image-3.0-pro"
DEFAULT_SIZE = "1024*1024"
KEY_ENV_NAMES = ("ANTHROPIC_AUTH_TOKEN", "TOKEN_PLAN_API_KEY")
SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent


def load_api_key(explicit: str | None = None) -> str | None:
    if explicit:
        return explicit.strip()
    for name in KEY_ENV_NAMES:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    env_file = SKILL_DIR / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() in KEY_ENV_NAMES:
                return value.strip().strip('"').strip("'") or None
    return None


def image_reference(value: str) -> str:
    """本地图片转 data URL；http(s) URL 或已有 data URL 原样返回。"""
    if value.startswith(("http://", "https://", "data:")):
        return value
    path = pathlib.Path(value).expanduser()
    if not path.is_file():
        raise ValueError(f"参考图文件不存在：{path}")
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def build_payload(args: argparse.Namespace) -> dict:
    content: list[dict] = []
    if args.reference:
        content.append({"image": image_reference(args.reference)})
    content.append({"text": args.prompt})

    parameters: dict = {"size": args.size}
    if args.n is not None:
        parameters["n"] = args.n
    if args.negative_prompt:
        parameters["negative_prompt"] = args.negative_prompt
    if args.no_prompt_extend:
        parameters["prompt_extend"] = False
    if args.seed is not None:
        parameters["seed"] = args.seed

    return {
        "model": args.model,
        "input": {"messages": [{"role": "user", "content": content}]},
        "parameters": parameters,
    }


def fail(message: str, hint: str = "") -> None:
    print(json.dumps({"ok": False, "error": message, "hint": hint}, ensure_ascii=False))
    sys.exit(1)


def error_hint(status: int, body: str) -> str:
    if status in (401, 403):
        return (
            "Token Plan 的 Key 必须以 sk-sp- 开头，且与百炼按量付费的 sk- Key 不通用；"
            "个人版在「我的订阅（个人版）」获取，团队版在「成员管理」分配席位后获取。"
        )
    if status == 404:
        return "模型不在当前套餐可用列表内，或 endpoint 路径写错。个人版可用 qwen-image-3.0-pro / wan2.7-image；qwen-image-2.0 系列为团队版专属。"
    if status == 429:
        return "触发限流或套餐 Credits 用尽，稍后重试或到控制台查看用量统计。"
    if status >= 500:
        return "上游服务异常，稍后重试。"
    return f"检查 request_id 后到百炼控制台排查。响应片段：{body[:200]}"


def extract_image_urls(result: dict) -> list[str]:
    urls: list[str] = []
    for choice in result.get("output", {}).get("choices") or []:
        for item in choice.get("message", {}).get("content") or []:
            if isinstance(item, dict) and item.get("image"):
                urls.append(item["image"])
    if not urls:
        for item in result.get("data") or []:
            if isinstance(item, dict) and item.get("url"):
                urls.append(item["url"])
    return urls


def main() -> None:
    parser = argparse.ArgumentParser(
        description="调用阿里云百炼 Token Plan 生图接口并下载图片到本地",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("prompt", help="图片描述（正向提示词），建议用引号包裹")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型 ID，默认 {DEFAULT_MODEL}")
    parser.add_argument("--size", default=DEFAULT_SIZE, help=f"尺寸，用星号分隔，默认 {DEFAULT_SIZE}")
    parser.add_argument("--n", type=int, default=None, help="生成张数")
    parser.add_argument("--negative-prompt", default=None, help="反向提示词")
    parser.add_argument("--no-prompt-extend", action="store_true", help="关闭提示词智能改写")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--reference", default=None, help="图生图：参考图的本地路径或公网 URL")
    parser.add_argument("--output", default="generated-images", help="图片保存目录，默认当前目录下 generated-images")
    parser.add_argument("--timeout", type=int, default=600, help="请求超时秒数，默认 600")
    parser.add_argument("--api-key", default=None, help="显式传入 API Key（不推荐）")
    args = parser.parse_args()

    api_key = load_api_key(args.api_key)
    if not api_key:
        fail(
            "未找到 Token Plan API Key",
            "设置环境变量 ANTHROPIC_AUTH_TOKEN，或把 .env.example 复制为 .env 并填入 sk-sp- 开头的 Key。",
        )
    if not api_key.startswith("sk-sp-"):
        print(json.dumps({"ok": True, "warning": "Key 不是 sk-sp- 前缀，这通常是百炼按量付费 Key，Token Plan 接口会鉴权失败。"}, ensure_ascii=False), file=sys.stderr)

    try:
        payload = build_payload(args)
    except ValueError as exc:
        fail(str(exc))

    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:600]
        fail(f"HTTP {exc.code}: {body}", error_hint(exc.code, body))
    except urllib.error.URLError as exc:
        fail(f"网络请求失败：{exc.reason}", "检查网络连通性，或是否需要配置代理。")

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        fail("响应不是合法 JSON", raw[:600])

    if result.get("code") or result.get("error"):
        fail(f"接口返回错误：{result.get('message') or result.get('error')}", f"code={result.get('code')}")

    urls = extract_image_urls(result)
    if not urls:
        fail("响应中未找到图片 URL", f"响应片段：{raw[:600]}")

    out_dir = pathlib.Path(args.output).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    saved: list[str] = []
    for index, url in enumerate(urls, 1):
        try:
            with urllib.request.urlopen(url, timeout=180) as response:
                blob = response.read()
        except Exception as exc:
            fail(f"图片下载失败（URL 有时效，需及时下载）：{exc}", f"原始 URL：{url[:160]}")
        path = out_dir / f"qwen_{stamp}_{index:02d}.png"
        if path.exists():
            path = out_dir / f"qwen_{stamp}_{index:02d}_{int(time.time() * 1000) % 1000}.png"
        path.write_bytes(blob)
        saved.append(str(path))

    print(json.dumps(
        {"ok": True, "model": args.model, "images": saved, "count": len(saved),
         "usage": result.get("usage", {}), "request_id": result.get("request_id", "")},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
