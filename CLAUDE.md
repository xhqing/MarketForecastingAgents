# CLAUDE.md

This file provides guidance to TRAE CN when working with this project.

## Project Overview

MarketForecastingAgents is an AI-powered market research report auto-generation system based on multi-agent collaboration, covering A-shares, Hong Kong stocks, and US stocks. It runs within TRAE CN IDE's SOLO mode, orchestrating three specialized investment agents to produce probability-weighted market forecasts.

## Project Structure

```
MarketForecastingAgents/
├── .trae/
│   ├── mcp.json              # MCP server configuration (git-ignored, contains secrets)
│   ├── mcp.json.example       # MCP server configuration template
│   └── rules/
│       ├── toolcallingrules.md  # Tool calling rules (English)
│       └── 工具调用规则.md       # Tool calling rules (Chinese)
├── agents_info/
│   ├── Livermore_info.md      # Livermore agent prompt & instructions
│   ├── Buffet_info.md         # Buffett agent prompt & instructions
│   └── CathieWood_info.md     # Cathie Wood agent prompt & instructions
├── chatHistory/               # Generated research reports & chat logs
├── targets.json               # Target configuration (indices, stocks, ETFs)
├── targets_validator.py       # Report coverage validation script
├── .gitignore
├── LICENSE                    # AGPL-3.0
├── README.md                  # English documentation
└── README_cn.md               # Chinese documentation
```

## Tech Stack

- **Runtime**: Python 3.10+ (for `targets_validator.py`)
- **IDE**: TRAE CN with SOLO mode
- **MCP Servers**: Installed via `uvx` (Python) and `npx` (Node.js)
- **Data Sources**: Longport API, AKShare, TuShare, Tonghuashun, Dongfang Caifu, Yahoo Finance
- **License**: AGPL-3.0

## Agent Architecture

| Agent | Role | Philosophy | Key MCP Servers |
|---|---|---|---|
| @Livermore | Market Analyst | Trend-following, key-point trading, volume-price confirmation | mcp-aktools, financemcp-dcths, akshare-one-mcp, market-data-fetcher |
| @Buffett | Value Investor | Fundamental analysis, margin of safety, long-term holding | china-stock-mcp, akshare-one-mcp, tushareMcp, market-data-fetcher |
| @CathieWood | Innovation Investor | Disruptive technology, convergence, 5-year horizon | financekit, market-data-fetcher |
| @SOLO Agent | Coordinator | Merges outputs, saves reports, runs validation | File system + command execution |

## Workflow

1. **Learn from Chat History** — All agents study past analysis patterns in `chatHistory/`
2. **Gather Real-Time Data** — Each agent uses MCP tools and WebSearch to collect latest data
3. **Multi-Agent Deliberation** — All 4 agents discuss and produce probability-weighted scenario forecasts for each target
4. **Merge & Save Report** — SOLO Agent merges all outputs into a Markdown report saved to `chatHistory/`
5. **Validate Coverage** — SOLO Agent runs `targets_validator.py`; if exit code = 1, loop back to step 1

## Forecast Scenarios

Each target is evaluated against six probability-weighted scenarios:

1. 震荡偏强 (Range-bound with bullish bias)
2. 震荡偏弱 (Range-bound with bearish bias)
3. 震荡上行 (Volatile uptrend)
4. 震荡下行 (Volatile downtrend)
5. 直接上行 (Direct uptrend)
6. 直接下行 (Direct downtrend)

## Target Configuration (targets.json)

All analysis targets are managed through `targets.json`. Structure:

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

Entries with empty `name` and `code` are placeholders — fill them in or remove them.

## Validation Script

```bash
python targets_validator.py <report.md> [--targets <targets.json>]
```

- Exit code `0`: All targets covered, no omissions
- Exit code `1`: Missing or extra targets detected

The script extracts all valid targets (where both `name` and `code` are non-empty) from `targets.json` and searches the report markdown for each target's name or code.

## Code Conventions

- `targets_validator.py` uses Python 3.10+ type hints (e.g., `list[dict]` instead of `List[Dict]`)
- The script reads files with `encoding="utf-8"` to handle Chinese characters
- Stock code variants are checked (e.g., `00700.HK` also matches `00700`; `688981.SH` also matches `688981`)
- Reports are saved as Markdown files in `chatHistory/` with naming pattern like `全市场走势预判_YYYYMMDD.md`
- Report language is primarily Chinese with English stock codes and technical terms

## MCP Server Configuration

MCP servers are configured in `.trae/mcp.json` (git-ignored). Use `.trae/mcp.json.example` as template. Required credentials:

- **Longport**: `LONGPORT_APP_KEY`, `LONGPORT_APP_SECRET`, `LONGPORT_ACCESS_TOKEN`
- **TuShare**: Token in tushareMcp URL
- **TARGETS_JSON_PATH**: Absolute path to `targets.json`

## Important Rules

- Never commit `.trae/mcp.json` — it contains API keys and tokens
- Never fabricate market data — all price data must be based on real, latest data
- Each forecast judgment must have clear reasoning and evidence
- Stop-loss levels are mandatory for every trading recommendation
- When market direction is unclear, recommend observation rather than forced direction
- Analysis must consider macro environment — never discuss individual stocks in isolation
- A-share and HK analysis must consider northbound/southbound capital flows
- US stock analysis must consider Federal Reserve policy and USD trends
- All risk warnings must be specific — no generic "market has risk" disclaimers

## Report Format

Generated reports follow this structure:

1. **风险前置声明** (Risk Disclaimer)
2. **宏观环境与市场基线** (Macro Environment & Market Baseline)
3. **A股走势预判** (A-Share Forecasts) — per target with four-agent views and scenario table
4. **港股走势预判** (HK Share Forecasts) — same format
5. **美股走势预判** (US Share Forecasts) — same format
6. Each target includes: current price, four-agent analysis, probability-weighted scenario table with price ranges

## Key Files to Understand

- `targets.json` — Central configuration for all analysis targets
- `targets_validator.py` — Ensures report completeness
- `agents_info/Livermore_info.md` — Full prompt for the Livermore agent (trend-following analysis)
- `agents_info/Buffet_info.md` — Full prompt for the Buffett agent (value investing analysis)
- `agents_info/CathieWood_info.md` — Full prompt for the Cathie Wood agent (innovation investing analysis)
- `chatHistory/` — Contains example reports showing expected output format
