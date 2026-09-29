# Stock-Analyzer

A Claude Code / Cowork plugin marketplace (`daniel-plugins`) containing one plugin:

**`annual-report-analyzer`** reads a public company's 10-K or 10-Q, adds current outside research, and produces a formatted PDF investment memo with a **Buy / Hold / Sell** rating.

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

See [`annual-report-analyzer/README.md`](annual-report-analyzer/README.md) for what the memo contains, customization, and limitations.

## Disclaimer

Output is an analytical summary for informational purposes only. It is not personalized investment advice or a solicitation to buy or sell any security. Verify figures against primary sources before making decisions.
