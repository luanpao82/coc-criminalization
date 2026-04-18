"""Generate a static HTML review interface from corpus_diffs.csv.

One page, three tabbed sections:
  * True value mismatches (both manual and auto have values, disagree)
  * Manual-blank auto-fills (manual blank, auto proposes value — easy backfills)
  * Needs-review flagged by extractor itself

Each row shows coc_id, year, field_id, manual, auto, source_page, and a
placeholder "accept / edit / reject" action column. For now the decision
is recorded by copy-pasting a resolution column; the full workflow would
replace this with a small database-backed UI.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path

from pipeline_utils import PIPELINE_DIR

DIFFS = PIPELINE_DIR / "corpus_diffs.csv"
OUT = PIPELINE_DIR / "review_ui.html"


def main():
    rows = list(csv.DictReader(open(DIFFS)))
    mismatches = [r for r in rows if r["manual_value"] and r["auto_value"]]
    autofills = [r for r in rows if not r["manual_value"] and r["auto_value"]]
    other = [r for r in rows if not r["auto_value"]]

    def table(rlist, caption, section_id):
        out = [f'<section id="{section_id}"><h2>{caption} ({len(rlist):,})</h2>']
        out.append("<table><thead><tr>")
        for h in ("CoC", "Year", "Field", "Class", "Manual", "Auto", "Source p.", "Reason"):
            out.append(f"<th>{h}</th>")
        out.append("</tr></thead><tbody>")
        for r in rlist[:2000]:  # cap for browser perf
            m = html.escape(str(r.get("manual_value", "") or "")[:80])
            a = html.escape(str(r.get("auto_value", "") or "")[:80])
            reason = html.escape(str(r.get("reason", "") or "")[:80])
            out.append(
                f"<tr>"
                f"<td>{html.escape(r['coc_id'])}</td>"
                f"<td>{html.escape(r['year'])}</td>"
                f"<td><code>{html.escape(r['field_id'])}</code></td>"
                f"<td>{html.escape(r['class'])}</td>"
                f"<td class='m'>{m}</td>"
                f"<td class='a'>{a}</td>"
                f"<td>{html.escape(str(r.get('source_page') or ''))}</td>"
                f"<td class='r'>{reason}</td>"
                f"</tr>"
            )
        if len(rlist) > 2000:
            out.append(f"<tr><td colspan='8'><em>...{len(rlist) - 2000:,} more rows not shown (see corpus_diffs.csv)</em></td></tr>")
        out.append("</tbody></table></section>")
        return "\n".join(out)

    nav = (
        '<nav><a href="#mismatch">Value mismatches</a> · '
        '<a href="#autofill">Auto-fills</a> · '
        '<a href="#other">Other</a></nav>'
    )
    style = """
    body { font-family: -apple-system, system-ui, sans-serif; max-width: 1400px; margin: 2em auto; padding: 0 1em; color: #1a1a1a; }
    h1 { border-bottom: 2px solid #333; padding-bottom: 0.3em; }
    h2 { margin-top: 2em; }
    nav { background: #f5f5f5; padding: 0.8em; position: sticky; top: 0; z-index: 10; }
    nav a { margin-right: 1em; color: #0366d6; text-decoration: none; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 1em; }
    th, td { text-align: left; padding: 4px 8px; border-bottom: 1px solid #eee; vertical-align: top; }
    th { background: #fafafa; position: sticky; top: 3em; }
    td.m { background: #fff4f4; }
    td.a { background: #f4fff4; }
    td.r { color: #666; font-size: 11px; }
    code { background: #f0f0f0; padding: 1px 4px; border-radius: 2px; font-size: 11px; }
    """
    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CoC Extraction — Reviewer UI</title>
<style>{style}</style>
</head>
<body>
<h1>CoC Data Construction — Reviewer Console</h1>
<p>One-page review of all automation–manual disagreements for FY2024. Pink = manual value; green = extractor proposal. Rows capped at 2,000 per section for browser performance; the full list is in <code>corpus_diffs.csv</code>.</p>
{nav}
{table(mismatches, "True value mismatches (both have values, disagree)", "mismatch")}
{table(autofills, "Manual-blank auto-fills (likely quick backfills after PI spot-check)", "autofill")}
{table(other, "Other (auto blank or extractor skipped)", "other")}
<hr>
<p><small>Generated from corpus_diffs.csv. See <a href="../progress/README.md">progress log</a> for methodology.</small></p>
</body>
</html>
"""
    OUT.write_text(html_out)
    print(f"wrote review UI -> {OUT}  ({len(mismatches)} mismatches, {len(autofills)} autofills, {len(other)} other)")


if __name__ == "__main__":
    main()
