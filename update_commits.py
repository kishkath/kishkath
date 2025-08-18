import os
import requests
from datetime import datetime
from collections import defaultdict

TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("USERNAME")

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

# Make request
headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.post(
    "https://api.github.com/graphql",
    json={"query": QUERY, "variables": {"login": USERNAME}},
    headers=headers
)
data = response.json()

# Extract contributions
contributions = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
monthly_commits = defaultdict(int)

for week in contributions:
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d")
        month_key = date.strftime("%Y-%m")
        monthly_commits[month_key] += day["contributionCount"]

# Build Year -> Quarter -> Month table
quarters = {"01": "Q1", "02": "Q1", "03": "Q1",
            "04": "Q2", "05": "Q2", "06": "Q2",
            "07": "Q3", "08": "Q3", "09": "Q3",
            "10": "Q4", "11": "Q4", "12": "Q4"}

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

start = "<!--START_SECTION:commits_table-->"
end = "<!--END_SECTION:commits_table-->"
new_readme = readme.split(start)[0] + start + "\n" + table + end + readme.split(end)[1]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)
