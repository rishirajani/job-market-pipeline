-- Every country must be an ISO code from the country_codes seed.
-- A row here means the BA sent a country the seed doesn't know yet: add it to seeds/country_codes.csv.
select source_job_id, country
from {{ ref('stg_bundesagentur__jobs') }}
where country is not null
and length(country) <> 2
