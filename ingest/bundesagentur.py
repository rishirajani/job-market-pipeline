import time, dlt
from dlt.sources.helpers import requests

API = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
HEADERS = {"X-API-Key": "jobboerse-jobsuche"}
PAGE_SIZE = 100
SEARCH_TERMS = ["Data Engineer", "Analytics Engineer", "Data Analyst", 
                "Business Intelligence", "Ontology", "Knowledge Graph", 
                "Knowledge Engineer", "Semantic Web", "Linked Data",
                ]

@dlt.resource(name="ba_jobs", primary_key="referenznummer", write_disposition="merge")
def ba_jobs(days:int = 7, max_pages:int = 5):
    for term in SEARCH_TERMS:
        for page in range(1, max_pages + 1):
            params = {"was": term, "angebotsart": 1, "veroeffentlichtseit": days, 
                      "size": PAGE_SIZE, "page": page}
            response = requests.get(f"{API}/pc/v6/jobs", headers=HEADERS, params=params, timeout=30)
            ads = response.json().get("ergebnisliste", [])
            print(f"{term} page {page}: {len(ads)} ads (total {response.json().get('maxErgebnisse')})")
            for ad in ads:
                ad["search_term"] = term 
            yield ads
            if len(ads) < PAGE_SIZE:
                break
            time.sleep(0.5)

if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="bundesagentur",
        destination=dlt.destinations.duckdb("data/market.duckdb"),
        dataset_name="raw_bundesagentur",
    )
    print(pipeline.run(ba_jobs()))
    