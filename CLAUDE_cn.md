# CLAUDE_cn.md

本文件为 TRAE CN 在处理本项目时提供指导。

## 项目概述

MarketForecastingAgents 是一个基于多智能体协作的 AI 市场研究报告自动生成系统，覆盖 A 股、港股和美股三大市场。系统运行于 TRAE CN IDE 的 SOLO 模式下，协调三个专业投资智能体，生成概率加权的市场走势预判。

## 项目结构

```
MarketForecastingAgents/
├── .trae/
│   ├── mcp.json              # MCP 服务器配置（已 git 忽略，包含密钥）
│   ├── mcp.json.example       # MCP 服务器配置模板
│   └── rules/
│       ├── toolcallingrules.md  # 工具调用规则（英文）
│       └── 工具调用规则.md       # 工具调用规则（中文）
├── agents_info/
│   ├── Livermore_info.md      # Livermore 智能体提示词和指令
│   ├── Buffet_info.md         # Buffett 智能体提示词和指令
│   └── CathieWood_info.md     # Cathie Wood 智能体提示词和指令
├── chatHistory/               # 生成的研报和聊天记录
├── targets.json               # 标的配置（指数、个股、ETF）
├── targets_validator.py       # 研报覆盖率校验脚本
├── .gitignore
├── LICENSE                    # AGPL-3.0
├── README.md                  # 英文文档
└── README_cn.md               # 中文文档
```

## 技术栈

- **运行时**：Python 3.10+（用于 `targets_validator.py`）
- **IDE**：TRAE CN SOLO 模式
- **MCP 服务器**：通过 `uvx`（Python）和 `npx`（Node.js）安装
- **数据源**：Longport API、AKShare、TuShare、同花顺、东方财富、Yahoo Finance
- **许可证**：AGPL-3.0

## 智能体架构

| 智能体 | 角色 | 分析哲学 | 关联 MCP 服务器 |
|---|---|---|---|
| @Livermore | 市场分析师 | 趋势跟踪、关键点交易、量价验证 | mcp-aktools, financemcp-dcths, akshare-one-mcp, market-data-fetcher |
| @Buffett | 价值投资者 | 基本面分析、安全边际、长期持有 | china-stock-mcp, akshare-one-mcp, tushareMcp, market-data-fetcher |
| @CathieWood | 创新投资者 | 颠覆式技术、跨行业融合、5年视野 | financekit, market-data-fetcher |
| @SOLO Agent | 协调者 | 合并输出、保存报告、运行校验 | 文件系统 + 命令执行 |

## 工作流程

1. **学习历史聊天记录** — 所有智能体学习 `chatHistory/` 中的历史分析模式
2. **收集实时数据** — 每个智能体使用 MCP 工具和 WebSearch 收集最新数据
3. **多智能体讨论** — 4 个智能体共同讨论，为每个标的生成概率加权的情景预测
4. **合并并保存报告** — SOLO Agent 将所有输出合并为 Markdown 报告，保存到 `chatHistory/`
5. **校验覆盖率** — SOLO Agent 运行 `targets_validator.py`；若退出码为 1，则返回步骤 1 重新执行

## 走势预判情景

每个标的均基于以下六种概率加权情景进行评估：

1. 震荡偏强
2. 震荡偏弱
3. 震荡上行
4. 震荡下行
5. 直接上行
6. 直接下行

## 标的配置（targets.json）

所有分析标的通过 `targets.json` 统一管理。结构如下：

```json
{
  "a_shares": {
    "index_major": [{"name": "...", "code": "000001.SH"}],
    "sse_stocks": [{"name": "...", "code": "688981.SH"}],
    "sse_etf": [{"name": "...", "code": "513310.SH"}],
    "szse_stocks": [{"name": "...", "code": "000063.SZ"}],
    "szse_etf": [{"name": "", "code": ""}]
  },
  "hk_shares": {
    "index_major": [{"name": "...", "code": "800000.HK"}],
    "hkex_stocks": [{"name": "...", "code": "00700.HK"}],
    "hkex_etf": [{"name": "...", "code": "02800.HK"}]
  },
  "us_shares": {
    "index_major": [{"name": "...", "code": ".NDX"}],
    "stocks": [{"name": "...", "code": "NVDA"}],
    "adr": [{"name": "...", "code": "BABA"}],
    "etf": [{"name": "...", "code": "QQQ"}]
  }
}
```

`name` 和 `code` 为空的条目为占位符，请根据需要填写或删除。

## 校验脚本

```bash
python targets_validator.py <report.md> [--targets <targets.json>]
```

- 退出码 `0`：全部覆盖，无遗漏
- 退出码 `1`：存在遗漏或多余标的

脚本从 `targets.json` 中提取所有有效标的（`name` 和 `code` 均非空的条目），然后在研报 Markdown 中逐一搜索每个标的的名称或代码。

## 代码规范

- `targets_validator.py` 使用 Python 3.10+ 类型提示（如 `list[dict]` 而非 `List[Dict]`）
- 脚本读取文件时使用 `encoding="utf-8"` 以正确处理中文字符
- 股票代码变体会被匹配检查（如 `00700.HK` 同时匹配 `00700`；`688981.SH` 同时匹配 `688981`）
- 报告以 Markdown 文件保存至 `chatHistory/`，命名格式如 `全市场走势预判_YYYYMMDD.md`
- 报告语言以中文为主，股票代码和技术术语使用英文

## MCP 服务器配置

MCP 服务器配置在 `.trae/mcp.json` 中（已 git 忽略）。使用 `.trae/mcp.json.example` 作为模板。需要填写的凭证：

- **Longport**：`LONGPORT_APP_KEY`、`LONGPORT_APP_SECRET`、`LONGPORT_ACCESS_TOKEN`
- **TuShare**：tushareMcp URL 中的 Token
- **TARGETS_JSON_PATH**：`targets.json` 的绝对路径

## 重要规则

- 禁止提交 `.trae/mcp.json` — 其中包含 API 密钥和令牌
- 禁止编造市场数据 — 所有价格数据必须基于真实最新数据
- 每个预判判断必须有明确的依据和证据
- 每条交易建议必须给出止损位，无任何例外
- 当市场方向不明确时，必须建议观望，不可强行给出方向
- 分析必须考虑宏观环境，不可脱离大背景谈个股
- A 股和港股分析需考虑北向/南向资金流向的影响
- 美股分析需考虑美联储政策和美元走势的影响
- 所有风险提示必须具体，不可使用"市场有风险，投资需谨慎"等空话

## 报告格式

生成的报告遵循以下结构：

1. **风险前置声明**
2. **宏观环境与市场基线**
3. **A股走势预判** — 每个标的包含四智能体观点和情景概率表
4. **港股走势预判** — 同上格式
5. **美股走势预判** — 同上格式
6. 每个标的包含：当前价格、四智能体分析、概率加权情景表及价格区间

## 关键文件说明

- `targets.json` — 所有分析标的的中央配置文件
- `targets_validator.py` — 确保报告覆盖完整性的校验脚本
- `agents_info/Livermore_info.md` — Livermore 智能体完整提示词（趋势跟踪分析）
- `agents_info/Buffet_info.md` — Buffett 智能体完整提示词（价值投资分析）
- `agents_info/CathieWood_info.md` — Cathie Wood 智能体完整提示词（创新投资分析）
- `chatHistory/` — 包含示例报告，展示预期输出格式
