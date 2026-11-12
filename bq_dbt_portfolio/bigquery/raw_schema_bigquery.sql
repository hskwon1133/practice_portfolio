-- ============================================================
-- BigQuery Raw Layer DDL
-- 프로젝트: ba_portfolio (BigQuery Sandbox 무료 티어 기준)
-- 데이터셋: raw
-- 주의: 모든 데이터는 synthetic(가상)이며 실제 회사 데이터가 아님
-- ============================================================

CREATE SCHEMA IF NOT EXISTS `raw`
OPTIONS (location = 'asia-northeast3');  -- 서울 리전

-- ------------------------------------------------------------
-- raw.sales_kpi_daily
-- 그레인: 서브카테고리 x 일자
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `raw.sales_kpi_daily` (
  date                        DATE        NOT NULL,
  category                    STRING      NOT NULL,
  category_group              STRING      NOT NULL,
  subcategory                 STRING      NOT NULL,
  gmv                         NUMERIC     NOT NULL,
  revenue                     NUMERIC     NOT NULL,
  unitsold                    INT64       NOT NULL,
  ppp_wo_vat                  NUMERIC     NOT NULL,
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
PARTITION BY date
CLUSTER BY subcategory;

-- ------------------------------------------------------------
-- raw.search_funnel_daily
-- 그레인: 키워드 x 서브카테고리 x 일자
-- ------------------------------------------------------------
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
PARTITION BY date
CLUSTER BY subcategory, keyword;

-- ------------------------------------------------------------
-- raw.keyword_dim
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `raw.keyword_dim` (
  keyword               STRING NOT NULL,
  mapped_subcategory    STRING NOT NULL,
  search_volume_tier    STRING NOT NULL
);
