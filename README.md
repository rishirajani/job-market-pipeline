# job-market-pipeline

A daily pipeline over job ads. It loads ads from public job APIs into DuckDB and models them with dbt, to answer questions such as which skills data- and knowledge-graph-roles demand, what their compensation is and what languages they require.

**Status: in progress.** Loading and first staging models work; check roadmap.

## Workflow

| Step | Tool | Function |
|---|---|---|
| Load | [dlt](https://dlthub.com) | One loader per source, merged on each ad's ID, so re-runs update rather than duplicate. Implemented sources so far: Arbeitnow, Bundesagentur für Arbeit |
| Store | DuckDB | Single local file; `data/market.duckdb` |
| Model | [dbt](https://www.getdbt.com) | Staging models with declared sources and tests |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python ingest/arbeitnow.py
python ingest/bundesagentur.py

cd market
dbt build
```

## What's built

- `ingest/`: one dlt loader per source
- `market/models/staging/arbeitnow/`: ads and their job types, renamed and typed
- Tests: `unique`, `not_null`, a `relationships` test between job types and ads,
  and a singular test that no ad is forward-dated

## Roadmap

- Search terms as their own table, and ad descriptions fetched once per new ad
- Bundesagentur staging model, then both sources combined and de-duplicated
- Language requirements, seniority and skills (mapped to ESCO) extracted from the ad text
- More sources: company career pages (Greenhouse, Lever, Personio) and other countries
- Final tables and a weekly market report
- Scheduled daily runs with GitHub Actions
