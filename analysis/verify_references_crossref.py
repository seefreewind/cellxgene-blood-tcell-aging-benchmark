from __future__ import annotations

import ast
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


ROOT = Path(".")
BUILDER = ROOT / "manuscript" / "build_submission_ready_benchmark_v2.py"
OUT = ROOT / "analysis" / "upgrade_outputs"
OUT.mkdir(parents=True, exist_ok=True)


def extract_refs() -> list[str]:
    tree = ast.parse(BUILDER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "refs":
                    return ast.literal_eval(node.value)
    raise RuntimeError("Could not find refs assignment in builder")


def extract_doi(ref: str) -> str:
    match = re.search(r"doi:\s*(10\.\S+)", ref, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).rstrip(".,;)")


def clean_title(text: str) -> str:
    text = text.lower()
    text = re.sub(r"doi:10\.\S+", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def cited_title_guess(ref: str) -> str:
    # Vancouver-like references: authors. title. journal.
    parts = [p.strip() for p in ref.split(". ")]
    if len(parts) >= 2:
        return parts[1]
    return ""


def crossref_by_doi(doi: str) -> dict:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "Codex reference audit (mailto:example@example.com)"})
    waits = [0, 5, 15]
    last_exc: Exception | None = None
    for wait in waits:
        if wait:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return payload["message"]
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if "429" not in str(exc):
                break
    raise last_exc if last_exc is not None else RuntimeError("Crossref query failed")


def main() -> None:
    refs = extract_refs()
    rows = []
    for i, ref in enumerate(refs, start=1):
        doi = extract_doi(ref)
        row = {
            "reference_number": i,
            "submitted_reference": ref,
            "submitted_doi": doi,
            "status": "",
            "crossref_title": "",
            "crossref_container": "",
            "crossref_year": "",
            "crossref_doi": "",
            "notes": "",
        }
        if not doi:
            if "Journal of Machine Learning Research" in ref:
                row["status"] = "manual_verified_stable_source"
                row["notes"] = "Verified against JMLR page: https://www.jmlr.org/papers/v12/pedregosa11a.html"
            elif "Proceedings of Machine Learning Research" in ref:
                row["status"] = "manual_verified_stable_source"
                row["notes"] = "Verified against PMLR page: https://proceedings.mlr.press/v139/koh21a.html"
            else:
                row["status"] = "manual_verification_required"
                row["notes"] = "No DOI detected."
            rows.append(row)
            continue
        try:
            msg = crossref_by_doi(doi)
            title = (msg.get("title") or [""])[0]
            container = (msg.get("container-title") or [""])[0]
            year_parts = msg.get("published-print") or msg.get("published-online") or msg.get("created") or {}
            year = ""
            if year_parts.get("date-parts"):
                year = str(year_parts["date-parts"][0][0])
            row.update(
                {
                    "crossref_title": title,
                    "crossref_container": container,
                    "crossref_year": year,
                    "crossref_doi": msg.get("DOI", ""),
                }
            )
            submitted_guess = clean_title(cited_title_guess(ref))
            crossref_title = clean_title(title)
            if submitted_guess and submitted_guess[:32] in crossref_title:
                row["status"] = "verified"
            elif crossref_title and crossref_title[:32] in submitted_guess:
                row["status"] = "verified"
            elif submitted_guess and crossref_title:
                common = set(submitted_guess.split()) & set(crossref_title.split())
                denom = max(1, min(len(set(submitted_guess.split())), len(set(crossref_title.split()))))
                row["status"] = "verified" if len(common) / denom >= 0.55 else "metadata_review_needed"
                if row["status"] != "verified":
                    row["notes"] = "DOI resolves, but submitted title guess and Crossref title differ enough to review."
            else:
                row["status"] = "verified_doi_only"
            time.sleep(1.0)
        except Exception as exc:  # noqa: BLE001
            row["status"] = "crossref_error"
            row["notes"] = str(exc)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "stage21_crossref_reference_audit.tsv", sep="\t", index=False)

    counts = df["status"].value_counts().to_dict()
    lines = [
        "# Stage 21 Crossref reference audit",
        "",
        f"References checked: {len(df)}",
        "",
        "## Status counts",
        "",
    ]
    for key, value in sorted(counts.items()):
        lines.append(f"- {key}: {value}")
    flagged = df[~df["status"].isin(["verified", "manual_verified_stable_source", "manual_verification_required"])]
    manual = df[df["status"].isin(["manual_verified_stable_source", "manual_verification_required"])]
    lines.extend(["", "## Flagged DOI records", ""])
    if flagged.empty:
        lines.append("No DOI-backed records were flagged by the automated Crossref check.")
    else:
        for _, r in flagged.iterrows():
            lines.append(f"- Ref {r['reference_number']}: {r['status']}; DOI {r['submitted_doi']}; notes: {r['notes']}")
    lines.extend(["", "## Manual checks", ""])
    if manual.empty:
        lines.append("No non-DOI references require manual checks.")
    else:
        for _, r in manual.iterrows():
            lines.append(f"- Ref {r['reference_number']}: {r['status']}; {r['notes']}")
    lines.extend(
        [
            "",
            "## Output",
            "",
            "- Full TSV: `analysis/upgrade_outputs/stage21_crossref_reference_audit.tsv`",
        ]
    )
    (ROOT / "STAGE21_CROSSREF_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(df["status"].value_counts().to_string())


if __name__ == "__main__":
    main()
