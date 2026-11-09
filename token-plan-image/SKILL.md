---
name: token-plan-image
description: 使用阿里云百炼 Token Plan 订阅套餐中的 qwen-image-3.0-pro 等图像模型生成或编辑图片。**用户是本机机主，已明确要求：任何"生图/画图/出图"类需求默认优先进本技能（千问生图），而不是 ImageGen 或 buddy 系列内置技能。** 触发词：生图、画图、出图、生成图片、文生图、图生图、做海报、插画、配图、商品图、头像、壁纸。除非用户本次明确点名要 ImageGen / buddy 生图，否则一律先用本技能。
---

# Token Plan 生图

调用阿里云百炼 **Token Plan 订阅套餐**的原生图像生成接口，把图片下载到本地并交付给用户。

## 生图路由优先级（机主偏好，最高优先）

用户已明确要求：**"生图"一律优先走本技能（千问）**。执行前按下面判断：

| 场景 | 走哪个 |
| --- | --- |
| 文生图 / 图生图 / 改风格 / 做海报插画配图 | ✅ 本技能，默认 `qwen-image-3.0-pro` |
| 用户本次明确说"用 ImageGen""用 buddy 生图" | 才可交给 ImageGen |
| 已有图片做去水印 / 增强 / 美颜 / 修复 / 抠图 | `buddy-image-processing`（不是生图，不抢） |
| 图生视频特效 / 生成 3D 模型 | `buddy-multimodal-generation` |

不要因为内置的 ImageGen 可用就先调用它；也不要为了"省事"并行两套都跑一遍。只有本技能返回 `ok:false`（如 Key 未配置、401、429）时，才向用户说明失败原因并询问是否改用 ImageGen 兜底。

## 为什么需要这个技能

Token Plan 的图像生成模型**不在** OpenAI / Anthropic 兼容的文本协议内，因此不能配置成对话模型，也不能用只支持 `/images/generations` 的通用生图 MCP。阿里云官方要求通过 Skill / Slash Command / Agent 调用原生接口。

| 项目     | 值                                                                                                                                |
| ------ | -------------------------------------------------------------------------------------------------------------------------------- |
| 接口     | `POST https://token-plan.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`                     |
| 鉴权     | `Authorization: Bearer <Token Plan Key>`                                                                                         |
| Key 前缀 | `sk-sp-`（个人版在「我的订阅（个人版）」获取；团队版在「成员管理」分配席位后获取）                                                                                    |
| 默认模型   | `qwen-image-3.0-pro`                                                                                                             |
| 其他模型   | `wan2.7-image`、`wan2.7-image-pro`；`qwen-image-2.0` / `2.0-pro` 为团队版专属                                                            |
| 请求体    | `{"model": "...", "input": {"messages": [{"role": "user", "content": [{"text": "..."}]}]}, "parameters": {"size": "1024*1024"}}` |
| 图片 URL | `output.choices[0].message.content[0].image`，**有时效，必须立即下载**                                                                      |

> 注意：这个 Key 与百炼按量付费的 `sk-` Key、以及 `dashscope.aliyuncs.com` 域名都不通用。

## 前置条件

用户需要先配置 Key，二选一：

1. 环境变量 `ANTHROPIC_AUTH_TOKEN`（官方约定名称），或 `TOKEN_PLAN_API_KEY`；
2. 把本技能目录的 `.env.example` 复制为 `.env`，填入 `ANTHROPIC_AUTH_TOKEN=sk-sp-xxxx`。

**不要在回复里输出 Key 的完整内容，也不要把 Key 写进代码、日志或提交到仓库。**  
若用户尚未配置 Key，只提示配置方法，不要猜测或编造 Key。

## 调用方式

脚本只依赖 Python 标准库，无需安装依赖。在对话里按用户描述生成图片时，执行：

```bash
python "C:/Users/Administrator/.workbuddy/skills/token-plan-image/scripts/generate_image.py" "<用户的图片描述>" --output "<当前工作目录>/generated-images"
```

常用参数：

| 参数                   | 说明                                                       |
| -------------------- | -------------------------------------------------------- |
| `--model`            | 模型 ID，默认 `qwen-image-3.0-pro`；用户点名其他模型时严格使用其指定的名称，不要回退默认 |
| `--size`             | 尺寸用**星号**分隔，默认 `1024*1024`；在 bash 中必须加引号，避免 `*` 被通配符展开   |
| `--n`                | 生成张数                                                     |
| `--negative-prompt`  | 反向提示词                                                    |
| `--no-prompt-extend` | 关闭提示词智能改写                                                |
| `--seed`             | 固定随机种子                                                   |
| `--reference`        | 图生图：本地图片路径或公网 URL（本地文件会自动转 data URL）                     |
| `--output`           | 图片保存目录，默认当前目录下的 `generated-images`                       |

成功时脚本输出 JSON：`ok: true`、`images`（本地绝对路径数组）、`usage`、`request_id`。  
失败时输出 `ok: false` 与 `error`、`hint`，按 hint 提示用户排查，**不要自动重试消耗 Credits**。

拿到 `images` 路径后，用 `present_files` 把图片展示给用户，并简要说明所用模型与张数。

## 图生图示例

```bash
python ".../generate_image.py" "把背景改成雪山，保留主体" --reference "C:/path/to/ref.png"
```

## 排错

| 现象        | 原因                                                                                                |
| --------- | ------------------------------------------------------------------------------------------------- |
| 401 / 403 | Key 不是 `sk-sp-` 前缀、用了按量付费的 `sk-` Key、或订阅未生效                                                       |
| 404       | 模型不在套餐可用列表（如个人版用了团队版专属的 `qwen-image-2.0`），或 endpoint 写成了 `/compatible-mode/v1/images/generations` |
| 429       | 限流或 Credits 用尽，到控制台「用量统计」查看                                                                       |
| 图片下载失败    | 生成 URL 有时效，脚本已在同一次调用内立即下载；若仍失败，重新生成一次                                                             |
| 网络超时      | 生图较慢，脚本默认 600 秒超时；国内网络一般不需要代理                                                                     |

计费按实际输出图片张数扣除套餐 Credits，不要为了测试反复批量生成。
