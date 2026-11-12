select 
    concat(source, ':', source_job_id) as job_id, source, source_job_id, 
    job_title, company_name, location, country, is_remote, 
    home_office_possible, job_url, posted_at, description_text, dlt_id, 
    dlt_load_id
from {{ ref('stg_bundesagentur__jobs') }}
union all
select 
    concat(source, ':', source_job_id) as job_id, source, source_job_id, 
    job_title, company_name, location, country, is_remote, 
    home_office_possible, job_url, posted_at, description_text, dlt_id, 
    dlt_load_id
from {{ ref('stg_arbeitnow__jobs') }}
