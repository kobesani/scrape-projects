import os
import pendulum
from loguru import logger

from scrape_projects.tinybird import TinyBirdApi
from scrape_projects.valorant import (
    ValorantResults,
    ValorantStatistics,
)

from scrape_projects.valorant.datasources import DATASOURCES

consumer = ValorantStatistics()
scraper = ValorantResults(consumer=consumer)

results = "\n".join(
    [
        result.process_item
        for result in scraper.get_matches_in_timeframe(
            pendulum.now().start_of('day').subtract(days=1).isoformat()
        )
    ]
)

tinybird = TinyBirdApi(os.environ.get("TB_API_TOKEN"))
response = tinybird.append_events(
    name=DATASOURCES["valorant_results"].name, wait=True, data=results
)

resp_json = response.json()

logger.info(f"Uploaded successfully - status code = {response.status_code}")
logger.info(f"Loaded {resp_json['successful_rows']} rows successfully")

if resp_json["quarantined_rows"] != 0:
    logger.warning(
        f"Loaded {resp_json['quarantined_rows']} quarantined, see UI for details"
    )
