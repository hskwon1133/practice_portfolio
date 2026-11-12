-- mart: search_funnel_daily
-- 키워드 x 서브카테고리 x 일자 그레인. 퍼널 전환율(CTR/ATC율/CVR)을 계산.

with staged as (

    select f.*, k.search_volume_tier
    from {{ ref('stg_search_funnel_daily') }} f
    left join {{ ref('stg_keyword_dim') }} k
        on f.keyword = k.keyword

),

final as (

    select
        event_date,
        keyword,
        subcategory,
        search_volume_tier,
        impressions,
        clicks,
        sdp_views,
        add_to_cart,
        purchases,
        gmv,
        unitsold,

        round(safe_divide(clicks, nullif(impressions, 0)) * 100, 3)       as ctr_pct,
        round(safe_divide(add_to_cart, nullif(sdp_views, 0)) * 100, 3)    as atc_rate_pct,
        round(safe_divide(purchases, nullif(clicks, 0)) * 100, 3)         as cvr_pct

    from staged

)

select * from final
