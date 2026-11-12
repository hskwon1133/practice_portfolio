-- staging: sales_kpi_daily
-- 원천 테이블을 표준 컬럼명/타입으로 정리하고 기본 DQ 필터만 적용한다.
-- 비즈니스 로직(마진율 계산 등)은 marts 레이어에서 수행한다.

with source as (

    select * from {{ source('raw', 'sales_kpi_daily') }}

),

cleaned as (

    select
        date                                            as order_date,
        category,
        category_group,
        subcategory,
        gmv,
        revenue,
        unitsold,
        ppp_wo_vat,
        coalesce(ad_funding, 0)                         as ad_funding,
        coalesce(rebate_funding, 0)                     as rebate_funding,
        coalesce(review_program_funding, 0)             as review_program_funding,
        coalesce(data_insight_funding, 0)               as data_insight_funding,
        gross_category_gp,
        coalesce(ad_cost, 0)                            as ad_cost,
        coalesce(review_program_cost, 0)                as review_program_cost,
        coalesce(data_insight_cost, 0)                  as data_insight_cost,
        net_gross_category_gp

    from source
    -- 기본 DQ 필터: 매출이 음수이거나 날짜가 비어있는 비정상 행 제외
    where revenue >= 0
      and date is not null

)

select * from cleaned
