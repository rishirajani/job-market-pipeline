import duckdb

c = duckdb.connect("data/market.duckdb")
query = """
    select a.job_id, a.source, a.job_title, a.company_name, a.location, a.posted_at, 
    b.source, b.job_title, b.company_name, b.location, b.posted_at
    from main.int_jobs__unioned a join main.int_jobs__unioned b 
    on trim(lower(a.company_name)) = trim(lower(b.company_name))  
    where a.source = 'arbeitnow' 
    and b.source = 'bundesagentur'
    """
print(c.sql(query).fetchall())

# Findings, 2026-11-13
#
# Cross-source duplicates: across Arbeitnow (1,500 ads) and the Bundesagentur (347),
# only one company appears in both (IONOS SE), with different jobs. No duplicates to
# remove yet. Revisit when company career pages (Greenhouse, Lever, Personio) are added.