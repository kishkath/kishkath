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
monthly_commits = defaultdict(int)
total_commits = 0

for week in contributions:
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        month_key = date.strftime("%Y-%m")
        count = day["contributionCount"]
        monthly_commits[month_key] += count
        total_commits += count

quarters = {"01": "Q1", "02": "Q1", "03": "Q1",
            "04": "Q2", "05": "Q2", "06": "Q2",
            "07": "Q3", "08": "Q3", "09": "Q3",
            "10": "Q4", "11": "Q4", "12": "Q4"}

# Build commit table
table = "| Year | Quarter | Month | Commits |\n|------|---------|--------|---------|\n"
for year_month in sorted(monthly_commits.keys(), reverse=True):
    year, month = year_month.split("-")
    q = quarters[month]
    month_name = datetime.strptime(month, "%m").strftime("%B")
    commits = monthly_commits[year_month]
    table += f"| {year} | {q} | {month_name} | {commits} |\n"

# Update README
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

# Update commits table
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
