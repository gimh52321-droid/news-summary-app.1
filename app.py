from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
app.secret_key = "secret_key_example"

# -------------------------
# 뉴스 카테고리 URL
# -------------------------
news_urls = {
    "경제": "https://news.naver.com/section/101",
    "사회": "https://news.naver.com/section/102",
    "세계": "https://news.naver.com/section/104"
}

# -------------------------
# 주제별 단어 사전
# -------------------------
predefined_words = {
    "경제": {
        "인플레이션": "화폐 가치 하락으로 인해 물가가 전반적으로 상승하는 현상",
        "금리": "돈을 빌릴 때 적용되는 이자율",
        "환율": "두 나라 통화의 교환 비율",
        "증시": "주식 시장",
        "채권": "정부나 기업이 발행하는 빚 문서",
        "경기부양": "경제를 활성화시키기 위한 정책",
        "재정정책": "정부가 세금과 지출로 경제를 조절하는 정책",
        "통화정책": "중앙은행이 금리와 화폐 공급을 조절하는 정책",
        "부동산": "토지나 건물 등 고정 자산",
        "시장점유율": "한 기업이 시장에서 차지하는 비율",
        "자산": "가치가 있는 재산",
        "적자": "수입보다 지출이 더 많은 상태",
        "흑자": "수입이 지출보다 많은 상태",
        "투자": "수익을 목적으로 자본을 투입하는 행위",
        "파산": "경제적 지급 불능 상태",
        "디플레이션": "전반적인 물가가 하락하는 현상",
        "벤처": "새로운 사업 아이디어를 가진 신생 기업",
        "주식배당": "주식 소유자에게 이익의 일부를 분배하는 것"
    },
    "사회": {
        "복지": "국가가 국민의 생활 안정을 위해 지원하는 정책",
        "청년실업": "청년층의 일자리 부족 현상",
        "노동시장": "노동력이 거래되는 시장",
        "고령화": "인구에서 노인 비율이 증가하는 현상",
        "범죄율": "범죄 발생 비율",
        "재난": "자연재해나 사고로 인한 피해",
        "정책": "정부가 추진하는 계획이나 법률",
        "시민권": "국가가 국민에게 부여하는 권리",
        "환경오염": "자연 환경이 오염되는 현상",
        "교육격차": "학생 간 학습 기회와 성취 차이",
        "복지사각지대": "복지 혜택이 미치지 않는 영역",
        "인권": "개인에게 보장된 기본적인 권리",
        "사회적기업": "사회적 목적을 가진 기업",
        "재난구호": "재난 발생 시 지원 활동",
        "노동조합": "노동자 권익을 보호하기 위한 조직",
        "젠더": "사회적 성 역할 및 성차 문제",
        "청소년보호": "청소년의 권리와 안전을 보호하는 정책"
    },
    "세계": {
        "국제기구": "국가 간 협력을 위해 설립된 기구",
        "분쟁": "두 국가 또는 집단 간 갈등",
        "전쟁": "무력 충돌",
        "평화협정": "전쟁을 끝내기 위한 합의",
        "인권침해": "사람의 권리가 침해되는 행위",
        "난민": "자국을 떠나 다른 나라로 피신한 사람",
        "경제제재": "국제적으로 가하는 경제적 제한",
        "외교": "국가 간 관계를 관리하는 활동",
        "국제법": "국제 사회에서 인정되는 법",
        "무역분쟁": "국가 간 무역 갈등",
        "기후변화": "지구 기후의 장기적 변화",
        "환경보호": "자연과 환경을 지키는 활동",
        "테러": "공포를 조장하는 폭력 행위",
        "유엔": "국제 연합",
        "글로벌화": "세계가 경제, 문화, 정치적으로 연결되는 현상",
        "브렉시트": "영국의 EU 탈퇴",
        "난민협약": "난민 보호를 위한 국제 조약"
    },
    "IT": {
        "클라우드": "인터넷 기반으로 제공되는 컴퓨팅 서비스",
        "빅데이터": "대규모 데이터 분석 기술",
        "인공지능": "사람처럼 학습, 추론, 판단하는 기술",
        "머신러닝": "기계가 학습하도록 하는 기술",
        "딥러닝": "인공신경망 기반의 학습 기술",
        "블록체인": "분산형 거래 기록 기술",
        "가상화폐": "디지털 형태의 화폐",
        "사이버보안": "인터넷 및 시스템 보호 기술",
        "IoT": "사물인터넷",
        "알고리즘": "문제를 해결하기 위한 단계적 절차",
        "데이터마이닝": "데이터에서 의미 있는 정보를 추출하는 기술",
        "API": "소프트웨어 기능을 연결하는 인터페이스",
        "프로그래밍": "컴퓨터 프로그램 작성 활동",
        "네트워크": "컴퓨터 간 연결망",
        "클라이언트": "서비스를 받는 측 시스템",
        "서버": "서비스를 제공하는 측 시스템"
    },
    "정치": {
        "민주주의": "국민이 주권을 가지고 정치에 참여하는 제도",
        "선거": "국민이 대표자를 뽑는 과정",
        "정당": "공통의 정치 목적을 가진 조직",
        "권력분립": "국가 권력을 나누어 견제하는 제도",
        "헌법": "국가의 기본 법",
        "법률": "국민의 권리와 의무를 규정한 규범",
        "국회의원": "국회를 구성하는 대표",
        "행정": "국가 정책 집행 활동",
        "사법": "법을 해석하고 적용하는 권한",
        "투표": "의견을 표시하여 선출하는 행위",
        "정책결정": "정책을 만들고 집행하는 과정",
        "외교정책": "국가 간 관계를 관리하는 정책",
        "선거법": "선거 관련 법률",
        "정치자금": "정치 활동에 사용되는 자금",
        "국방": "국가를 보호하기 위한 군사 활동"
    },
    "생활문화": {
        "트렌드": "사회 전반에 유행하는 경향",
        "문화재": "역사적 가치가 있는 유산",
        "생활용품": "일상에서 사용하는 물품",
        "건강관리": "몸과 마음을 돌보는 활동",
        "식문화": "음식과 관련된 문화",
        "여행지": "관광할 만한 장소",
        "취미": "여가 활동과 관심사",
        "패션": "의복과 스타일 문화",
        "뷰티": "외모와 관련된 관리",
        "요리": "음식을 만드는 활동",
        "전통문화": "오래전부터 전해 내려오는 문화",
        "예술": "인간의 창작 활동과 작품",
        "공연": "음악, 연극 등 공연 활동",
        "축제": "지역 또는 국가 단위 행사",
        "생활정보": "일상 생활에 필요한 정보"
    }
}

