# 五类错误：判定标准与高频错因库

## 一、分类总表

| type | 中文 | 判定问题 | 是否严重错误 |
|---|---|---|---|
| `grammar` | 语法 | 句子结构成立吗？主谓一致吗？时态对吗？ | 多数严重（主谓、谓语、词性） |
| `spelling` | 拼写 | 这个单词字母对得上吗？ | 不严重，但核心词拼错要下沉 |
| `collocation` | 搭配 | 这两个词母语者会放一起吗？ | 严重（搭配错=不会写英语） |
| `word` | 用词 | 词义/词性/语域对得上吗？ | 词性错=严重；词义偏差=中等 |
| `logic` | 逻辑/漏译 | 这个信息挂对主语了吗？有没有整块丢？ | 严重 |

**分类冲突时的处理**：一个 token 同时有语法和搭配问题时，按"最严重的那个"归类，在 `why` 里把另一层说清楚。不要为了凑分类把一个错拆成两条。

## 二、各类判定细则

### grammar（语法）

必查五项：

1. **主谓一致**：找主语中心词，跳过紧邻的名词
   - `the output of vehicles have reached` → 主语是 output，用 has
   - `the government encourage` → 单数加 -s
2. **谓语数量**：一句话只能一个谓语（除非有连词/从句引导）
   - `industry develop have developeds` → 三个谓语形式
3. **时态**：完成时 = have/has + 过去分词，不能只有分词
4. **冠词**：泛指不加 the；副词前不能加 a（`a constantly`）
5. **句法完整**：`By + 动名词` 后面必须有主语；`which` 从句要有明确先行词

### spelling（拼写）

只在两种情况下判错：
- 写完的词不在词典里（`repidly`、`goverment`、`entre`）
- 词形不对（`developeds` 里的 -s）

**不判错**：连笔潦草但仍可辨认为正确词的，写进 `why` 提醒"字迹要清楚"，但不标错。

**交叉验证**：同一个词全篇出现两次，两处写法不同才判拼写错；两处一致但都错，判一次即可（在 `why` 注明"本篇错两次"）。

### collocation（搭配）

中文硬翻的重灾区。判定口诀：**这个词，母语者会这么说吗？**

高频错配库（四级翻译）：

| 中文 | 学生的错配 | 正确搭配 |
|---|---|---|
| 占……份额 | take up the percentage | account for ... of the share |
| 加大投入 | enhance the invests | increase investment |
| 政策引导 | make policies to lead | provide policy guidance |
| 技术创新 | develop the innovation | carry out technological innovation |
| 提高竞争力 | enhance the competence | enhance competitiveness |
| 创出新高 | break the record | hit / set new highs |
| 做出贡献 | make devotion to | make contributions to |
| 采取措施 | take on measures | adopt measures |
| 垃圾分类 | sort the trash | garbage classification |
| 大力发展 | highly develop | vigorously develop |
| 达到……辆 | reach to ... | reach ... |

### word（用词）

三种子类型：

1. **词义偏差**：`productivity`（生产率）≠ 产量；`competence`（能力）≠ 竞争力；`useful` ≠ effective
2. **词性误用**：`the economic`（形容词当名词）、`the develop`（动词当名词）、`environment protection`（名词当形容词）
3. **语域/程度**：`For now`（暂时）≠ 目前；`a lot` 太口语；`frequently`（频繁）≠ 积极（actively）

### logic（逻辑/漏译）

两种子类型：

1. **信息错位**：`which breaks the record` 挂到了"市场份额"上，而原文说的是"出口量"
2. **整块漏译**：一个分句完全没出现（如"出口量"整个丢了）

**判定标准**：如果读者只能靠猜才知道这句话在说什么，就是 logic 级；如果意思在但表达笨，最多是 collocation 级。

## 三、四级翻译高频错因（按出现频次）

1. **Chinese ≠ China**：`Chinese` 作主语指"中国人/中文"，国家必须写 `China`。这是四级最高频扣分点，几乎每套都有人错。
2. **主谓一致**：长主语 + 后置修饰时，谓语跟着最近的名词走了
3. **词性**：`economic/economy`、`develop/development`、`environment/environmental`、`technology/technological`
4. **数字换算**：万 = ten thousand，千万 = ten million，亿 = hundred million
5. **固定搭配**：account for、carry out、make contributions to、adopt measures
6. **冠词**：泛指不加 the；`a/an` 看音标不看字母
7. **时态链**：中文无时态，英文要自己补；描述"近年来"用完成时

## 四、写 `why` 的模板

```
【错在哪】具体指出问题（不是"语法错误"，而是"主语是单数却用了 have"）
【为什么】一句话讲原理（谓语只看主语中心词）
【怎么改】给出正确形式，加粗
【可迁移】一句能用在别处的规律（这是四级固定句式）
```

长度 2–5 句，200–400 字。太短没信息量，太长学生不看。
