with jobs as (
    select *
    from {{ source('bundesagentur', 'ba_jobs') }}
),

details as (
    select referenznummer, stellenangebots_beschreibung
    from {{  source('bundesagentur', 'ba_job_details') }}
), 

locations as (
    select _dlt_parent_id, adresse__ort, adresse__land
    from {{ source('bundesagentur', 'ba_jobs__stellenlokationen') }}
    where _dlt_list_idx = 0
),

country_codes as (
    select *
    from {{ ref('country_codes') }}
),

renamed as (
    select 
        'bundesagentur' as source,
        j.referenznummer as source_job_id,
        j.stellenangebots_titel as job_title,
        j.firma as company_name,
        l.adresse__ort as location,
        coalesce(c.iso_code, l.adresse__land) as country,
        coalesce(j.homeofficeprozent = 100, false) as is_remote, -- true only in cases where the ad is 100% remote; nulls count as not remote
        j.homeofficemoeglich as home_office_possible, -- treated as hybrid work when is_remote is false and home_office_possible is true; nulls just mean its unknown information
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
    left join locations l on l._dlt_parent_id = j._dlt_id
    left join country_codes c on c.ba_country_name = l.adresse__land
)

select *
from renamed 