# -------------------------
# 기사 본문 가져오기
# -------------------------
def get_article_text(url):
    try:
        res = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        soup = BeautifulSoup(res.text, "html.parser")
        content = soup.select_one("#dic_area") or soup.select_one("div#articleBodyContents") or soup.select_one("div.news_end")
        if not content:
            return soup.get_text(separator=" ", strip=True)
        text = content.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text)
    except Exception:
        return "본문을 불러올 수 없습니다."

# -------------------------
# 뉴스 요약 400~600자
# -------------------------
def smart_summary(text, min_len=400, max_len=600):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    sentences = re.split(r'(?<=[.?!])\s+', text)
    selected = []
    for s in sentences:
        selected.append(s.strip())
        if len(" ".join(selected)) >= min_len:
            break
    summary = " ".join(selected)
    summary = summary[:max_len]
    if not summary.endswith((".", "!", "?")):
        summary += "."
    return summary

# -------------------------
# 뉴스 목록 가져오기
# -------------------------
def get_news(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
    except Exception:
        return []

    news_items = []
    candidates = soup.select("div.sa_item_inner") or soup.select("ul.list_news li")

    for i, item in enumerate(candidates[:10]):
        title_tag = item.select_one("a.sa_text_title") or item.select_one("a")
        if not title_tag:
            continue
        link = title_tag.get("href")
        if not link:
            continue

        full_text = get_article_text(link)
        news_items.append({
            "id": i + 1,
            "title": title_tag.get_text(strip=True),
            "link": link,
            "summary": smart_summary(full_text),
            "content": full_text
        })
    return news_items

# -------------------------
# 메인 페이지
# -------------------------
@app.route("/")
def index():
    query = request.args.get("query", "").strip()
    news_data = {}

    for cat, url in news_urls.items():
        articles = get_news(url)
        if query:
            articles = [a for a in articles if query in a["title"] or query in a["content"]]
        news_data[cat] = articles

    return render_template(
        "index.html",
        news_data=news_data,
        favorites=session.get("favorites", []),
        wordbook=session.get("wordbook", []),
        query=query
    )

# -------------------------
# 단어 뜻 조회
# -------------------------
@app.route("/api/define")
def define_word():
    word = request.args.get("word", "").strip()
    meanings = []
    for words in predefined_words.values():
        if word in words:
            meanings.append(words[word])
    return jsonify({"meanings": meanings or ["뜻을 찾을 수 없습니다."]})

# -------------------------
# 단어장 관리
# -------------------------
@app.route("/add_word", methods=["POST"])
def add_word():
    data = request.get_json() or {}
    word = data.get("word", "").strip()
    meanings = data.get("meanings", [])
    wb = session.get("wordbook", [])
    wb = [w for w in wb if w["word"] != word]
    wb.insert(0, {"word": word, "meanings": meanings})
    session["wordbook"] = wb[:20]
    return jsonify(success=True)

@app.route("/wordbook")
def wordbook_page():
    return render_template("wordbook.html", wordbook=session.get("wordbook", []))

@app.route("/delete_word", methods=["POST"])
def delete_word():
    data = request.get_json() or {}
    word = data.get("word")
    session["wordbook"] = [w for w in session.get("wordbook", []) if w["word"] != word]
    return jsonify(success=True)

# -------------------------
# 즐겨찾기
# -------------------------
@app.route("/favorite/<path:title>")
def add_favorite(title):
    fav = session.get("favorites", [])
    if title not in fav:
        fav.append(title)
    session["favorites"] = fav
    return redirect(url_for("index"))

@app.route("/unfavorite/<path:title>")
def remove_favorite(title):
    fav = session.get("favorites", [])
    if title in fav:
        fav.remove(title)
    session["favorites"] = fav
    return redirect(url_for("index"))

@app.route("/favorites")
def show_favorites():
    return render_template("favorites.html", favorites=session.get("favorites", []))

# -------------------------
# 실행 (Render 대응)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
