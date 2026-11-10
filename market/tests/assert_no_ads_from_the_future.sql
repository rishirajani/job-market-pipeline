select *
from {{ ref('stg_arbeitnow__jobs') }}
where posted_at >= current_timestamp + interval 1 day 
