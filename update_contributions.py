import json
import os
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

USERNAME = "Nishit-soni-01"
TOKEN = os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    raise SystemExit("GITHUB_TOKEN is missing.")

today = datetime.now(timezone.utc).date()
start = today - timedelta(days=364)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": f"{start.isoformat()}T00:00:00Z",
        "to": f"{today.isoformat()}T23:59:59Z"
    }
}

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": USERNAME
    },
    method="POST"
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

if result.get("errors"):
    raise SystemExit(f"GitHub API error: {result['errors']}")

user = result.get("data", {}).get("user")
if not user:
    raise SystemExit(f"GitHub user not found: {USERNAME}")

calendar = user["contributionsCollection"]["contributionCalendar"]

days = [
    {
        "date": day["date"],
        "count": day["contributionCount"]
    }
    for week in calendar["weeks"]
    for day in week["contributionDays"]
]

# Keep the most recent 365 days.
days = [day for day in days if start.isoformat() <= day["date"] <= today.isoformat()]

# Calculate the current streak. If today has no contributions yet,
# count the streak ending yesterday.
streak_days = days[:]
if streak_days and streak_days[-1]["date"] == today.isoformat() and streak_days[-1]["count"] == 0:
    streak_days.pop()

streak = 0
for day in reversed(streak_days):
    if day["count"] > 0:
        streak += 1
    else:
        break

active_days = sum(1 for day in days if day["count"] > 0)

weekday_totals = Counter()
monthly_totals = Counter()

for day in days:
    day_date = date.fromisoformat(day["date"])
    weekday_totals[day_date.strftime("%A")] += day["count"]
    monthly_totals[day_date.strftime("%Y-%m")] += day["count"]

months = []
current_month = today.year * 12 + today.month - 1

for offset in range(11, -1, -1):
    year, month_index = divmod(current_month - offset, 12)
    month = month_index + 1
    key = f"{year}-{month:02d}"

    months.append({
        "label": date(year, month, 1).strftime("%b"),
        "total": monthly_totals.get(key, 0)
    })

busiest_day = (
    max(weekday_totals, key=weekday_totals.get)
    if weekday_totals and max(weekday_totals.values()) > 0
    else "—"
)

data = {
    "total_contributions": calendar["totalContributions"],
    "streak": streak,
    "active_days": active_days,
    "busiest_day": busiest_day,
    "months": months,
    "calendar": days
}

Path("contributions.json").write_text(
    json.dumps(data, indent=2),
    encoding="utf-8"
)

print(
    f"Updated contributions.json: "
    f"{data['total_contributions']} contributions, "
    f"{active_days} active days, {streak}-day streak."
)