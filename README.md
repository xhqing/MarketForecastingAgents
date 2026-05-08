# MarketForecastingAgents

基于多智能体协作的 AI 市场研究报告自动生成系统，覆盖 A 股、港股、美股三大市场。

## 系统架构

本项目采用 **多智能体协作架构**，由一个总控 Agent（TRAE CN SOLO Coder）统一调度 7 个专项智能体，各司其职完成数据获取、市场分析和研报撰写。

```
                        ┌───────────────────────────────┐
                        │     TRAE CN SOLO Coder        │
                        │         （总控 Agent）           │
                        └───────┬───────────┬───────────┘
                                │           │
        ┌───────────────────────┤           ├───────────────────────┐
        │                       │           │                       │
        ▼                       ▼           ▼                       ▼
┌───────────────┐   ┌───────────────┐   ┌───────────┐   ┌─────────────────┐
│ 数据获取智能体  │   │  市场分析智能体  │   │ 研报撰写智能体│   │   浏览器预览      │
│  (×5 个)      │   │  (Livermore)  │   │   (Report  │   │                 │
│               │   │               │   │  Generator)│   │                 │
└───────────────┘   └───────────────┘   └───────────┘   └─────────────────┘
```

### 智能体团队

| 智能体 | 角色 | 使用的 MCP / 能力 |
|--------|------|-------------------|
| **@MarketDataFetcher001** | 主数据获取 | `market-data-fetcher` MCP 服务器（优先使用） |
| **@MarketDataFetcher002** | 辅助数据获取 | 自有的独立 MCP 服务器 |
| **@MarketDataFetcher003** | 辅助数据获取 | 自有的独立 MCP 服务器 |
| **@MarketDataFetcher004** | 辅助数据获取 | 自有的独立 MCP 服务器 |
| **@MarketDataFetcher005** | 辅助数据获取 | 自有的独立 MCP 服务器 |
| **@Livermore** | 市场分析 | 自有 MCP 服务器 + 网络搜索 + 金融市场分析能力 |
| **@Report Generator** | 研报撰写 | `report-generator` MCP 服务器 |

### MCP 服务器

| MCP 服务器 | 功能 | 关联智能体 |
|------------|------|-----------|
| `market-data-fetcher` | 主要数据获取（指数、股票、ETF 实时/历史行情） | MarketDataFetcher001（优先） |
| `report-generator` | 生成空研报模板 + 写入最终完整研报 | Report Generator |
| 各智能体自有 MCP | 辅助补充数据获取、多源交叉验证 | MarketDataFetcher002 ~ 005 |

### 工作流程

```
Step 1: 生成模板
  Report Generator ──report-generator MCP──▶ 空研报模板 ──▶ 所有智能体

Step 2: 数据获取
  MarketDataFetcher001 ──market-data-fetcher MCP──▶ 主要数据 ──┐
  MarketDataFetcher002~005 ──各自 MCP──▶ 补充数据 ────────────┤
                                                                ▼
                                                       整理后的最新数据

Step 3: 市场分析
  Livermore ◀── 研报模板 + 最新数据
  Livermore ──MCP + WebSearch + 金融分析──▶ 分析结果 ──▶ Report Generator

Step 4: 生成研报
  Report Generator ──report-generator MCP──▶ 最终完整研报 (.html)

Step 5: 浏览器预览
  自动打开生成的研报
```

## 项目结构

```
MarketForecastingAgents
├── README.md                 # 项目说明
├── targets.json              # 标的配置文件（用户维护）
└── .trae/                    # TRAE CN 配置目录
    ├── mcp.json              # MCP 服务器配置
    └── agents/               # 自定义智能体配置
        ├── MarketDataFetcher001.md
        ├── MarketDataFetcher002.md
        ├── MarketDataFetcher003.md
        ├── MarketDataFetcher004.md
        ├── MarketDataFetcher005.md
        ├── Livermore.md
        └── Report Generator.md
```

## 标的配置（targets.json）

所有分析标的通过项目根目录下的 `targets.json` 统一管理，覆盖 A 股、港股、美股三大市场，支持指数、个股和 ETF 的灵活配置。用户可直接编辑该文件增删标的。

当前预设标的包括：

