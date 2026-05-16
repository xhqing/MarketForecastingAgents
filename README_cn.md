# MarketForecastingAgents

基于多智能体协作的 AI 市场研究报告自动生成系统，覆盖 A 股、港股、美股三大市场。

[English Documentation](README.md)

***

## 功能特性

- **多智能体协作**：整合三位专业投资智能体——Livermore（趋势跟踪）、Buffett（价值投资）、Cathie Wood（颠覆式创新），各自拥有独特的分析哲学，提供多视角市场评估。
- **全市场覆盖**：支持 A 股（上交所/深交所）、港股（港交所）、美股（纽交所/纳斯达克），包括指数、个股和 ETF。
- **实时数据集成**：连接多个 MCP（模型上下文协议）服务器，获取实时行情、财务报表、技术指标、板块资金流向和研报数据。
- **自动化校验**：内置 `targets_validator.py` 确保生成的研报完整覆盖所有配置标的，零遗漏。
- **灵活的标的配置**：所有分析标的通过 `targets.json` 统一管理，可随时增删改。

***

## 系统架构

### 智能体团队

| 智能体             | 角色    | 分析哲学                | MCP / 能力                                   |
| --------------- | ----- | ------------------- | ------------------------------------------ |
| **@Livermore**  | 市场分析师 | 趋势跟踪、关键点交易、量价验证     | 自有 MCP 服务器 + 网络搜索 + 金融市场分析能力               |
| **@Buffett**    | 价值投资者 | 基本面分析、安全边际、长期持有     | China Stock MCP + Market Data Fetcher + 研报 |
| **@CathieWood** | 创新投资者 | 颠覆式技术、跨行业融合、5年视野    | FinanceKit + Market Data Fetcher + 研报      |
| **@SOLO Agent** | 协调者   | 合并所有智能体输出、保存报告、运行校验 | 文件系统 + 命令执行                                |

### MCP 服务器

| MCP 服务器                 | 功能                                                  | 关联智能体                          |
| ----------------------- | --------------------------------------------------- | ------------------------------ |
| **market-data-fetcher** | 获取指数、股票和 ETF 数据（Longport / AKShare / Yahoo Finance） | Livermore, Buffett, CathieWood |
| **financekit**          | 股票报价、公司信息、技术分析、风险指标、期权链                             | CathieWood                     |
| **china-stock-mcp**     | A 股财务数据、资产负债表、利润表、现金流量表、股东信息                        | Buffett                        |
| **mcp-aktools**         | 基于 AKShare 的工具：股票指标、板块资金流向、交易建议                     | Livermore                      |
| **financemcp-dcths**    | 同花顺和东方财富板块指数、成分股和日行情数据                              | Livermore                      |
| **akshare-one-mcp**     | 历史数据、实时数据、财务指标（基于 HTTP）                             | Livermore, Buffett             |
| **Time**                | 当前时间和时区转换                                           | 所有智能体                          |
| **FaXianBaoGao（发现报告）**  | 研报搜索和内容获取                                           | 所有智能体                          |
| **tushareMcp**          | TuShare 金融数据 API（基于 HTTP）                           | Buffett                        |

