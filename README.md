# MarketForecastingAgents

An AI-powered market research report auto-generation system based on multi-agent collaboration, covering A-shares, Hong Kong stocks, and US stocks.

[中文文档](README_cn.md)

***

## Features

- **Multi-Agent Collaboration**: Leverages three specialized investment agents — Livermore (trend-following), Buffett (value investing), and Cathie Wood (disruptive innovation) — each with distinct analytical philosophies, providing multi-perspective market assessments.
- **Full Market Coverage**: Supports A-shares (SSE/SZSE), Hong Kong stocks (HKEX), and US stocks (NYSE/NASDAQ), including indices, individual stocks, and ETFs.
- **Real-Time Data Integration**: Connects to multiple MCP (Model Context Protocol) servers for real-time market data, financial statements, technical indicators, sector fund flows, and research reports.
- **Automated Validation**: Built-in `targets_validator.py` ensures generated reports fully cover all configured targets with zero omissions.
- **Flexible Target Configuration**: All analysis targets are managed through a single `targets.json` file — add, remove, or modify entries as needed.

***

## System Architecture

### Agent Team

| Agent           | Role                | Analytical Philosophy                                             | MCP / Capabilities                                          |
| --------------- | ------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| **@Livermore**  | Market Analyst      | Trend-following, key-point trading, volume-price confirmation     | Custom MCP servers + Web Search + Financial market analysis |
| **@Buffett**    | Value Investor      | Fundamental analysis, margin of safety, long-term holding         | China Stock MCP + Market Data Fetcher + Research reports    |
| **@CathieWood** | Innovation Investor | Disruptive technology, convergence across sectors, 5-year horizon | FinanceKit + Market Data Fetcher + Research reports         |
| **@SOLO Agent** | Coordinator         | Merges outputs from all agents, saves reports, runs validation    | File system + Command execution                             |

### MCP Servers

| MCP Server              | Function                                                                                | Connected Agents               |
| ----------------------- | --------------------------------------------------------------------------------------- | ------------------------------ |
| **market-data-fetcher** | Fetches index, stock, and ETF data (Longport / AKShare / Yahoo Finance)                 | Livermore, Buffett, CathieWood |
| **financekit**          | Stock quotes, company info, technical analysis, risk metrics, options chain             | CathieWood                     |
| **china-stock-mcp**     | A-share financial data, balance sheets, income statements, cash flows, shareholder info | Buffett                        |
| **mcp-aktools**         | AKShare-based tools: stock indicators, sector fund flows, trading suggestions           | Livermore                      |
| **financemcp-dcths**    | Tonghuashun (THS) and Dongfang Caifu (DC) sector indices, members, and daily data       | Livermore                      |
| **akshare-one-mcp**     | Historical data, real-time data, financial metrics (HTTP-based)                         | Livermore, Buffett             |
| **Time**                | Current time and timezone conversion                                                    | All agents                     |
| **FaXianBaoGao (发现报告)** | Research report search and content retrieval                                            | All agents                     |
| **tushareMcp**          | TuShare financial data API (HTTP-based)                                                 | Buffett                        |

### Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Instruction                          │
│  (Sent to SOLO Agent in TRAE CN SOLO mode)                       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 1: Learn from Chat History                                 │
│  All agents study past analysis patterns in chatHistory/          │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 2: Gather Real-Time Data                                   │
│  Each agent uses MCP tools and WebSearch to collect latest data   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 3: Multi-Agent Deliberation                                │
│  All 4 agents discuss and produce a consolidated market forecast  │
│  with probability-weighted scenarios for each target              │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 4: Merge & Save Report                                     │
│  SOLO Agent merges all outputs into a Markdown report             │
│  saved to chatHistory/                                           │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 5: Validate Coverage                                       │
│  SOLO Agent runs targets_validator.py                            │
│  If exit code = 1 → loop back to Step 1                         │
│  If exit code = 0 → done ✓                                       │
└──────────────────────────────────────────────────────────────────┘
```

***

## Project Structure

```
MarketForecastingAgents
├── .trae/
│   ├── mcp.json.example       # MCP server configuration template
│   └── rules/
│       ├── toolcallingrules.md # Tool calling rules (English)
│       └── 工具调用规则.md      # Tool calling rules (Chinese)
├── agents_info/
│   ├── Livermore_info.md      # Livermore agent prompt & instructions
│   ├── Buffet_info.md         # Buffett agent prompt & instructions
│   └── CathieWood_info.md     # Cathie Wood agent prompt & instructions
├── chatHistory/               # Generated research reports & chat logs
│   ├── 全市场走势预判_20260513.md  # Full market forecast report
│   ├── 港股走势预判_20260513.md    # HK market forecast report
│   └── ...
├── targets.json               # Target configuration (indices, stocks, ETFs)
├── targets_validator.py       # Report coverage validation script
├── .gitignore
├── LICENSE                    # AGPL-3.0
├── README.md                  # This file (English)
└── README_cn.md               # Chinese documentation
```

***

## Target Configuration (targets.json)

All analysis targets are managed through `targets.json` in the project root directory, covering A-shares, Hong Kong stocks, and US stocks. The file supports flexible configuration of indices, individual stocks, and ETFs. Users can directly edit this file to add or remove targets.

### Structure

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

### Current Preset Targets

- **A-Share Indices**: SSE Composite (000001.SH), SZSE Component (399001.SZ)
- **A-Share Stocks**: SMIC (688981.SH), ZTE (000063.SZ)
- **A-Share ETFs**: China-Korea Semiconductor ETF (513310.SH)
- **HK Indices**: Hang Seng Index (800000.HK), Hang Seng Tech Index (800700.HK)
- **HK Stocks**: Tencent, Alibaba, Xiaomi, Kuaishou, JD.com, Meituan, SMIC, Pop Mart, CATL, BYD, HKEX, AIA, China Mobile, NetEase, Baidu, Li Auto, XPeng, Anta, Horizon Robotics, and 20+ more
- **HK ETFs**: Tracker Fund (02800.HK), CSOP Hang Seng Tech (03033.HK)
- **US Indices**: NASDAQ 100 (.NDX), S\&P 500 (.SPX)
- **US Stocks**: NVIDIA (NVDA)
- **US ADRs**: Alibaba (BABA)
- **US ETFs**: QQQ, SPY

> **Note**: Entries with empty `name` and `code` fields are placeholders — fill them in or remove them as needed.

***

## Report Validation (targets\_validator.py)

The `targets_validator.py` script verifies that a generated research report fully covers all targets defined in `targets.json`.

### Usage

```bash
python targets_validator.py <report.md> [--targets <targets.json>]
```

### What It Does

1. Extracts all valid targets from `targets.json` (entries where both `name` and `code` are non-empty)
2. Searches the report markdown for each target's name or code
3. Outputs: missing targets list, coverage statistics

### Exit Codes

| Code | Meaning                           |
| ---- | --------------------------------- |
| `0`  | All targets covered, no omissions |
| `1`  | Missing or extra targets detected |

***

## Getting Started

### Prerequisites

- [TRAE CN](https://www.trae.com.cn/) IDE with SOLO mode support
- Python 3.10+ (for running `targets_validator.py`)
- [uv](https://github.com/astral-sh/uv) (for MCP server installation via `uvx`)
- [Node.js](https://nodejs.org/) (for MCP server installation via `npx`)
- Optional: [Longport](https://longportapp.com/) account for real-time HK/US market data

### Setup

1. **Configure MCP Servers**: Copy the example configuration and fill in your credentials:
   ```bash
   cp .trae/mcp.json.example .trae/mcp.json
   ```
   Edit `.trae/mcp.json` and replace placeholder values:
   - `LONGPORT_APP_KEY`, `LONGPORT_APP_SECRET`, `LONGPORT_ACCESS_TOKEN` — your Longport API credentials
   - `TARGETS_JSON_PATH` — absolute path to your `targets.json`
   - `tushareMcp` URL — replace `your_tushare_token_here` with your TuShare token
2. **Configure Targets**: Edit `targets.json` to add, remove, or modify the indices, stocks, and ETFs you want to analyze.
3. **Set Up Agents**: Import the three agents into TRAE CN using the links in `agents_info/`:
   - Livermore: See `agents_info/Livermore_info.md` for the prompt
   - Buffett: See `agents_info/Buffet_info.md` for the prompt
   - Cathie Wood: See `agents_info/CathieWood_info.md` for the prompt

### Generating a Research Report

After configuration, switch to **SOLO mode** in TRAE CN and send the following instruction to the SOLO Agent:

```PlainText
1. Learn the financial market analysis logic and response framework from the files in /path/to/MarketForecastingAgents/chatHistory/ together with @Livermore @Buffett @CathieWood;
2. All 4 agents (@Livermore @Buffett @CathieWood @SOLO Agent) use MCP tools or WebSearch to gather as much latest data and information as possible;
3. All 4 agents (@Livermore @Buffett @CathieWood @SOLO Agent) discuss and produce a forecast for the next 6 months for all targets in /path/to/MarketForecastingAgents/targets.json, assigning probability values and price ranges for each of the following scenarios with reasoning: 1. Range-bound with bullish bias; 2. Range-bound with bearish bias; 3. Volatile uptrend; 4. Volatile downtrend; 5. Direct uptrend; 6. Direct downtrend.
4. @SOLO Agent merges the outputs from @Livermore @Buffett @CathieWood and @SOLO Agent, saves the merged content as a Markdown document in /path/to/MarketForecastingAgents/chatHistory/;
5. @SOLO Agent runs /path/to/MarketForecastingAgents/targets_validator.py — if the exit code is 1, repeat steps 1-4 until the exit code is 0.
```

> **Important**: Replace `/path/to/MarketForecastingAgents/` with the actual absolute path on your system.

***

## Forecast Scenarios

Each target in the generated report is evaluated against six probability-weighted scenarios:

| # | Scenario                      | Description                                                |
| - | ----------------------------- | ---------------------------------------------------------- |
| 1 | Range-bound with bullish bias | Price oscillates within a range but leans upward           |
| 2 | Range-bound with bearish bias | Price oscillates within a range but leans downward         |
| 3 | Volatile uptrend              | Price trends upward with significant oscillations          |
| 4 | Volatile downtrend            | Price trends downward with significant oscillations        |
| 5 | Direct uptrend                | Price moves steadily upward without significant pullbacks  |
| 6 | Direct downtrend              | Price moves steadily downward without significant rebounds |

***

## Disclaimer

The research reports generated by this project are for reference only and do not constitute any investment advice. Financial markets carry inherent risks — invest with caution and always conduct your own due diligence.

## License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).
