-- staging: search_funnel_daily
-- 퍼널 단계가 역전되는(비정상) 행을 걸러내고 표준 컬럼명으로 정리한다.

with source as (

    select * from {{ source('raw', 'search_funnel_daily') }}

),

cleaned as (

    select
        date            as event_date,
        keyword,
        subcategory,
        impressions,
        clicks,
        sdp_views,
        add_to_cart,
        purchases,
        gmv,
        unitsold

    from source
    where impressions >= clicks
      and clicks >= 0
      and sdp_views >= 0
      and date is not null

)

select * from cleaned
