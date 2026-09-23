#!/usr/bin/env python3
"""
Sync Kaggle medal data for demacia1314.

Queries the Kaggle public JSON API for live competition stats and rewrites the
dynamic numbers in assets/*.svg and README.md.

Medals are read from users.ProfileService/GetProfile, which returns
achievementSummaries with totalSilverMedals / totalBronzeMedals and the
competition ranking. Verified against
users.RankingService/GetUserMedalCounts, which serves the same counts.

Attribution of each medal to a specific competition is NOT available from the
public API -- the per-competition participation list is gated. The
SILVER_COMPETITION constant below stays hand-maintained until that changes.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

USERNAME = "demacia1314"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hand-maintained: the API exposes medal COUNTS, not which competition earned them.
SILVER_COMPETITION = {
    "name": "AI Agent Security - Multi-Step Tool Attacks",
    "slug": "ai-agent-security-multi-step-tool-attacks",
    "category": "Featured · Code Competition",
    "teams": 4186,
    "rank": 45,
    "percentile": "Top 1.07%",
}


def _opener():
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    return urllib.request.build_opener()


def _post(opener, service, payload):
    req = urllib.request.Request(
        "https://www.kaggle.com/api/i/" + service,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with opener.open(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_kaggle_data():
    opener = _opener()
    profile = _post(opener, "users.ProfileService/GetProfile", {"userName": USERNAME})

    comp = next(
        (
            s
            for s in profile.get("achievementSummaries", [])
            if s.get("summaryType") == "USER_ACHIEVEMENT_TYPE_COMPETITIONS"
        ),
        {},
    )
    return {
        "userName": profile.get("userName", USERNAME),
        "displayName": profile.get("displayName", USERNAME),
        "tier": profile.get("performanceTier", "CONTRIBUTOR"),
        "gold": comp.get("totalGoldMedals", 0),
        "silver": comp.get("totalSilverMedals", 0),
        "bronze": comp.get("totalBronzeMedals", 0),
        "rank": comp.get("rankCurrent"),
        "rankOutOf": comp.get("rankOutOf"),
        "rankPercent": comp.get("rankPercentage"),
        "competitions": profile.get("totalCompetitions", 0),
    }


def _fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


def update_svg(rel_path, replacements, data):
    """Apply literal string replacements, then verify the file changed."""
    path = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(path):
        print(f"  skip (missing): {rel_path}")
        return False
    with open(path, encoding="utf-8") as fh:
        original = fh.read()

    text = original
    for pattern, template in replacements:
        text = re.sub(pattern, lambda m, t=template: t.format(**data), text)

    if text == original:
        print(f"  unchanged: {rel_path}")
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(f"  updated:   {rel_path}")
    return True


def main():
    print(f"Fetching live Kaggle data for {USERNAME}...")
    try:
        data = fetch_kaggle_data()
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"ERROR: Kaggle fetch failed: {exc}", file=sys.stderr)
        return 1

    data["percentile"] = (
        f"Top {data['rankPercent'] * 100:.2f}%" if data.get("rankPercent") else "—"
    )
    data["percentile_upper"] = data["percentile"].upper()

    print(
        "Kaggle: tier={tier} gold={gold} silver={silver} bronze={bronze} "
        "rank={rank}/{rankOutOf} competitions={competitions}".format(**data)
    )

    tallies = {
        "gold": data["gold"],
        "silver": data["silver"],
        "bronze": data["bronze"],
        "rank": _fmt(data["rank"]),
        "rank_out_of": _fmt(data["rankOutOf"]),
        "percentile": data["percentile"],
        "percentile_upper": data["percentile_upper"],
        "tier": data["tier"],
        "silver_medal": data["silver"],
    }

    print("Rewriting assets...")
    changed = False

    changed |= update_svg(
        "assets/kaggle-badge.svg",
        [
            (r"(?<=· )\d+ SILVER · \d+ BRONZE", "{silver_medal} SILVER · {bronze} BRONZE"),
            (
                r"COMPETITIONS RANK [\d,]+ / [\d,]+ · (?:TOP|Top) [\d.]+%",
                "COMPETITIONS RANK {rank} / {rank_out_of} · {percentile_upper}",
            ),
        ],
        tallies,
    )

    changed |= update_svg(
        "assets/terminal-header.svg",
        [
            (r"EXPERT · \d+ MEDALS", "{tier} · {medal_total} MEDALS"),
        ],
        {**tallies, "medal_total": data["gold"] + data["silver"] + data["bronze"]},
    )

    changed |= update_svg(
        "assets/kaggle-card.svg",
        [
            (r"\[GOLD: \d+\]", "[GOLD: {gold}]"),
            (r"\[SILVER: \d+\]", "[SILVER: {silver}]"),
            (r"\[BRONZE: \d+\]", "[BRONZE: {bronze}]"),
        ],
        tallies,
    )

    print("Sync finished." + ("" if changed else " Nothing to commit."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
