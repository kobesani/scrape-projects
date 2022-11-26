import os

from scrape_projects.tinybird import TinyBirdApi

# results page schema
schema = (
    "event String `json:$.event`, "
    "map_stats UInt8 `json:$.map_stats`, "
    "player_stats UInt8 `json:$.player_stats`, "
    "stakes String `json:$.stakes`, "
    "status String `json:$.status`, "
    "start_timestamp DateTime `json:$.start_timestamp`, "
    "link String `json:$.link`"
)

data = {
    "format": "ndjson",
    "name": "valorant_results_pages_test",
    "mode": "create",
    "schema": schema,
}

tinybird = TinyBirdApi(os.environ.get("TB_API_TOKEN"))

response = tinybird.create_datasource(**data)

print(response)
