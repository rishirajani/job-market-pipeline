with source as (
    select *
    from {{ source('arbeitnow', 'arbeitnow_jobs') }}
),

renamed as (
    select 'arbeitnow' as source, 
           slug as source_job_id, 
           title as job_title, 
           company_name,
           nullif(trim(location), '') as location,
           remote as is_remote,
           url as job_url,
           to_timestamp(created_at) as posted_at, 
           trim(regexp_replace(
                replace(
                    replace(
                        replace(description, '&lt;', '<'), 
                        '&gt;', '>'), 
                    '&amp;', '&'), 
                '<[^>]+>', ' ', 'g')) as description_text, 
           _dlt_id as dlt_id,
           _dlt_load_id as dlt_load_id
    from source
)

select *
from renamed
