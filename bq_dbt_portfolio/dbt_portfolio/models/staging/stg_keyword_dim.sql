-- staging: keyword_dim

select
    keyword,
    mapped_subcategory,
    search_volume_tier

from {{ source('raw', 'keyword_dim') }}
