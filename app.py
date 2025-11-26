from flask import Flask, render_template, request, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = "secret_key_example"

# ✔ 카테고리 3개만 유지
news_urls = {
    "사회": "https://news.naver.com/section/102",
    "경제": "https://news.naver.com/section/101",
    "세계": "https://news.naver.com/section/104"
}

# ✔ 핵심 내용 기반 요약 (400~500자)
def smart_summary(text, min_len=400, max_len=500):
    text = re.sub(r"\s+", " ", text)

    keywords = [
        "경제", "시장", "정부", "정책", "분석", "전망",
        "사건", "사고", "국제", "전쟁", "기술", "위기",
        "인플레이션", "금리", "사회", "이슈"
    ]

    parts = text.split(".")
    selected = []

    for p in parts:
        if any(k in p for k in keywords):
            selected.append(p.strip())

    summary = ". ".join(selected)

    # 너무 짧으면 원문 일부 사용
    if len(summary) < min_len:  
        summary = text[:max_len]

    # 정확히 500자 제한
    return summary[:max_len] + "..."

# ✔ 뉴스 10개로 제한
def get_news(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    news_items = []
    number = 1

    for item in soup.select("div.sa_item_inner")[:10]:
        title_tag = item.select_one("a.sa_text_title")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag["href"]
        summary_tag = item.select_one(".sa_text_lede")
        raw_summary = summary_tag.get_text(strip=True) if summary_tag else title

        summary = smart_summary(raw_summary)

        news_items.append({
            "id": number,
            "title": title,
            "link": link,
            "summary": summary
        })
        number += 1

    return news_items


@app.route("/", methods=["GET"])
def index():
    # 카테고리별 뉴스 수집
    news_data = {cat: get_news(url) for cat, url in news_urls.items()}

    # 검색 기능
    query = request.args.get("query", "")
    filtered_news = []

    if query:
        for cat, articles in news_data.items():
            for n in articles:
                if query.lower() in n["title"].lower() or query.lower() in n["summary"].lower():
                    filtered_news.append(n)

    favorites = session.get("favorites", [])

    return render_template(
        "index.html",
        news_data=news_data,
        filtered_news=filtered_news,
        query=query,
        favorites=favorites
    )

@app.route("/favorite/<string:title>")
def add_favorite(title):
    favorites = session.get("favorites", [])
    if title not in favorites:
        favorites.append(title)
    session["favorites"] = favorites
    return redirect(url_for("index"))

@app.route("/unfavorite/<string:title>")
def remove_favorite(title):
    favorites = session.get("favorites", [])
    if title in favorites:
        favorites.remove(title)
    session["favorites"] = favorites
    return redirect(url_for("index"))

@app.route("/favorites")
def show_favorites():
    favorites = session.get("favorites", [])
    return render_template("favorites.html", favorites=favorites)

if __name__ == "__main__":
    app.run(debug=True)
