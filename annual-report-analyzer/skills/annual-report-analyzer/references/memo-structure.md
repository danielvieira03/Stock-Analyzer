# Memo Structure and Markdown Syntax

Every memo uses the same sections in the same order, so readers learn where to find things and memos can be compared. Target length: 6-10 pages.

## Contents
- Header block (metadata)
- Section-by-section guide
- Source labels
- Markdown syntax supported by the PDF builder
- Disclaimer text
- Skeleton

## Header block (metadata)

The memo begins with a metadata block the PDF builder turns into a cover strip. Use these exact keys:

```
---
company: Apple Inc.
ticker: AAPL
rating: Buy
filing: Form 10-K, fiscal year ended September 28, 2024
date: 2026-09-28
price: $000.00 (as of 2026-09-28)
value_range: $000 - $000
horizon: 12 months
confidence: Medium
---
```

`rating` must be exactly `Buy`, `Hold`, or `Sell`. The builder colors the rating badge accordingly. `date` is the memo date. `price` includes its as-of date.

## Section-by-section guide

### 1. Executive Summary
Half a page. State the rating, the thesis in two or three sentences, the three to five facts that drive it, the main risk, and the valuation range versus the current price. A reader who stops here should still know what you think and why.

### 2. Company Information
What the company does, how it makes money, revenue by segment and geography, key products, customers, scale (revenue, employees, market cap), and any recent strategic changes. Include a small table of key facts if helpful.

### 3. Industry Analysis
Market size and growth, structure (fragmented vs concentrated), cycle sensitivity, regulation, secular tailwinds and headwinds, and the forces that determine industry profitability. Draw on web sources; label them.

### 4. Competitive Advantage
Does the company have a durable edge, and is it widening or narrowing? Assess the sources: scale, network effects, switching costs, brand, cost position, intangible assets, regulatory barriers. Name the main competitors and compare on the metrics that matter. Support claims with evidence such as margins persisting above peers, market share trends, or pricing power.

### 5. Management
Who runs the company, tenure and background, track record against past targets, capital allocation decisions, compensation alignment with shareholders, insider ownership and transactions, and governance (board independence, dual-class shares, related-party dealings). Be candid about strengths and concerns.

### 6. Financial Health
The core numbers with interpretation. Include a multi-year table (revenue, growth, margins, net income, FCF, net debt, key ratios), then discuss growth, profitability, cash generation, balance sheet strength, and capital allocation. Note accounting quality issues or non-GAAP adjustments. Include current valuation multiples versus history and peers.

### 7. Risks
Rank the risks by importance, not by where they appeared in the filing. For each major risk, describe it, explain how it would show up in the financials, and note any evidence it is already materializing. Distinguish company-specific risks from general market or macro risk. Include the strongest bear-case argument.

### 8. Recommendation: Buy / Hold / Sell
State the rating again and the reasoning through the four questions (quality, trajectory, price, risk). Present the bear / base / bull value range with assumptions. Give confidence, and what would make the view more positive or more negative.

### 9. Conclusion
One short paragraph: the final take and the single most important thing to watch.

### 10. Sources and Methodology
List the filing (form, period, filing date) and each web source with title, publisher, and access date. Note calculation conventions and any significant estimates or data gaps.

## Source labels

- `[F]` fact from the filing; add the item where practical, e.g. `[F, Item 7]`
- `[W]` fact from web research; add the source and date, e.g. `[W, Reuters, 2026-09-15]`
- Unlabeled statements are the analyst's own judgment

Apply labels to numbers, quotes, and non-obvious factual claims. Do not label every sentence; that makes the memo unreadable.

## Markdown syntax supported by the PDF builder

The builder handles a deliberately small set of syntax so output stays consistent:

- `---` metadata block at the very top (see above)
- `# Title` is ignored in favor of the cover block, but may be included for readability
- `## Section heading` and `### Subheading`
- Paragraphs separated by blank lines
- `- item` bullet lists (use sparingly)
- Pipe tables with a header separator row:
  ```
  | Metric | FY2022 | FY2023 | FY2024 |
  |--------|--------|--------|--------|
  | Revenue ($B) | 394.3 | 383.3 | 391.0 |
  ```
- `**bold**` and `*italic*` inline
- `> note` for a callout box (good for the key takeaway of a section)
- `---` on its own line after the metadata block inserts a horizontal rule

Avoid raw HTML, images, and nested lists. Use plain text for special characters; ampersands and angle brackets are handled automatically.

## Disclaimer text

Place this as the final paragraph of Sources and Methodology:

> This memo is an analytical summary based on public filings and publicly available information as of the date shown. It is for informational purposes only and does not constitute personalized investment advice, an offer, or a solicitation to buy or sell any security. Figures may contain errors or omissions; verify against primary sources before making decisions. Past performance does not guarantee future results.

## Skeleton

```
---
company: 
ticker: 
rating: 
filing: 
date: 
price: 
value_range: 
horizon: 12 months
confidence: 
---

## Executive Summary

## Company Information

## Industry Analysis

## Competitive Advantage

## Management

## Financial Health

## Risks

## Recommendation: Buy / Hold / Sell

## Conclusion

## Sources and Methodology
```
