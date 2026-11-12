# Superset 대시보드 설계안

원칙: 차트 타입은 데이터의 "역할"(매출 추이/크기 비교/구조 분석)에 따라 고르고, 색은 서브카테고리별로 고정 순서 배정(필터로 계열 수가 바뀌어도 같은 서브카테고리는 항상 같은 색). 2축(dual-axis) 차트는 쓰지 않음 — 스케일이 다른 지표는 별도 차트로 분리.

서브카테고리 색 고정 순서(6개, 항상 이 순서로 배정):
`Drinks → Water → Snacks → Coffee & Tea → Meal Essentials → Healthy Food`

---

## 대시보드 1: 매출/마진 KPI

**필터 바 (상단 1줄)**: 기간(월 범위) / 서브카테고리(멀티셀렉트)

| 순서 | 차트 | 타입 | 소스 | 비고 |
|---|---|---|---|---|
| 1 | 최신월 GMV · YoY 성장률 | Big Number with Trendline | `mart_kpi_monthly_summary` | 헤드라인 숫자, 전체 서브카테고리 합산 |
| 2 | 최신월 Net Margin% · YoY delta(%p) | Big Number with Trendline | `mart_kpi_monthly_summary` | 마진율은 %p 단위로 delta 표기 |
| 3 | 월별 GMV 추이 (서브카테고리별) | Line Chart | `mart_kpi_monthly_summary` | x=month_start, y=gmv, color=subcategory, 범례 항상 표시 |
| 4 | 월별 Net Margin% 추이 (서브카테고리별) | Line Chart | `mart_kpi_monthly_summary` | GMV 차트와 분리(스케일 다름 → dual-axis 대신 별도 차트) |
| 5 | 서브카테고리별 최신월 YoY 성장률 비교 | Bar Chart (가로) | `mart_kpi_monthly_summary` | gmv_yoy_growth_pct 내림차순 정렬 |
| 6 | 월별 KPI 상세 테이블 | Table | `mart_kpi_monthly_summary` | gmv, revenue, net_margin_pct, 각 성장률 — 검증 가능성 어필용 |

## 대시보드 2: 검색 Funnel / SDP 개선

**필터 바**: 기간(월 범위) / 서브카테고리 / search_volume_tier

| 순서 | 차트 | 타입 | 소스 | 비고 |
|---|---|---|---|---|
| 1 | CTR·ATC율·CVR 월별 추이 | Line Chart (3계열) | `mart_search_funnel_monthly_trend` | 세 지표 모두 %단위로 스케일 동일 → 한 차트에 3계열 가능. 계열색은 카테고리 색과 별도로 지표용 고정 3색 사용 |
| 2 | 퍼널 단계별 전환 (노출→클릭→SDP진입→장바구니→구매) | Funnel Chart | `mart_search_funnel_daily` (집계) | 서브카테고리 필터 적용 시 해당 카테고리만 |
| 3 | 서브카테고리별 최신월 CVR 비교 | Bar Chart | `mart_search_funnel_monthly_trend` | 내림차순 정렬 |
| 4 | 키워드 Top 20 (GMV 기준) | Table | `mart_search_funnel_daily` (집계) | keyword, impressions, ctr_pct, cvr_pct, gmv |

---

## 적용한 디자인 원칙 (dataviz 기준)

- **2축 금지**: GMV와 마진율처럼 스케일이 다른 지표는 같은 차트에 절대 안 넣고 분리된 차트로 둠
- **카테고리 색 고정 순서**: 필터로 서브카테고리 수가 바뀌어도(예: Drinks만 필터링) 항상 같은 색 유지 — 생존한 계열이 재배색되지 않도록
- **단일 계열은 범례 생략**: 지표 1개짜리 차트(예: YoY 성장률 바 차트)는 제목으로 충분, 범례 불필요
- **다계열은 범례 필수**: 서브카테고리 6개 라인차트는 항상 범례 표시, 4개 이하면 직접 라벨링도 병행
- **헤드라인은 숫자로**: "지금 당장 알아야 할 숫자"(최신 GMV, 마진 YoY)는 차트가 아니라 Big Number 카드로 먼저 보여줌