- **港股指数**：恒生指数 (HSI)、恒生科技指数 (HSTECH)、国企指数 (HSCEI)
- **美股指数**：标普 500 (.SPX)、纳斯达克 100 (.NDX)、道琼斯工业 (.DJI)
- **港股个股**：腾讯控股、阿里巴巴、小米、快手、京东、美团、紫金矿业、中芯国际、华虹半导体、泡泡玛特、中国神华、宁德时代、赣锋锂业、昆仑能源、中国石油化工股份、国泰君安国际、中国宏桥、招商银行、建设银行、中国银行、汇丰控股、信达生物、药明生物、中国海洋石油、中国石油股份、工商银行、比亚迪股份、香港交易所、友邦保险、中国人寿、中国平安、中国移动、网易、百度集团、理想汽车、小鹏汽车、安踏体育、地平线机器人等
- **港股 ETF**：盈富基金、南方恒生科技、恒生中国企业
- **美股 ETF**：QQQ、SPY、DIA
- **A 股**：预留配置结构，可按需填入

## 数据获取策略

数据获取采用**优先级 + 多源交叉验证**策略：

1. **优先**由 `MarketDataFetcher001` 通过 `market-data-fetcher` MCP 服务器获取指数、股票、ETF 的实时行情和历史数据
2. **其次**由 `MarketDataFetcher002 ~ 005` 利用各自独立的 MCP 服务器进行补充数据获取和交叉验证，确保数据完整性和准确性
3. 所有数据按 `targets.json` 中配置的标的逐一获取，整理后统一交付给 `Livermore` 进行分析

## 使用方式

### 前置准备

1. **配置 MCP 服务器**：在 `.trae/mcp.json` 中配置 `market-data-fetcher` 和 `report-generator` 两个 MCP 服务器，以及各数据智能体自有的 MCP 连接信息。

2. **配置自定义智能体**：在 `.trae/agents/` 目录下完成 7 个智能体的自定义配置（`MarketDataFetcher001 ~ 005`、`Livermore`、`Report Generator`）。

3. **配置标的**：根据需要编辑 `targets.json`，增删需要分析的指数、股票和 ETF。

### 生成研报

配置完成后，在 TRAE CN 中切换到 **SOLO 模式**，向 SOLO Coder 发送以下指令：

```markdown
与你的下级智能体(@MarketDataFetcher001 @MarketDataFetcher002 @MarketDataFetcher003 @MarketDataFetcher004 @MarketDataFetcher005 @Livermore @Report Generator)通力合作，生成一份最新的市场研究报告。 

 具体步骤： 
     1、首先让@Report Generator利用report-generator MCP服务器生成空的研报模板并把这个空的研报模板给到所有其他智能体(@MarketDataFetcher001 @MarketDataFetcher002 @MarketDataFetcher003 @MarketDataFetcher004 @MarketDataFetcher005 @Livermore)。 
     2、(@MarketDataFetcher001 @MarketDataFetcher002 @MarketDataFetcher003 @MarketDataFetcher004 @MarketDataFetcher005)根据研报模板和当前项目根目录下的targets.json文件得知需要哪些最新数据后开始利用各自的MCP服务器去获取数据，优先让@MarketDataFetcher001利用market-data-fetcher MCP服务器获取数据，其次再考虑另外4个数据获取智能体(@MarketDataFetcher002 @MarketDataFetcher003 @MarketDataFetcher004 @MarketDataFetcher005)协助获取最新数据，最后把这些最新数据整理后给到@Livermore。 
     3、Livemore根据研报模板、最新市场数据、自己的MCP服务器、网络搜索技能和金融市场分析能力对targets.json里配置的所有标的进行深入分析，分析后把需要在研报里面展示的所有数据和信息给到@Report Generator。 
     4、@Report Generator根据这些数据和信息再次利用report-generator MCP服务器生成最终的完整研报。 

 报告生成后，直接在浏览器中打开它。
```

智能体团队将自动按流程协作：**生成模板 → 获取数据 → 市场分析 → 撰写研报**，完成后自动在浏览器中打开生成的研报。

## 免责声明

本项目生成的研报仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。

## 许可证

本项目采用 [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE) 开源许可证。
