-- ============================================================
-- BigQuery Raw Layer DDL — Sandbox 실행용
-- 운영용 설계는 raw_schema_bigquery.sql (날짜 파티션 + 클러스터링) 참고
--
-- 이 파일을 따로 두는 이유:
--   BigQuery Sandbox는 테이블·파티션 기본 만료가 60일로 고정된다.
--   파티션 만료는 "파티션 날짜" 기준이라, 2023-01-01 ~ 2025-12-31 데이터를
--   날짜 파티션 테이블에 넣으면 모든 파티션이 이미 60일을 넘겨 적재 직후 삭제된다.
--   그래서 Sandbox에서는 PARTITION BY 만 빼고, 컬럼·제약·CLUSTER BY는 운영용과 동일하게 둔다.
--
-- 주의:
--   - 파티션이 없는 테이블도 Sandbox에서는 "생성 시점" 기준 60일 뒤 테이블째 삭제된다.
--   - Sandbox는 DML(INSERT/UPDATE/DELETE/MERGE)이 불가하므로 적재는 load job
--     (load_to_bigquery.py, WRITE_TRUNCATE)으로만 한다.
--   - 실행 시 기본 프로젝트를 지정해야 한다 (bq --project_id=<GCP_PROJECT_ID> query ...).
-- 모든 데이터는 synthetic(가상)이며 실제 회사 데이터가 아님
-- ============================================================

CREATE SCHEMA IF NOT EXISTS `raw`
OPTIONS (location = 'asia-northeast3');  -- 서울 리전

CREATE TABLE IF NOT EXISTS `raw.sales_kpi_daily` (
  date                        DATE        NOT NULL,
  category                    STRING      NOT NULL,
  category_group              STRING      NOT NULL,
  subcategory                 STRING      NOT NULL,
  gmv                         NUMERIC     NOT NULL,
  revenue                     NUMERIC     NOT NULL,
  unitsold                    INT64       NOT NULL,
  unit_price_ex_vat           NUMERIC     NOT NULL,
  ad_funding                  NUMERIC,
  rebate_funding              NUMERIC,
  review_program_funding      NUMERIC,
  data_insight_funding        NUMERIC,
  gross_category_gp           NUMERIC     NOT NULL,
  ad_cost                     NUMERIC,
  review_program_cost         NUMERIC,
  data_insight_cost           NUMERIC,
  net_gross_category_gp       NUMERIC     NOT NULL
)
CLUSTER BY subcategory;  -- 운영용과 달리 PARTITION BY date 없음

CREATE TABLE IF NOT EXISTS `raw.search_funnel_daily` (
  date            DATE    NOT NULL,
  keyword         STRING  NOT NULL,
  subcategory     STRING  NOT NULL,
  impressions     INT64   NOT NULL,
  clicks          INT64   NOT NULL,
  sdp_views       INT64   NOT NULL,
  add_to_cart     INT64   NOT NULL,
  purchases       INT64   NOT NULL,
  gmv             NUMERIC NOT NULL,
  unitsold        INT64   NOT NULL
)
CLUSTER BY subcategory, keyword;  -- 운영용과 달리 PARTITION BY date 없음

CREATE TABLE IF NOT EXISTS `raw.keyword_dim` (
  keyword               STRING NOT NULL,
  mapped_subcategory    STRING NOT NULL,
  search_volume_tier    STRING NOT NULL
);
