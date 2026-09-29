# Stock-Analyzer

A Claude Code / Cowork plugin marketplace (`daniel-plugins`) containing one plugin:

**`annual-report-analyzer`** reads a public company's 10-K or 10-Q, adds current outside research, and produces a formatted PDF investment memo with a **Buy / Hold / Sell** rating.

## What it is

Give it a company and it does what an equity analyst would: it reads the filing, checks what the market and the news say, and writes up a view. The result is a 6-10 page memo a portfolio manager could read in ten minutes, ending in a Buy / Hold / Sell rating with a stated horizon (12 months by default), a valuation range and a confidence level.

## How a memo is built

1. **Intake:** company, filing type (latest 10-K by default, or a 10-Q) and an optional angle such as value or income.
2. **Get the filing:** use your upload, or find the latest 10-K or 10-Q on SEC EDGAR and confirm the fiscal period. If it can't be retrieved, it asks you to upload it rather than writing from memory.
3. **Read it deliberately:** business, specific (not boilerplate) risk factors, MD&A, financial statements and notes, legal proceedings and controls.
4. **Compute the financials:** growth, margins, free cash flow, debt and coverage, and capital allocation, with the inputs shown so you can check the math.
5. **Research outside the filing:** current price and multiples, news since the filing, competitors, management and insider activity, and the strongest bull and bear arguments.
6. **Form the view:** the rating comes from four questions (quality, trajectory, price, risk), not from the company's story. A great business isn't a Buy at any price, and a beaten-down one isn't a Buy just because it fell.
7. **Write and render:** ten fixed sections, from Executive Summary to Sources and Methodology, rendered to a PDF with a cover strip showing the rating.

## How to read a memo

- Claims from the filing are tagged **[F]**, and claims from web research are tagged **[W]** with source and date. Untagged statements are the analyst's own judgment, so you can tell what the company says from what independent sources say.
- Every calculated figure shows its inputs, and market data carries its as-of date.
- The bear case is required, and anything missing is flagged rather than invented.

## Install

In the Claude app (Cowork): open the plugins area, choose to add a marketplace from GitHub, and paste the repo link:

```
https://github.com/danielvieira03/Stock-Analyzer
```

Then install `annual-report-analyzer` from the `daniel-plugins` marketplace.

In Claude Code:

```
/plugin marketplace add danielvieira03/Stock-Analyzer
/plugin install annual-report-analyzer@daniel-plugins
```

## Use

```
/analyze-stock NVDA
```

Or ask in plain language: "Analyze Costco's latest 10-K and give me an investment memo." You can also upload a filing; otherwise Claude fetches it from SEC EDGAR.

The PDF step needs Python with `reportlab` (`pip install reportlab`). Without it, the memo is delivered as Markdown in chat.

## What's in a memo

Ten sections, always in the same order: Executive Summary, Company Information, Industry Analysis, Competitive Advantage, Management, Financial Health, Risks, Recommendation (Buy / Hold / Sell), Conclusion, and Sources and Methodology.

## Installing the skill on its own (without the plugin)

**Claude.ai (Pro, Max, Team, Enterprise):** zip the `annual-report-analyzer/skills/annual-report-analyzer` folder (the one containing `SKILL.md`) and upload it under Settings > Capabilities > Skills. Code execution must be enabled so the PDF can be generated.

**Claude Code (manual):** copy that same folder into `~/.claude/skills/` (personal) or `.claude/skills/` inside a project. To get the slash command too, copy `annual-report-analyzer/commands/analyze-stock.md` into `~/.claude/commands/` or a project's `.claude/commands/`, since without the plugin wrapper the two aren't linked.

## Repo layout

```
.claude-plugin/
└── marketplace.json             # Marketplace listing (daniel-plugins)
annual-report-analyzer/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   └── analyze-stock.md         # The /analyze-stock slash command
└── skills/
    └── annual-report-analyzer/
        ├── SKILL.md             # Workflow and writing standards (what Claude reads)
        ├── references/
        │   ├── filing-guide.md      # Where to look in a 10-K / 10-Q, red flags, EDGAR tips
        │   ├── financial-metrics.md # Metric definitions and sector adjustments
        │   ├── rating-framework.md  # How Buy / Hold / Sell is decided
        │   └── memo-structure.md    # Section guide, source labels, markdown syntax
        ├── scripts/
        │   └── build_memo_pdf.py    # Renders the memo Markdown to a consistent PDF
        └── examples/
            └── sample-memo.md       # Illustrative memo showing the format (fake data)
```

## Customizing

- **Rating logic:** edit `references/rating-framework.md`.
- **Sections or tone:** edit `references/memo-structure.md` and the workflow in `SKILL.md`.
- **Look and feel of the PDF:** change the palette at the top of `scripts/build_memo_pdf.py`.
- **Filing-only mode:** to ground the memo strictly in the filing, delete step 5 in `SKILL.md` and the `[W]` label convention.

## Limitations

- Web research quality depends on what search returns; check the Sources section.
- Market prices and multiples go stale quickly. The memo states the date they were pulled.
- Foreign private issuers (20-F) and very new IPOs may need manual guidance.

## Disclaimer

Output is an analytical summary for informational purposes only. It is not personalized investment advice or a solicitation to buy or sell any security. Verify figures against primary sources before making decisions.
