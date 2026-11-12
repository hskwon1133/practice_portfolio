-- mart: sales_margin_daily
-- 서브카테고리 x 일자 그레인의 매출/마진 분석 마트.
-- gross/net margin %을 계산해 대시보드(Superset)에서 바로 사용 가능한 형태로 제공.

with staged as (

    select * from {{ ref('stg_sales_kpi_daily') }}

),

final as (

    select
        order_date,
        category,
        category_group,
        subcategory,
        gmv,
        revenue,
        unitsold,
        unit_price_ex_vat,

        -- funding/cost 합계
        (ad_funding + rebate_funding + review_program_funding + data_insight_funding)   as total_funding,
        (ad_cost + review_program_cost + data_insight_cost)                             as total_cost,

        gross_category_gp,
        net_gross_category_gp,

        -- 마진율 (%)
        round(safe_divide(gross_category_gp, revenue) * 100, 2)      as gross_margin_pct,
        round(safe_divide(net_gross_category_gp, revenue) * 100, 2)  as net_margin_pct,

        -- 평균 판매단가
        round(safe_divide(revenue, nullif(unitsold, 0)), 2)          as avg_selling_price

    from staged

)

select * from final
