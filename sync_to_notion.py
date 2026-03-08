import requests
import os
import datetime

token = os.environ["NOTION_TOKEN"]
db = os.environ["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {token}",
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
    return r.json()[0][0][0]


def send_to_notion(title, intro, link, star=0):
    payload = {
        "parent": {"database_id": db},
        "properties": {
            "name": {
                "title": [{"text": {"content": title}}]
            },
            "link": {
                "url": link
            },
            "star": {
                "number": star
            },
            "introduction": {
                "rich_text": [{"text": {"content": intro}}]
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

gh = requests.get(
    "https://api.github.com/search/repositories?q=stars:>10000&sort=stars&order=desc&per_page=5"
).json()

for repo in gh["items"]:
    intro = translate(repo["description"] or "")
    send_to_notion(
        repo["name"],
        intro,
        repo["html_url"],
        repo["stargazers_count"]
    )

hn_ids = requests.get(
    "https://hacker-news.firebaseio.com/v0/topstories.json"
).json()[:5]

for i in hn_ids:
    item = requests.get(
        f"https://hacker-news.firebaseio.com/v0/item/{i}.json"
    ).json()

    title = item.get("title")
    link = item.get("url", f"https://news.ycombinator.com/item?id={i}")

    intro = translate(title)

    send_to_notion(
        f"HN: {title}",
        intro,
        link
    )

rss = requests.get("https://export.arxiv.org/rss/cs.AI").text

entries = rss.split("<item>")[1:6]

for e in entries:
    title = e.split("<title>")[1].split("</title>")[0]
    link = e.split("<link>")[1].split("</link>")[0]

    intro = translate(title)

    send_to_notion(
        f"arXiv: {title}",
        intro,
        link
    )
