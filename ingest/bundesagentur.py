import time, dlt, base64, duckdb
from dlt.sources.helpers import requests

API = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
HEADERS = {"X-API-Key": "jobboerse-jobsuche"}
PAGE_SIZE = 100
SEARCH_TERMS = ["Data Engineer", "Analytics Engineer", "Data Analyst", 
                "Business Intelligence", "Ontology", "Knowledge Graph", 
                "Knowledge Engineer", "Semantic Web", "Linked Data",
                ]
DETAILS_TABLE = "ba_job_details"

@dlt.resource(name="ba_jobs", primary_key="referenznummer", write_disposition="merge")
def ba_jobs(days: int = 7, max_pages: int = 5):
    found = {}
    for term in SEARCH_TERMS:
        for page in range(1, max_pages + 1):
            params = {"was": term, "angebotsart": 1, "veroeffentlichtseit": days, 
                      "size": PAGE_SIZE, "page": page}
            response = requests.get(f"{API}/pc/v6/jobs", headers=HEADERS, params=params, timeout=30)
            ads = response.json().get("ergebnisliste", [])
            print(f"{term} page {page}: {len(ads)} ads (total {response.json().get('maxErgebnisse')})")
            for ad in ads:
                ref = ad["referenznummer"]
                if ref not in found:
                    found[ref] = ad
                    found[ref]["search_terms"] = []
                found[ref]["search_terms"].append(term)
            if len(ads) < PAGE_SIZE:
                break
            time.sleep(0.5)
    yield list(found.values())

def known_details():
    """IDs of ads whose details are already in the warehouse."""
    con = duckdb.connect("data/market.duckdb")
    try:
        rows = con.sql(f"select referenznummer from raw_bundesagentur.{DETAILS_TABLE}").fetchall()
        return {row[0] for row in rows}
    except duckdb.CatalogException:
        try:
            ads = con.sql("select count(*) from raw_bundesagentur.ba_jobs").fetchone()[0]
        except duckdb.CatalogException:
            ads = 0
        if ads:
            print(f"WARNING: {ads} ads are stored but the table {DETAILS_TABLE} is missing. "
                  "Fetching details for every ad again. Check the table name.")
        return set()
    finally:
        con.close()

def bundesagentur(known):
    @dlt.transformer(name=DETAILS_TABLE, primary_key="referenznummer", 
                     write_disposition="merge")
    def ba_job_details(ads):
        fetched = 0
        for ad in ads:
            ref = ad["referenznummer"]
            if ref in known:
                continue
            encoded = base64.b64encode(ref.encode()).decode()
            try:
                response = requests.get(f"{API}/pc/v4/jobdetails/{encoded}", headers=HEADERS, timeout=30)
            except Exception as error:
                print(f" no details for {ref}: {error}")
                continue
            yield response.json()
            fetched += 1
            time.sleep(0.3)
        print(f"details fetched: {fetched}, skipped: {len(ads) - fetched}")

    jobs = ba_jobs()
    return [jobs, jobs | ba_job_details]

if __name__ == "__main__":
    known = known_details()
    print(f"details already stored: {len(known)}")
    pipeline = dlt.pipeline(
        pipeline_name="bundesagentur",
        destination=dlt.destinations.duckdb("data/market.duckdb"),
        dataset_name="raw_bundesagentur",
    )
    print(pipeline.run(bundesagentur(known)))
    