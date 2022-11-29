import os

from loguru import logger

from scrape_projects.tinybird import DatasourcesApi, PipeApi
from scrape_projects.valorant.datasources import VALORANT_RESULTS_DATASOURCE


tinybird_ds = DatasourcesApi(os.environ.get("TB_API_TOKEN"))

ds = VALORANT_RESULTS_DATASOURCE

existing_datasources = DatasourcesApi.get_datasources()["datasources"]
ds_already_exists = [x for x in existing_datasources if x["name"] == ds.name]

if len(ds_already_exists) == 0:
    response = tinybird_ds.create_datasource(
        format=ds.format,
        name=ds.name,
        mode=ds.mode,
        schema=ds.schema,
    )
else:
    logger.warning(
        f"Datsource named: {ds_already_exists[0]['name']} already exists, "
        f"created at {ds_already_exists[0]['created_at']} "
        f"with id {ds_already_exists[0]['id']}"
    )

logger.info(response)

tinybird_pipe = PipeApi(os.environ.get("TB_API_TOKEN"))

pipe = ds.pipes[0]
create_pipe_response = tinybird_pipe.create_pipe(pipe.name, pipe.sql)
pipe_json = create_pipe_response.json()

node = pipe.nodes[0]
# tinybird_pipe.enable_node()
tinybird_pipe.append_node(pipe_name=pipe.name, node_name=node.name)
