import os

from dataclasses import asdict
from loguru import logger

from scrape_projects.tinybird import DatasourcesApi, PipeApi
from scrape_projects.valorant.datasources import DATASOURCES, PIPES


tinybird_ds = DatasourcesApi(os.environ.get("TB_API_TOKEN"))

ds = DATASOURCES["valorant_results"]

existing_datasources = DatasourcesApi.get_datasources()["datasources"]
ds_already_exists = [
    x for x in existing_datasources if x["name"] == ds.name
]

if len(ds_already_exists) == 0:
    response = tinybird_ds.create_datasource(**asdict(ds))
else:
    logger.warning(
        f"Datsource named: {ds_already_exists[0]['name']} already exists, "
        f"created at {ds_already_exists[0]['created_at']} "
        f"with id {ds_already_exists[0]['id']}"
    )

logger.info(response)

tinybird_pipe = PipeApi(os.environ.get("TB_API_TOKEN"))

pipe = PIPES["valorant_results"]
create_pipe_response = tinybird_pipe.create_pipe(pipe.name, pipe.sql)
pipe_json = create_pipe_response.json()
