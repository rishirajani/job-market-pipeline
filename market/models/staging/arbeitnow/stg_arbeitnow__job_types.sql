with job_types as (
    select *
    from {{ source('arbeitnow', 'arbeitnow_jobs__job_types') }}
),

jobs as (
    select _dlt_id, slug
    from {{ source('arbeitnow', 'arbeitnow_jobs') }}
)

select 
    j.slug as source_job_id,
    lower(trim(t.value)) as job_type,
    t._dlt_list_idx as position
from job_types t
join jobs j on j._dlt_id = t._dlt_parent_id
