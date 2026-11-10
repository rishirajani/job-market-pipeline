import time
import dlt
from dlt.sources.helpers import requests


@dlt.resource(name="arbeitnow_jobs", primary_key="slug", write_disposition="merge")
def arbeitnow_jobs(max_pages: int = 5):
    url = "https://www.arbeitnow.com/api/job-board-api"
    for _ in range(max_pages):
        page = requests.get(url, timeout=30).json()
        yield page["data"]
        url = page["links"]["next"]
        if not url:
            break
        time.sleep(1)


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="arbeitnow",
        destination=dlt.destinations.duckdb("data/market.duckdb"),
        dataset_name="raw_arbeitnow",
    )
    print(pipeline.run(arbeitnow_jobs()))
