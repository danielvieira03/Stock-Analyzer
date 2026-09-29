---
description: Analyze a company's 10-K/10-Q and produce a Buy/Hold/Sell investment memo
argument-hint: [ticker or company name] [optional: path to filing]
---

Use the `annual-report-analyzer` skill (bundled with this plugin) to analyze $ARGUMENTS.

Follow the skill's workflow exactly: intake, retrieve the filing, read it deliberately, compute the financial picture, research outside the filing, form the view, write the memo, and produce the PDF. If $ARGUMENTS is empty, ask which company and which filing (10-K or 10-Q) before proceeding.
