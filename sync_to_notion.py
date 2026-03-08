import requests
import os
import datetime
import re

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def translate(text):
    if not text:
        return ""

    r = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={
            "client": "gtx",
            "sl": "en",
            "tl": "zh",
            "dt": "t",
            "q": text
        }
    )

    try:
        return r.json()[0][0][0]
    except:
        return text

def send_to_notion(title, intro, link, source):

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "name": {
                "title": [{"text": {"content": title}}]
            },
            "link": {
                "url": link
            },
            "introduction": {
                "rich_text": [{"text": {"content": intro}}]
            },
            "source": {
                "select": {"name": source}
            },
            "date": {
                "date": {"start": datetime.date.today().isoformat()}
            }
        }
    }

    requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload
    )

print("Fetching GitHub Trending...")

html = requests.get(
    "https://github.com/trending?since=daily"
).text

repos = re.findall(
    r'href="/(.*?)"',
    html
)

seen = set()
count = 0

for r in repos:

    if "/" in r and r.count("/") == 1:

        if r in seen:
            continue

        seen.add(r)

        url = f"https://github.com/{r}"

        api = requests.get(
            f"https://api.github.com/repos/{r}"
        ).json()

        name = api.get("name")
        desc = api.get("description", "")

        intro = translate(desc)

        send_to_notion(
            name,
            intro,
            url,
            "GitHub"
        )

        count += 1
        if count >= 5:
            break

print("Fetching Hacker News...")

ids = requests.get(
    "https://hacker-news.firebaseio.com/v0/topstories.json"
).json()[:5]

for i in ids:

    item = requests.get(
        f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
    ).json()

    title = item.get("title")

    link = item.get(
        "url",
        f"https://news.ycombinator.com/item?id={i}"
    )

    intro = translate(title)

    send_to_notion(
        title,
        intro,
        link,
        "HackerNews"
    )

print("Fetching arXiv AI papers...")

rss = requests.get(
    "https://export.arxiv.org/rss/cs.AI"
).text

items = rss.split("<item>")[1:6]

for i in items:

    title = i.split("<title>")[1].split("</title>")[0]
    link = i.split("<link>")[1].split("</link>")[0]

    intro = translate(title)

    send_to_notion(
        title,
        intro,
        link,
        "arXiv"
    )

print("Done.")
