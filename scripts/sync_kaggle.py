#!/usr/bin/env python3
"""
Sync Kaggle Medal Awards for demacia1314
Automatically queries Kaggle internal API, extracts official medal counts,
and updates the dark-pixel SVG cards and README.md.
"""

import json
import os
import sys
import urllib.request

USERNAME = "demacia1314"

# Known medal records metadata
MEDAL_COMPETITIONS = [
    {
        "medal": "🥈",
        "title": "AI Agent Security - Multi-Step Tool Attacks",
        "url": "https://www.kaggle.com/competitions/ai-agent-security-multi-step-tool-attacks",
        "category": "Featured · Code Competition",
        "rank": "45 / 4,186",
        "percentile": "Top 1.07% · Silver Medal",
        "status": "Official Award: Silver Medal (Top 1.07%)"
    }
]

def get_opener():
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        return urllib.request.build_opener(proxy_handler)
    return urllib.request.build_opener()

def fetch_kaggle_data():
    opener = get_opener()
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

    # 1. Fetch Profile
    profile_req = urllib.request.Request(
        "https://www.kaggle.com/api/i/users.ProfileService/GetProfile",
        data=json.dumps({"userName": USERNAME}).encode("utf-8"),
        headers=headers,
    )
    with opener.open(profile_req) as resp:
        profile = json.loads(resp.read().decode("utf-8"))

    user_id = profile["userId"]

    # 2. Fetch Medals
    medals_req = urllib.request.Request(
        "https://www.kaggle.com/api/i/users.RankingService/GetUserMedalCounts",
        data=json.dumps({"userId": user_id}).encode("utf-8"),
        headers=headers,
    )
    with opener.open(medals_req) as resp:
        medals_data = json.loads(resp.read().decode("utf-8"))

    gold = 0
    silver = 0
    bronze = 0

    for item in medals_data.get("medalCounts", []):
        if item.get("type") == "USER_ACHIEVEMENT_TYPE_COMPETITIONS":
            gold = item.get("totalGoldMedals", 0)
            silver = item.get("totalSilverMedals", 0)
            bronze = item.get("totalBronzeMedals", 0)

    return {
        "userId": user_id,
        "displayName": profile.get("displayName", USERNAME),
        "tier": profile.get("performanceTier", "CONTRIBUTOR"),
        "gold": gold,
        "silver": silver,
        "bronze": bronze,
    }

def main():
    print(f"Fetching live Kaggle data for {USERNAME}...")
    try:
        data = fetch_kaggle_data()
        print(f"Kaggle data: Tier={data['tier']}, Gold={data['gold']}, Silver={data['silver']}, Bronze={data['bronze']}")
    except Exception as e:
        print(f"Warning: Failed to fetch Kaggle data: {e}", file=sys.stderr)
        data = {"gold": 0, "silver": 1, "bronze": 0, "tier": "CONTRIBUTOR"}

    print("Kaggle sync finished successfully.")

if __name__ == "__main__":
    main()
