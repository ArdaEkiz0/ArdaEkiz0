"""Top-languages terminal bar. Pulls public repo language bytes via `gh api`
(works in Actions with GITHUB_TOKEN), writes data/langs.json, and refreshes
the README block between <!-- langs:start --> markers. No external service.
"""
import json
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(BASE, "data", "langs.json")
README = os.path.join(BASE, "README.md")
START, END = "<!-- langs:start -->", "<!-- langs:end -->"
CELLS = 20


def gh(*args):
    return subprocess.run(
        ["gh", "api", *args], capture_output=True, text=True, check=True
    ).stdout


def gh_json(*args):
    return json.loads(gh(*args))


def main() -> None:
    user = os.environ.get("GITHUB_USER", "ArdaEkiz0")
    repos = gh(f"users/{user}/repos", "--paginate", "--jq",
               ".[] | select(.fork == false) | .name").split()
    totals: dict[str, int] = {}
    for r in repos:
        for lang, n in gh_json(f"repos/{user}/{r}/languages").items():
            totals[lang] = totals.get(lang, 0) + n
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])
    top, rest = ranked[:3], ranked[3:]
    rows = [(lang, n / grand) for lang, n in top]
    if rest:
        rows.append(("Other", sum(n for _, n in rest) / grand))

    lines = ["arda@github ~ $ lang --top"]
    for lang, frac in rows:
        filled = max(round(frac * CELLS), 1) if frac > 0 else 0
        bar = "█" * filled + "░" * (CELLS - filled)
        lines.append(f"{lang:<12} {bar}  {frac * 100:3.0f}%")
    block = "\n".join(lines)

    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    json.dump({"user": user, "langs": totals}, open(DATA, "w", encoding="utf-8"), indent=2)

    md = open(README, encoding="utf-8").read()
    assert START in md and END in md, "lang markers missing in README"
    pre, _, rest_md = md.partition(START)
    _, _, post = rest_md.partition(END)
    open(README, "w", encoding="utf-8", newline="\n").write(
        f"{pre}{START}\n```console\n{block}\n```\n{END}{post}")
    print(block)


if __name__ == "__main__":
    main()
