# data.json 数据格式

## 顶层结构

```json
{
  "meta": {...},
  "dims": [...],
  "kv": [...],
  "sentences": [...],
  "errors": {...},
  "transcript": [...],
  "method": {...},
  "downgrades": [...],
  "tips": [...],
  "collocations": [...],
  "rewrite": {...}
}
```

## meta（必填）

| 字段 | 类型 | 说明 |
|---|---|---|
| `exam` | string | 如 `"2024年12月 · 第3套"`，显示在顶栏 |
| `part` | string | 如 `"Part IV 汉译英"` |
| `topic` | string | 话题词，进 `<title>` |
| `title` | string | 主标题 |
| `subtitle` | string | 副标题（分数、折算说明） |
| `score` | number | 15 分制得分，可带 0.5 |
| `max` | number | 固定 15 |
| `verdict` | string(HTML) | 总评，2–3 句，用 `<b>` 强调 |
| `simpleNote` | string(HTML) | 绿色条的文案：简单版能到多少分 |
| `scoreWhy` | string(HTML) | 插进评分表的那一行的说明 |
| `scoreNote` | string(HTML) | 评分表下方"为什么不是上一档/下一档" |
| `simpleWhy` | string(HTML) | 两版对照页"为什么简单版能拿 11 分"的正文 |

## dims（可选，画条形图）

```json
[{"name": "内容传达", "value": 10, "max": 15, "color": "var(--green)"}]
```

`color` 可用 `var(--green)` / `var(--red)` / `var(--amber)` / `var(--ink)`。

## kv（可选，评分页右下角）

```json
[{"k": "折算 710 分制", "v": "约 46 / 106.5"},
 {"k": "若补三单+词性", "v": "9–10 分", "color": "var(--green)"}]
```

## sentences（必填，按原文顺序）

```json
{
  "no": 1,
  "zh": "近年来，中国新能源汽车产业发展迅速。",
  "ref": "In recent years, China's NEV industry has developed rapidly.",
  "simple": "In recent years, China's new energy car industry grows very fast.",
  "simpleNote": "「产业发展迅速」→ grows very fast；不会 NEV 就写 new energy car。",
  "tokens": [
    {"t": "In recent years, "},
    {"t": "develop have ", "strike": true},
    {"t": "developeds", "e": "e1"},
    {"t": ". ", "e": "e2"}
  ]
}
```

### token 三种形态

| 形态 | 写法 | 渲染结果 |
|---|---|---|
| 普通文字 | `{"t": "..."}` | 原样输出 |
| 标错 | `{"t": "...", "e": "e1"}` | 波浪线 + 上标编号，可点击 |
| 划掉 | `{"t": "...", "strike": true}` | 删除线，不可点击 |
| 划掉且标错 | `{"t": "...", "e": "e10", "strike": true}` | 删除线 + 波浪线 + 上标 |

**注意**：
- `t` 里的空格、标点都要保留，拼接后就是完整句子
- 一个 `e` 只能被一个 token 引用（重复引用会校验失败）
- 长标注（>12 词）尽量拆开，避免上标掉行

## errors（必填）

key 为 `e1`…`eN`，**必须按出现顺序连续编号**。

```json
"e1": {
  "type": "grammar",
  "bad": "industry developeds",
  "good": "industry has developed",
  "why": "你把 develop have 划掉了…<b>① 缺助动词</b>…",
  "src": "产业发展迅速",
  "srcEn": "the industry has developed rapidly"
}
```

| 字段 | 说明 |
|---|---|
| `type` | 只能是 `grammar` / `spelling` / `collocation` / `word` / `logic` |
| `bad` | 原文写法（可以只截出错的部分，不必整句） |
| `good` | 改法（简洁，不要写整段） |
| `why` | 2–5 句，HTML 可用 `<b>`；讲清错在哪 + 为什么 + 怎么改 + 规律 |
| `src` | 对应的中文片段 |
| `srcEn` | 对应的英文标准说法 |

## transcript（必填）

手写原文逐行转录，一行一个字符串。划掉的部分用 `<del>…</del>`。

```json
["In recent years, the Chinese new energy vehicle industry",
 "<del>develop have</del> developeds repidly. For now, the productivity of"]
```

## method（可选，但强烈建议 —— 「保底打法」标签页）

