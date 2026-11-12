import duckdb

c = duckdb.connect("data/market.duckdb")
query = """
    select distinct company_name
    from main.int_jobs__unioned 
    order by 1
    """
print(c.sql(query).fetchall())

# Findings, 2026-11-13
#
# Company names are inconsistent, even within one source:
# - case and spacing: OpenAI / Openai, SumUp / sumup, "Deliveroo" / "Deliveroo "
# - branches: FERCHAU GmbH Niederlassung ... (9 variants), Brunel GmbH NL ..., Hays ... Standort ...
# - scraping leftovers: Addepar1, Intetics 2, Artefactjobs / Artefactlinkedin
# - a job title in the company field: "Signal Processing Engineer (RF Processing & Analytics)"
# Any per-company count is wrong until names are normalised: lower-case, trim, strip legal
# suffixes (GmbH, SE, AG, & Co. KG) and branch suffixes, plus a seed for the odd cases.