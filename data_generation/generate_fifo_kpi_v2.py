"""
generate_fifo_kpi_v2.py
------------------------
가상(synthetic) Grocery 카테고리 일자별 KPI 데이터 생성.
실제 회사 데이터가 아닌 포트폴리오/BI 시연용 예시입니다.

구조: Grocery (대분류 고정)
  ├─ Beverages
  │    ├─ Drinks
  │    └─ Water
  ├─ Snacks, Coffee & Tea
  │    ├─ Snacks
  │    └─ Coffee & Tea
  └─ Meal & Healthy
       ├─ Meal Essentials
       └─ Healthy Food

기간: 3개년 일자 단위 (2023-01-01 ~ 2025-12-31)
그레인: subcategory x date (SKU 단위 아님, 서브카테고리 집계 기준)
원가: 서브카테고리별 FIFO 입고 배치 시뮬레이션
"""

import numpy as np
import pandas as pd
from collections import deque

rng = np.random.default_rng(7)

CATEGORY = "Grocery"

# (category_group, subcategory): 파라미터
# markup은 목표 순마진율(net margin)에 맞춰 역산한 값입니다.
# net_margin ≈ (1 - 1/(markup*0.975))*100 + ~1.8%p(Funding-Cost 순기여분)
SUBCATS = {
    ("Beverages", "Drinks"):               dict(base_units=1800, unit_growth=0.012, base_cost=650,  markup=1.570, summer_boost=0.35),   # 목표 순마진 35~38%
    ("Beverages", "Water"):                dict(base_units=2600, unit_growth=0.008, base_cost=350,  markup=1.854, summer_boost=0.45),   # 목표 순마진 45~48%
    ("Snacks, Coffee & Tea", "Snacks"):     dict(base_units=1500, unit_growth=0.015, base_cost=900,  markup=1.293, summer_boost=0.05),   # 목표 순마진 20%대 초중반
    ("Snacks, Coffee & Tea", "Coffee & Tea"): dict(base_units=900,  unit_growth=0.020, base_cost=1400, markup=1.535, summer_boost=-0.10), # 캡슐커피 영향, 목표 순마진 ~35%
    ("Meal & Healthy", "Meal Essentials"):  dict(base_units=1100, unit_growth=0.010, base_cost=2200, markup=1.535, summer_boost=0.0),    # Sauce & Seasoning 영향, 목표 순마진 ~35%
    ("Meal & Healthy", "Healthy Food"):     dict(base_units=700,  unit_growth=0.025, base_cost=3200, markup=1.633, summer_boost=0.10),   # 목표 순마진 38~40%
}

DATES = pd.date_range("2023-01-01", "2025-12-31", freq="D")


def seasonal_factor(date: pd.Timestamp, summer_boost: float) -> float:
    # 여름철(6~8월) 음료/생수 등 성수기 반영, 연말(12월) 소폭 성수기
    month = date.month
    season = 1.0
    if month in (6, 7, 8):
        season += summer_boost
    if month == 12:
        season += 0.08
    # 요일 효과: 주말 소폭 상승
    if date.weekday() >= 5:
        season *= 1.06
    return season


def simulate_subcat(group: str, subcat: str, p: dict) -> pd.DataFrame:
    inventory = deque()  # FIFO: [qty, unit_cost]
    unit_cost_level = float(p["base_cost"])
    rows = []

    for day_idx, date in enumerate(DATES):
        year_progress = day_idx / 365.25
        growth = (1 + p["unit_growth"]) ** year_progress
        season = seasonal_factor(date, p["summer_boost"])

        # --- 입고: 7일마다 배치 입고, 원가는 완만한 랜덤워크 ---
        if day_idx % 7 == 0:
            unit_cost_level *= (1 + rng.normal(0.0008, 0.006))
            receive_qty = int(p["base_units"] * growth * 7 * rng.uniform(1.05, 1.30))
            inventory.append([receive_qty, round(unit_cost_level, 2)])

        # --- 판매량 ---
        unitsold = max(0, int(p["base_units"] * growth * season * rng.uniform(0.85, 1.10)))

        # --- FIFO 원가 계산 ---
        to_consume = unitsold
        cogs = 0.0
        while to_consume > 0 and inventory:
            batch = inventory[0]
            take = min(batch[0], to_consume)
            cogs += take * batch[1]
            batch[0] -= take
            to_consume -= take
            if batch[0] == 0:
                inventory.popleft()
        if to_consume > 0:
            cogs += to_consume * unit_cost_level  # 재고 부족 시 최신 단가로 보충

        # --- 판매가 & GMV / Revenue ---
        unit_price_ex_vat = round(unit_cost_level * p["markup"] * rng.uniform(0.98, 1.02), 1)
        gmv = round(unitsold * unit_price_ex_vat, 0)
        revenue = round(gmv * rng.uniform(0.96, 0.99), 0)

        # --- Funding / Cost ---
        ad_funding = round(gmv * rng.uniform(0.008, 0.020), 0)
        rebate_funding = round(gmv * rng.uniform(0.005, 0.015), 0)
        review_program_funding = round(gmv * rng.uniform(0.002, 0.006), 0)
        data_insight_funding = round(gmv * rng.uniform(0.001, 0.004), 0)

        ad_cost = round(ad_funding * rng.uniform(0.30, 0.50), 0)
        review_program_cost = round(review_program_funding * rng.uniform(0.40, 0.60), 0)
        data_insight_cost = round(data_insight_funding * rng.uniform(0.30, 0.50), 0)

        gross_category_gp = round(revenue - cogs, 0)
        net_gross_category_gp = round(
            gross_category_gp
            + ad_funding + rebate_funding + review_program_funding + data_insight_funding
            - ad_cost - review_program_cost - data_insight_cost,
            0,
        )

        rows.append(dict(
            date=date.strftime("%Y-%m-%d"),
            category=CATEGORY,
            category_group=group,
            subcategory=subcat,
            gmv=gmv,
            revenue=revenue,
            unitsold=unitsold,
            unit_price_ex_vat=unit_price_ex_vat,
            ad_funding=ad_funding,
            rebate_funding=rebate_funding,
            review_program_funding=review_program_funding,
            data_insight_funding=data_insight_funding,
            gross_category_gp=gross_category_gp,
            ad_cost=ad_cost,
            review_program_cost=review_program_cost,
            data_insight_cost=data_insight_cost,
            net_gross_category_gp=net_gross_category_gp,
        ))

    return pd.DataFrame(rows)


def main():
    dfs = [simulate_subcat(g, s, p) for (g, s), p in SUBCATS.items()]
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(["date", "category_group", "subcategory"]).reset_index(drop=True)

    df.to_csv("sales_kpi_daily.csv", index=False, encoding="utf-8-sig")

    print("총 행 수:", len(df))
    print("기간:", df["date"].min(), "~", df["date"].max())
    print("\n[미리보기 - 2023-01-01]")
    print(df[df["date"] == "2023-01-01"].to_string(index=False))
    print("\n[서브카테고리별 3개년 합계]")
    summary = df.groupby(["category_group", "subcategory"]).agg(
        total_gmv=("gmv", "sum"),
        total_revenue=("revenue", "sum"),
        total_units=("unitsold", "sum"),
        avg_net_margin_pct=("net_gross_category_gp", lambda x: round(100 * x.sum() / df.loc[x.index, "revenue"].sum(), 2)),
    ).reset_index()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