不填这一页就是空白；填了才有完整的三招 + 拆句 + 五步走。内容直接从 `assets/example-data.json` 的 `method` 整块复制，只需替换 `splits` 里的例句（用本篇真题的句子最好）。

```json
"method": {
  "intro": "HTML，2 段，讲清「两条命：单词语法不出硬错 + 内容不跑题」和 11 分档对词汇零要求",
  "tricks": [
    {
      "title": "用上位词替代",
      "desc": "HTML，讲清这招怎么用 + 什么时候别用",
      "rows": [["匠人 craftsman", "workers"], ["高楼大厦", "many buildings"]]
    }
  ],
  "splits": [
    { "zh": "中文原句", "en": ["拆出来的第 1 句", "第 2 句"], "note": "HTML，讲清怎么拆、哪个词要注意" }
  ],
  "steps": [
    { "title": "划主干", "desc": "HTML，一句话" }
  ]
}
```

| 字段 | 说明 |
|---|---|
| `intro` | 总纲，HTML |
| `tricks[].title/desc` | 三招，固定 3 条（上位词 → 解释 → 大词小词） |
| `tricks[].rows` | `[原文, 保底写法]` 二元素数组，渲染成小表 |
| `splits[].zh/en/note` | 拆句示例，`en` 是字符串数组，一行一句 |
| `steps[].title/desc` | 考场五步 |

## downgrades（可选，但强烈建议）

```json
[{"from": "has developed rapidly", "to": "grows very fast",
  "why": "完成时改一般现在时，时态风险归零"}]
```

`why` 填"降级的代价/收益"，一句话。

## tips（可选）

```json
[{"title": "主谓一致", "desc": "<code>industry has</code>、<code>government encourages</code>…"}]
```

## collocations（可选）

```json
[["has developed rapidly", "发展迅速"], ["account for", "占（比例）"]]
```

## rewrite（可选，但强烈建议）

```json
{
  "bad": "…<span class=\"del\">错误的片段</span>…",
  "good": "…<span class=\"ins\">改后的片段</span>…"
}
```

整段文本，用 `del` / `ins` 标出差异。注意 JSON 里双引号要转义。

## 最小可用数据

只填必填项也能出页面：

```json
{
  "meta": {"exam":"2024年12月 · 第1套","part":"Part IV 汉译英","topic":"环境保护",
           "title":"四级汉译英批改","subtitle":"15 分制","score":7,"max":15,
           "verdict":"…","simpleNote":"…","scoreWhy":"…","scoreNote":"…","simpleWhy":"…"},
  "sentences": [{"no":1,"zh":"…","ref":"…","tokens":[{"t":"…","e":"e1"}]}],
  "errors": {"e1":{"type":"grammar","bad":"…","good":"…","why":"…","src":"…","srcEn":"…"}},
  "transcript": ["…"]
}
```

但**实际交付必须带 `method`**，否则「保底打法」标签页是空的。

## 页面结构（7 个标签）

| 标签 | 内容 | 数据来源 |
|---|---|---|
| 总结 | 分数环、总评、简单版提示、一句话诊断 | `meta` + `tips[0..2]` |
| 逐句批改 | 手写转录 + 逐句标注（点标注开详情） | `sentences` / `transcript` |
| 错误清单 | 表格，分类筛选 | `errors` |
| 两版对照 | 精确版 vs 简单版 + 逐条降级 | `sentences[].ref/simple` + `downgrades` |
| 评分解析 | 六档评分表 + 维度条形图 + 折算 | `meta` + `dims` + `kv` |
| 保底打法 | 三招换词 + 拆句 + 考场五步 | `method` |
| 改写与提升 | 最小改动版 + 硬伤清单 + 搭配表 | `rewrite` / `tips` / `collocations` |

顶部条：品牌 + 7 个标签 + 右侧统计；第二行是**分类跳转 chips**（点某类 → 跳到该类第一处错误并弹出详情，再点取消）。两者都 sticky，滚动时常驻。

## 校验会拦下的问题

`build.py` 会在生成前检查：

- 缺字段 / `type` 不在枚举里
- token 引用了不存在的 `e`
- 定义了 `e` 但没有 token 引用（页面上不会出现）
- 同一个 `e` 被引用两次
- 编号跳号（只警告）
- `<b>`、`<span>` 开合不匹配
- 错误数与分数明显矛盾（只警告）
- 简单版超过 35 词或含高阶词（只警告）