### 工作流程

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户指令                                   │
│  （在 TRAE CN SOLO 模式下发送给 SOLO Agent）                      │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  步骤 1：学习历史聊天记录                                          │
│  所有智能体学习 chatHistory/ 中的历史分析模式                       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  步骤 2：收集实时数据                                              │
│  每个智能体使用 MCP 工具和 WebSearch 收集最新数据                    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  步骤 3：多智能体讨论                                              │
│  4 个智能体共同讨论，为每个标的生成概率加权的                         │
│  情景预测                                                         │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  步骤 4：合并并保存报告                                            │
│  SOLO Agent 将所有输出合并为 Markdown 报告                         │
│  保存到 chatHistory/                                              │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  步骤 5：校验覆盖率                                               │
│  SOLO Agent 运行 targets_validator.py                            │
│  若退出码 = 1 → 返回步骤 1 重新执行                               │
│  若退出码 = 0 → 完成 ✓                                            │
└──────────────────────────────────────────────────────────────────┘
```

***

## 项目结构

```
MarketForecastingAgents
├── .trae/
│   ├── mcp.json.example       # MCP 服务器配置模板
│   └── rules/
│       ├── toolcallingrules.md # 工具调用规则（英文）
│       └── 工具调用规则.md      # 工具调用规则（中文）
├── agents_info/
│   ├── Livermore_info.md      # Livermore 智能体提示词和指令
│   ├── Buffet_info.md         # Buffett 智能体提示词和指令
│   └── CathieWood_info.md     # Cathie Wood 智能体提示词和指令
├── chatHistory/               # 生成的研报和聊天记录
│   ├── 全市场走势预判_20260513.md  # 全市场走势预判报告
│   ├── 港股走势预判_20260513.md    # 港股走势预判报告
│   └── ...
├── targets.json               # 标的配置（指数、个股、ETF）
├── targets_validator.py       # 研报覆盖率校验脚本
├── .gitignore
├── LICENSE                    # AGPL-3.0
├── README.md                  # 英文文档
└── README_cn.md               # 本文件（中文文档）
```

***

## 标的配置（targets.json）

所有分析标的通过项目根目录下的 `targets.json` 统一管理，覆盖 A 股、港股、美股三大市场，支持指数、个股和 ETF 的灵活配置。用户可直接编辑该文件增删标的。

### 结构

```json
{
  "a_shares": {
    "index_major": [{"name": "...", "code": "000001.SH"}],
    "sse_stocks":   [{"name": "...", "code": "688981.SH"}],
    "sse_etf":      [{"name": "...", "code": "513310.SH"}],
    "szse_stocks":  [{"name": "...", "code": "000063.SZ"}],
    "szse_etf":     [{"name": "...", "code": ""}]
  },
  "hk_shares": {
    "index_major":  [{"name": "...", "code": "800000.HK"}],
    "hkex_stocks":  [{"name": "...", "code": "00700.HK"}],
    "hkex_etf":     [{"name": "...", "code": "02800.HK"}]
  },
  "us_shares": {
    "index_major":  [{"name": "...", "code": ".NDX"}],
    "stocks":       [{"name": "...", "code": "NVDA"}],
    "adr":          [{"name": "...", "code": "BABA"}],
    "etf":          [{"name": "...", "code": "QQQ"}]
  }
}
```

### 当前预设标的

- **A 股指数**：上证指数 (000001.SH)、深证成指 (399001.SZ)
- **A 股个股**：中芯国际 (688981.SH)、中兴通讯 (000063.SZ)
- **A 股 ETF**：中韩半导体 (513310.SH)
- **港股指数**：恒生指数 (800000.HK)、恒生科技指数 (800700.HK)
- **港股个股**：腾讯控股、阿里巴巴、小米、快手、京东、美团、中芯国际、泡泡玛特、宁德时代、比亚迪股份、香港交易所、友邦保险、中国移动、网易、百度集团、理想汽车、小鹏汽车、安踏体育、地平线机器人等 40+ 只
- **港股 ETF**：盈富基金 (02800.HK)、南方恒生科技 (03033.HK)
- **美股指数**：纳斯达克 100 (.NDX)、标普 500 (.SPX)
- **美股个股**：英伟达 (NVDA)
- **美股 ADR**：阿里巴巴 (BABA)
- **美股 ETF**：QQQ、SPY

> **注意**：`name` 和 `code` 为空的条目为占位符，请根据需要填写或删除。

***

## 研报校验（targets\_validator.py）

`targets_validator.py` 脚本用于校验生成的研报是否完整覆盖 `targets.json` 中定义的所有标的。

### 用法

```bash
python targets_validator.py <report.md> [--targets <targets.json>]
```

### 功能说明

1. 从 `targets.json` 提取所有有效标的（`name` 和 `code` 均非空的条目）
2. 在研报 Markdown 中逐一搜索每个标的的名称或代码
3. 输出：遗漏标的列表、覆盖率统计

### 退出码

| 退出码 | 含义        |
| --- | --------- |
| `0` | 全部覆盖，无遗漏  |
| `1` | 存在遗漏或多余标的 |

***

## 快速开始

### 前置条件

- [TRAE CN](https://www.trae.com.cn/) IDE（需支持 SOLO 模式）
- Python 3.10+（用于运行 `targets_validator.py`）
- [uv](https://github.com/astral-sh/uv)（用于通过 `uvx` 安装 MCP 服务器）
- [Node.js](https://nodejs.org/)（用于通过 `npx` 安装 MCP 服务器）
- 可选：[Longport](https://longportapp.com/) 账户（用于获取港股/美股实时数据）

### 配置步骤

1. **配置 MCP 服务器**：复制示例配置并填入凭证：
   ```bash
   cp .trae/mcp.json.example .trae/mcp.json
   ```
   编辑 `.trae/mcp.json`，替换以下占位符：
   - `LONGPORT_APP_KEY`、`LONGPORT_APP_SECRET`、`LONGPORT_ACCESS_TOKEN` — 你的 Longport API 凭证
   - `TARGETS_JSON_PATH` — `targets.json` 的绝对路径
   - `tushareMcp` URL — 将 `your_tushare_token_here` 替换为你的 TuShare token
2. **配置标的**：根据需要编辑 `targets.json`，增删需要分析的指数、股票和 ETF。
3. **设置智能体**：使用 `agents_info/` 中的信息将三个智能体导入 TRAE CN：
   - Livermore：参见 `agents_info/Livermore_info.md` 获取提示词
   - Buffett：参见 `agents_info/Buffet_info.md` 获取提示词
   - Cathie Wood：参见 `agents_info/CathieWood_info.md` 获取提示词

### 生成研报

配置完成后，在 TRAE CN 中切换到 **SOLO 模式**，向 SOLO Agent 发送以下指令：

```PlainText
1、你和 @Livermore @Buffett @CathieWood 一起学习这个目录(/path/to/MarketForecastingAgents/chatHistory/)中的金融市场分析逻辑和回答框架。
2、你们4个智能体(@Livermore @Buffett @CathieWood @SOLO Agent)一起利用 MCP 工具或 WebSearch 技能搜索尽可能多的最新数据和信息。
3、你们4个智能体(@Livermore @Buffett @CathieWood @SOLO Agent)商量探讨后给出一份截止今天当前时刻的接下来半年这个文件(/path/to/MarketForecastingAgents/targets.json)中提到的所有标的的走势预判，分别给出以下每个选项的概率值和每个选项的价格运行区间并说明理由，选项：1、震荡偏强；2、震荡偏弱；3、震荡上行；4、震荡下行；5、直接上行；6、直接下行。
4、你把你们4个智能体(@Livermore @Buffett @CathieWood @SOLO Agent)的输出内容进行综合分析，把综合分析的结果保存在 Markdown 文档中并把这个文档存放在这个目录(/path/to/MarketForecastingAgents/chatHistory/)中。 
5、最后由你来进行目标数校验：运行这个Py文件(/path/to/MarketForecastingAgents/targets_validator.py)，运行后若退出码为1则重新执行步骤1-5直到退出码为0为止。
```

> **重要提示**：请将 `/path/to/MarketForecastingAgents/` 替换为你系统上的实际绝对路径。

***

## 走势预判情景

研报中对每个标的的走势预判涵盖以下六种概率加权情景：

| 编号 | 情景   | 描述            |
| -- | ---- | ------------- |
| 1  | 震荡偏强 | 价格在区间内震荡但偏向上行 |
| 2  | 震荡偏弱 | 价格在区间内震荡但偏向下行 |
| 3  | 震荡上行 | 价格总体上行但伴随显著震荡 |
| 4  | 震荡下行 | 价格总体下行但伴随显著震荡 |
| 5  | 直接上行 | 价格稳步上行，无明显回调  |
| 6  | 直接下行 | 价格稳步下行，无明显反弹  |

***

## 免责声明

本项目生成的研报仅供参考，不构成任何投资建议。金融市场存在固有风险，投资需谨慎，请务必进行独立判断。

## 许可证

本项目采用 [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE) 开源许可证。
