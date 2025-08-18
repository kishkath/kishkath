import os
import requests
from datetime import datetime
from collections import defaultdict

TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("USERNAME")

GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# GraphQL query for contributions
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
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

response = requests.post(GRAPHQL_URL, json={"query": QUERY, "variables": {"login": USERNAME}}, headers=HEADERS)
data = response.json()

contributions = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
six_month_commits = defaultdict(int)
total_commits = 0

for week in contributions:
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        year = date.year
        month = date.month
        period = "Jan–Jun" if month <= 6 else "Jul–Dec"
        key = (year, period)
        count = day["contributionCount"]
        six_month_commits[key] += count
        total_commits += count

# Sort by year (desc), then period (Jul–Dec first)
sorted_keys = sorted(six_month_commits.keys(), key=lambda x: (x[0], x[1] == "Jan–Jun"), reverse=True)

# Build table
table = "| Year | Period    | Commits |\n|------|-----------|---------|\n"
for year, period in sorted_keys:
    table += f"| {year} | {period} | {six_month_commits[(year, period)]} |\n"

# Update README
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

start_table = "<!--START_SECTION:commits_table-->"
end_table = "<!--END_SECTION:commits_table-->"
new_readme = readme.split(start_table)[0] + start_table + "\n" + table + end_table + readme.split(end_table)[1]

# Update total commits badge
import re
badge_pattern = r"!\[Total Commits\]\(https:\/\/img\.shields\.io\/badge\/Total%20Commits-[^\)]+\)"
badge_replacement = f"![Total Commits](https://img.shields.io/badge/Total%20Commits-{total_commits}-blue)"
new_readme = re.sub(badge_pattern, badge_replacement, new_readme)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)
