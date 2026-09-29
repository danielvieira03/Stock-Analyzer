# Annual Report Analyzer (skill)

Reads a public company's 10-K or 10-Q, adds current outside research, and produces a formatted investment memo with a **Buy / Hold / Sell** rating.

This skill is bundled as part of the `annual-report-analyzer` Claude Code plugin — see the repo root README for how to install the whole plugin (skill + `/analyze-stock` command) in one step. This file documents the skill itself.

## What you get

A PDF memo (typically 6-10 pages) with the same structure every time:

1. Executive Summary
2. Company Information
3. Industry Analysis
4. Competitive Advantage
5. Management
6. Financial Health
7. Risks
8. Recommendation: Buy / Hold / Sell
9. Conclusion
10. Sources and Methodology

Facts from the filing are tagged `[F]` and facts from web research are tagged `[W]`, so you can tell what the company says from what independent sources say.

## How to use it

Once the plugin is installed, either run the command:

```
/analyze-stock NVDA
```

or just ask in plain language:

- "Analyze Costco's latest 10-K and give me an investment memo."
- "Here's NVIDIA's 10-Q. Should I buy, hold, or sell?"

You can also upload the filing directly. Otherwise, Claude looks it up on SEC EDGAR.

## Installing this skill on its own (without the plugin)

If you'd rather not use the plugin/marketplace system:

**Claude.ai (Pro, Max, Team, Enterprise):** zip this `annual-report-analyzer` folder (the one containing `SKILL.md`), then upload it under Settings > Capabilities > Skills. Code execution must be enabled so the PDF can be generated.

**Claude Code (manual):** copy this folder into `~/.claude/skills/` (personal) or `.claude/skills/` inside a project. You'd then also need to copy `commands/analyze-stock.md` from the plugin into `~/.claude/commands/` or a project's `.claude/commands/` separately to get the slash command, since without the plugin wrapper the two aren't linked automatically.

The PDF step needs Python with `reportlab` (`pip install reportlab`). Claude.ai's code environment handles this for you.

## Repo layout (this folder)

```
annual-report-analyzer/            # (the skill, inside skills/ at the plugin root)
├── SKILL.md                     # Workflow and writing standards (what Claude reads)
├── README.md                    # This file
├── references/
│   ├── filing-guide.md          # Where to look in a 10-K / 10-Q, red flags, EDGAR tips
│   ├── financial-metrics.md     # Metric definitions and sector adjustments
│   ├── rating-framework.md      # How Buy / Hold / Sell is decided
│   └── memo-structure.md        # Section guide, source labels, markdown syntax
├── scripts/
│   └── build_memo_pdf.py        # Renders the memo Markdown to a consistent PDF
└── examples/
    └── sample-memo.md           # Illustrative memo showing the format (fake data)
```

## Customizing

- **Rating logic**: edit `references/rating-framework.md`.
- **Sections or tone**: edit `references/memo-structure.md` and the workflow in `SKILL.md`.
- **Look and feel of the PDF**: change the palette at the top of `scripts/build_memo_pdf.py`.
- **Filing-only mode**: to ground the memo strictly in the filing, delete step 5 in `SKILL.md` and the `[W]` label convention.

## Limitations

- Web research quality depends on what search returns; check the Sources section.
- Market prices and multiples go stale quickly. The memo states the date they were pulled.
- Foreign private issuers (20-F) and very new IPOs may need manual guidance.

## Disclaimer

Output is an analytical summary for informational purposes only. It is not personalized investment advice or a solicitation to buy or sell any security. Verify figures against primary sources before making decisions.
