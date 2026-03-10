import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# -----------------------------------
# Selenium Driver 설정
# -----------------------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# -----------------------------------
# 순위 추출 (2~50위용)
# -----------------------------------
def extract_rank(item):
    # 2~50위 숫자 span
    span_rank = item.select_one("span.fz-12")
    if span_rank:
        txt = span_rank.get_text(strip=True)
        if txt.isdigit():
            return int(txt)
    return None


# -----------------------------------
# 개별 아이템 파싱
# -----------------------------------
def parse_item(item, idx):
    # 1위 처리: 리스트 첫 번째 요소는 무조건 rank=1
    if idx == 0:
        rank = 1
    else:
        rank = extract_rank(item)

    # 제목
    title_tag = item.select_one("a.prod_link.line-clamp-2")
    title = title_tag.get_text(strip=True) if title_tag else None

    # 저자 / 출판사 / 출판일
    info_tag = item.select_one("div.line-clamp-2.fz-14")
    author = publisher = pub_date = None
    if info_tag:
        parts = info_tag.get_text(" ", strip=True).split("·")
        parts = [p.strip() for p in parts]
        if len(parts) == 3:
            author, publisher, pub_date = parts

    # 할인율
    # 할인율 (어떤 패턴이든 % 포함 숫자를 찾으면 인식)
    discount = None

    # text-green-800이 포함된 모든 span 확인
    green_tags = item.select("span.text-green-800")

    for tg in green_tags:
        txt = tg.get_text(strip=True)
        if re.match(r"^\d+%$", txt):
            discount = txt
            break

    # 그래도 없으면 fallback: 전체 span에서 % 포함 텍스트 찾기
    if discount is None:
        tag_any = item.find("span", string=re.compile(r"\d+%"))
        if tag_any:
            txt = tag_any.get_text(strip=True)
            if re.match(r"^\d+%$", txt):
                discount = txt


    # 판매가격
    price_tag = item.select_one("span.fz-16 span.font-bold")
    price = price_tag.get_text(strip=True).replace(",", "") if price_tag else None

    # 평점
    score_tag = item.select_one("span.font-bold.text-black")
    score = score_tag.get_text(strip=True) if score_tag else None

    return {
        "rank": rank,
        "title": title,
        "author": author,
        "publisher": publisher,
        "pub_date": pub_date,
        "discount": discount,
        "price": price,
        "score": score,
        "site": "교보문고"
    }


# -----------------------------------
# 월간 베스트 1달 크롤링
# -----------------------------------
def kyobo_month_bestseller(ym):
    url = f"https://store.kyobobook.co.kr/bestseller/total/monthly?ym={ym}&page=1&per=50"
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.select("li.mt-9")  # 핵심 selector

    print(f"{ym} 수집 개수: {len(items)}")

    rows = []
    for idx, item in enumerate(items):
        data = parse_item(item, idx)
        data["ym"] = ym
        rows.append(data)

    return pd.DataFrame(rows)


# -----------------------------------
# 여러 달 자동 크롤링
# -----------------------------------
def multi_month_bestseller(start_ym, end_ym):
    start_year, start_month = int(start_ym[:4]), int(start_ym[4:])
    end_year, end_month = int(end_ym[:4]), int(end_ym[4:])

    all_df = pd.DataFrame()
    year, month = start_year, start_month

    while True:
        ym = f"{year}{month:02d}"
        df = kyobo_month_bestseller(ym)
        all_df = pd.concat([all_df, df], ignore_index=True)

        if year == end_year and month == end_month:
            break

        month += 1
        if month > 12:
            year += 1
            month = 1

    return all_df


# -----------------------------------
# CSV 저장
# -----------------------------------
def save_to_csv(df, filename):
    if df is None or df.empty:
        print("⚠ 저장할 데이터가 없습니다.")
        return
    df.to_csv(filename, encoding="utf-8-sig", index=False)
    print(f"📁 CSV 저장 완료: {filename} (총 {len(df)}개)")


# -----------------------------------
# 실행부
# -----------------------------------
if __name__ == "__main__":
    df_all = multi_month_bestseller("202412", "202512")
    save_to_csv(df_all, "kyobo_2024_2025.csv")
    print(df_all.head())
