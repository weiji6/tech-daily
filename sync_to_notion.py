import requests
import os
import datetime

token = os.environ["NOTION_TOKEN"]
db = os.environ["DATABASE_ID"]

url = "https://api.github.com/search/repositories?q=stars:>10000&sort=stars&order=desc&per_page=5"
data = requests.get(url).json()

def translate(text):
    if not text:
        return ""
    r = requests.post(
        "https://libretranslate.de/translate",
        json={
            "q": text,
            "source": "en",
            "target": "zh"
        }
    )
    return r.json()["translatedText"]

for repo in data["items"]:

    description = repo["description"] or ""
    chinese_intro = translate(description)

    payload = {
        "parent": {"database_id": db},
        "properties": {
            "name": {
                "title": [{"text": {"content": repo["name"]}}]
            },
            "link": {
                "url": repo["html_url"]
            },
            "star": {
                "number": repo["stargazers_count"]
            },
            "introduction": {
                "rich_text": [{"text": {"content": chinese_intro}}]
            },
            "date": {
                "date": {"start": datetime.date.today().isoformat()}
            }
        }
    }

    requests.post(
        "https://api.notion.com/v1/pages",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        },
        json=payload
    )
