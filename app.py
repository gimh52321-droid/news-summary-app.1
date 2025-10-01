from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup

app = Flask(__name__)

# 연합뉴스 RSS 링크 (스포츠, 경제, 사회 예시)
rss_urls = {
    "스포츠": "https://www.yna.co.kr/rss/sports.xml",
    "경제": "https://www.yna.co.kr/rss/economy.xml",
    "사회": "https://www.yna.co.kr/rss/society.xml"
}

html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>연합뉴스 뉴스</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }
        h1 { text-align: center; }
        .news { background: white; padding: 15px; margin: 10px; border-radius: 10px; box-shadow: 0 0 5px #aaa; }
        .news h2 { font-size: 20px; margin: 0; }
        .news p { font-size: 14px; color: #333; }
    </style>
</head>
<body>
    <h1>연합뉴스 최신 뉴스</h1>
    {% for category, articles in news_data.items() %}
        <h2>{{ category }}</h2>
        {% for article in articles %}
            <div class="news">
                <h2><a href="{{ article['link'] }}" target="_blank">{{ article['title'] }}</a></h2>
                <p>{{ article['summary'] }}</p>
            </div>
        {% endfor %}
    {% endfor %}
</body>
</html>
"""

@app.route("/")
def index():
    news_data = {}
    for category, url in rss_urls.items():
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:5]:  # 각 카테고리 5개 기사만
            summary = BeautifulSoup(entry.summary, "html.parser").get_text()
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary
            })
        news_data[category] = articles
    return render_template_string(html_template, news_data=news_data)

if __name__ == "__main__":
    app.run(debug=True)
