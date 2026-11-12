-- mart: kpi_monthly_summary
-- 서브카테고리 x 월 그레인의 핵심 KPI 거버넌스 마트.
-- MoM/YoY 성장률을 window function으로 계산해, 경영 리포팅에 바로 쓸 수 있는 형태로 제공.

with daily as (

    select * from {{ ref('mart_sales_margin_daily') }}

),

monthly as (

    select
        date_trunc(order_date, month)  as month_start,
        subcategory,
        category_group,

        sum(gmv)                       as gmv,
        sum(revenue)                   as revenue,
        sum(unitsold)                  as unitsold,
        sum(gross_category_gp)         as gross_category_gp,
        sum(net_gross_category_gp)     as net_gross_category_gp,

        -- 월 가중평균 마진율 (일별 %의 단순평균이 아니라 합산 기준으로 계산)
        round(safe_divide(sum(gross_category_gp), sum(revenue)) * 100, 2)      as gross_margin_pct,
        round(safe_divide(sum(net_gross_category_gp), sum(revenue)) * 100, 2)  as net_margin_pct

    from daily
    group by 1, 2, 3

),

with_growth as (

    select
        month_start,
        subcategory,
        category_group,
        gmv,
        revenue,
        unitsold,
        net_margin_pct,

        -- MoM: 직전월 대비
        lag(gmv) over (partition by subcategory order by month_start)      as gmv_prev_month,
        lag(revenue) over (partition by subcategory order by month_start) as revenue_prev_month,

        -- YoY: 전년 동월 대비 (12개월 전)
        lag(gmv, 12) over (partition by subcategory order by month_start)      as gmv_prev_year,
        lag(revenue, 12) over (partition by subcategory order by month_start) as revenue_prev_year,
        lag(net_margin_pct, 12) over (partition by subcategory order by month_start) as net_margin_pct_prev_year

    from monthly

)

select
    month_start,
    subcategory,
    category_group,
    gmv,
    revenue,
    unitsold,
    net_margin_pct,

    round(safe_divide(gmv - gmv_prev_month, gmv_prev_month) * 100, 2)          as gmv_mom_growth_pct,
    round(safe_divide(revenue - revenue_prev_month, revenue_prev_month) * 100, 2) as revenue_mom_growth_pct,

    round(safe_divide(gmv - gmv_prev_year, gmv_prev_year) * 100, 2)            as gmv_yoy_growth_pct,
    round(safe_divide(revenue - revenue_prev_year, revenue_prev_year) * 100, 2) as revenue_yoy_growth_pct,
    round(net_margin_pct - net_margin_pct_prev_year, 2)                        as net_margin_pct_yoy_delta

from with_growth
order by subcategory, month_start
