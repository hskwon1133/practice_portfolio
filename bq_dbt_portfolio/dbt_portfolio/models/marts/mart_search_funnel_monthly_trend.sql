-- mart: search_funnel_monthly_trend
-- 서브카테고리 x 월 그레인. SDP 개선 스토리라인(CTR/ATC율/CVR의 연도별 개선 추세)을
-- Superset 대시보드에서 바로 라인차트로 보여줄 수 있는 형태로 집계.

with daily as (

    select * from {{ ref('mart_search_funnel_daily') }}

),

monthly as (

    select
        date_trunc(event_date, month) as month_start,
        subcategory,

        sum(impressions)   as impressions,
        sum(clicks)        as clicks,
        sum(sdp_views)     as sdp_views,
        sum(add_to_cart)   as add_to_cart,
        sum(purchases)     as purchases,
        sum(gmv)           as gmv

    from daily
    group by 1, 2

)

select
    month_start,
    subcategory,
    impressions,
    clicks,
    sdp_views,
    add_to_cart,
    purchases,
    gmv,

    round(safe_divide(clicks, nullif(impressions, 0)) * 100, 3)     as ctr_pct,
    round(safe_divide(add_to_cart, nullif(sdp_views, 0)) * 100, 3)  as atc_rate_pct,
    round(safe_divide(purchases, nullif(clicks, 0)) * 100, 3)       as cvr_pct

from monthly
order by subcategory, month_start
