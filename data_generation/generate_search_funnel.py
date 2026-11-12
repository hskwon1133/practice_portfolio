"""
generate_search_funnel.py
---------------------------------------------------------------
DB2: 검색어 기준 SDP 개선 Funnel 분석용 synthetic 데이터 생성

그레인: 키워드 x 서브카테고리 x 일자
기간: 2023-01-01 ~ 2025-12-31 (DB1과 동일, 3개년)
키워드: 서브카테고리당 10개 x 6개 서브카테고리 = 60개

퍼널: 노출(impressions) -> 클릭(clicks, CTR) -> SDP 진입(sdp_views)
      -> 장바구니(add_to_cart) -> 구매(purchases, CVR)

스토리라인: SDP 개선 작업으로 CTR/장바구니전환율/CVR이 3개년에 걸쳐
완만하게 개선되는 추세를 반영 (연간 개선 트렌드 + 랜덤 노이즈).
모든 수치는 가상(synthetic) 데이터이며 실제 회사 데이터가 아님.
---------------------------------------------------------------
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

DATES = pd.date_range("2023-01-01", "2025-12-31", freq="D")

# 서브카테고리별 키워드 10개 + 검색량 티어 + 평균 단가(ppp 유사치)
KEYWORDS = {
    "Drinks": {
        "tier": "High",
        "avg_price": 1800,
        "words": ["탄산음료", "주스", "이온음료", "커피음료", "탄산수",
                  "에너지드링크", "두유", "티음료", "스무디", "레모네이드"],
    },
    "Water": {
        "tier": "High",
        "avg_price": 900,
        "words": ["생수", "미네랄워터", "탄산수세트", "유아용생수", "온천수",
                  "스파클링워터", "먹는샘물", "정수기필터", "생수세트", "대용량생수"],
    },
    "Snacks": {
        "tier": "Mid",
        "avg_price": 2400,
        "words": ["과자", "초콜릿", "젤리", "스낵", "견과류",
                  "쿠키", "감자칩", "비스킷", "에너지바", "팝콘"],
    },
    "Coffee & Tea": {
        "tier": "Mid",
        "avg_price": 3600,
        "words": ["커피캡슐", "원두커피", "인스턴트커피", "티백", "녹차",
                  "홍차", "콜드브루", "디카페인커피", "커피믹스", "허브티"],
    },
    "Meal Essentials": {
        "tier": "Mid",
        "avg_price": 4800,
        "words": ["즉석밥", "라면", "소스", "조미료", "식용유",
                  "간장", "참기름", "카레", "짜장소스", "국물요리"],
    },
    "Healthy Food": {
        "tier": "Low",
        "avg_price": 7200,
        "words": ["프로틴바", "비타민", "건강식품", "다이어트식품", "오트밀",
                  "그래놀라", "현미", "곤약", "저칼로리간식", "유산균"],
    },
}

TIER_BASE_IMPRESSIONS = {"High": (3000, 6000), "Mid": (1000, 3000), "Low": (300, 1000)}


def build_keyword_dim():
    rows = []
    for subcat, cfg in KEYWORDS.items():
        for kw in cfg["words"]:
            rows.append({
                "keyword": kw,
                "mapped_subcategory": subcat,
                "search_volume_tier": cfg["tier"],
            })
    return pd.DataFrame(rows)


def seasonal_factor(date):
    f = 1.0
    if date.month in (6, 7, 8):
        f += 0.15
    if date.month == 12:
        f += 0.20
    if date.weekday() >= 5:
        f *= 1.08
    return f


def yearly_improvement(date, start_year=2023):
    """SDP 개선으로 인한 연차별 CTR/ATC/CVR 개선 배수 (완만한 우상향)."""
    years_elapsed = (date - pd.Timestamp(f"{start_year}-01-01")).days / 365.0
    return years_elapsed  # 0.0 ~ 3.0 선형 증가


def simulate_keyword(subcat, keyword, tier, avg_price):
    lo, hi = TIER_BASE_IMPRESSIONS[tier]
    base_impressions = RNG.uniform(lo, hi)
    base_ctr = RNG.uniform(0.03, 0.07)
    base_sdp_rate = RNG.uniform(0.90, 0.97)
    base_atc_rate = RNG.uniform(0.14, 0.22)
    base_cart_to_purchase = RNG.uniform(0.45, 0.60)

    # 연간 개선폭 (서브카테고리/키워드별로 약간 다르게)
    ctr_improve_per_year = RNG.uniform(0.002, 0.006)
    atc_improve_per_year = RNG.uniform(0.005, 0.015)
    cvr_improve_per_year = RNG.uniform(0.01, 0.025)

    rows = []
    for d in DATES:
        season = seasonal_factor(d)
        yrs = yearly_improvement(d)

        impressions = base_impressions * season * RNG.normal(1.0, 0.08)
        impressions = max(impressions, 0)

        ctr = min(base_ctr + ctr_improve_per_year * yrs + RNG.normal(0, 0.003), 0.20)
        ctr = max(ctr, 0.005)
        clicks = impressions * ctr

        sdp_views = clicks * min(base_sdp_rate + RNG.normal(0, 0.01), 1.0)

        atc_rate = min(base_atc_rate + atc_improve_per_year * yrs + RNG.normal(0, 0.01), 0.60)
        atc_rate = max(atc_rate, 0.02)
        add_to_cart = sdp_views * atc_rate

        c2p = min(base_cart_to_purchase + cvr_improve_per_year * yrs + RNG.normal(0, 0.02), 0.85)
        c2p = max(c2p, 0.10)
        purchases = add_to_cart * c2p

        unit_multiplier = RNG.uniform(1.0, 1.3)
        unitsold = purchases * unit_multiplier
        price = avg_price * RNG.uniform(0.97, 1.03)
        gmv = unitsold * price

        rows.append({
            "date": d.strftime("%Y-%m-%d"),
            "keyword": keyword,
            "subcategory": subcat,
            "impressions": round(impressions),
            "clicks": round(clicks),
            "sdp_views": round(sdp_views),
            "add_to_cart": round(add_to_cart),
            "purchases": round(purchases),
            "gmv": round(gmv, 2),
            "unitsold": round(unitsold),
        })
    return pd.DataFrame(rows)


def main():
    keyword_dim = build_keyword_dim()
    keyword_dim.to_csv("keyword_dim.csv", index=False, encoding="utf-8-sig")
    print(f"keyword_dim.csv: {len(keyword_dim)}행")

    all_frames = []
    for subcat, cfg in KEYWORDS.items():
        for kw in cfg["words"]:
            all_frames.append(simulate_keyword(subcat, kw, cfg["tier"], cfg["avg_price"]))

    df = pd.concat(all_frames, ignore_index=True)
    df = df.sort_values(["date", "subcategory", "keyword"]).reset_index(drop=True)
    df.to_csv("search_funnel_daily.csv", index=False, encoding="utf-8-sig")
    print(f"search_funnel_daily.csv: {len(df)}행")

    print("\n--- 미리보기 ---")
    print(df.head(5).to_string(index=False))

    print("\n--- 연도별 CTR/ATC-rate/CVR 추세 (개선 확인) ---")
    df["year"] = pd.to_datetime(df["date"]).dt.year
    summary = df.groupby("year").agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        sdp_views=("sdp_views", "sum"),
        add_to_cart=("add_to_cart", "sum"),
        purchases=("purchases", "sum"),
        gmv=("gmv", "sum"),
    )
    summary["ctr_pct"] = (summary["clicks"] / summary["impressions"] * 100).round(2)
    summary["atc_rate_pct"] = (summary["add_to_cart"] / summary["sdp_views"] * 100).round(2)
    summary["cvr_pct"] = (summary["purchases"] / summary["clicks"] * 100).round(2)
    print(summary[["ctr_pct", "atc_rate_pct", "cvr_pct", "gmv"]])


if __name__ == "__main__":
    main()
