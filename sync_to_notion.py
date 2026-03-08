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

    try:
        r = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client": "gtx",
                "sl": "en",
                "tl": "zh",
                "dt": "t",
                "q": text
            },
            timeout=10
        )

        return r.json()[0][0][0]

    except:
        return text

def send_to_notion(title, intro, link):

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "name": {
                "title": [
                    {"text": {"content": title}}
                ]
            },
            "link": {
                "url": link
            },
            "introduction": {
                "rich_text": [
                    {"text": {"content": intro}}
                ]
            },
            "date": {
                "date": {
                    "start": datetime.date.today().isoformat()
                }
            }
        }
    }

    requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload
    )

print("Fetching GitHub Trending...")

try:

    html = requests.get(
        "https://github.com/trending?since=daily",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    ).text

    repos = re.findall(
        r'/([\w\-]+/[\w\-]+)"',
        html
    )

    seen = set()
    count = 0

    for repo in repos:

        if repo in seen:
            continue

        seen.add(repo)

        try:

            api = requests.get(
                f"https://api.github.com/repos/{repo}",
                timeout=10
            ).json()

            name = api.get("name")
            desc = api.get("description") or ""

            if not name:
                continue

            intro = translate(desc)

            send_to_notion(
                f"[GitHub] {name}",
                intro,
                f"https://github.com/{repo}"
            )

            count += 1

            if count >= 5:
                break

        except:
            continue

except:
    print("GitHub fetch failed")

print("Fetching Hacker News...")

try:

    ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        timeout=10
    ).json()[:5]

    for i in ids:

        try:

            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{i}.json",
                timeout=10
            ).json()

            title = item.get("title")

            link = item.get(
                "url",
                f"https://news.ycombinator.com/item?id={i}"
            )

            intro = translate(title)

            send_to_notion(
                f"[HN] {title}",
                intro,
                link
            )

        except:
            continue

except:
    print("HN fetch failed")

print("Fetching arXiv papers...")

try:

    rss = requests.get(
        "https://export.arxiv.org/rss/cs.AI",
        timeout=10
    ).text

    items = rss.split("<item>")[1:6]

    for item in items:

        try:

            title = item.split("<title>")[1].split("</title>")[0]
            link = item.split("<link>")[1].split("</link>")[0]

            intro = translate(title)

            send_to_notion(
                f"[arXiv] {title}",
                intro,
                link
            )

        except:
            continue

except:
    print("arXiv fetch failed")

print("Done.")
