with jobs as (
    select *
    from {{ source('bundesagentur', 'ba_jobs') }}
),

details as (
    select referenznummer, stellenangebots_beschreibung
    from {{  source('bundesagentur', 'ba_job_details') }}
), 

renamed as (
    select 
        'bundesagentur' as source,
        j.referenznummer as source_job_id,
        j.stellenangebots_titel as job_title,
        j.firma as company_name,
        cast(null as varchar) as location,
        j.homeofficemoeglich as is_remote,
        case 
            when j.externe_url is NULL or j.externe_url like '' 
            then 'https://www.arbeitsagentur.de/jobsuche/jobdetail/' || j.referenznummer 
            else j.externe_url 
        end as job_url,
        j.datum_erste_veroeffentlichung::timestamptz as posted_at,
        trim(d.stellenangebots_beschreibung) as description_text,
        j._dlt_id as dlt_id,
        j._dlt_load_id as dlt_load_id
    from jobs j
    left join details d on j.referenznummer = d.referenznummer
)

select *
from renamed 
