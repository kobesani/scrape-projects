import json
import os
import pendulum
from loguru import logger
from pathlib import Path

# from scrape_projects.tinybird import TinyBirdApi
from scrape_projects.tinybird import ValorantDatasourceApi, TinyBirdApi
from scrape_projects.valorant import (
    ValorantMatches,
    ValorantStatistics,
)

from scrape_projects.valorant.datasources import (
    VALORANT_RESULTS_DATASOURCE,
    VALORANT_MATCH_PLAYER_RESULTS,
    VALORANT_MATCH_TEAM_RESULTS,
)


def flatten(l: list):
    return [item for sublist in l for item in sublist]


consumer = ValorantStatistics()
# scraper = ValorantResults(consumer=consumer)
scraper = ValorantMatches(
    config_path=Path(__file__).parent
    / "scrape_projects"
    / "valorant"
    / "configs"
    / "vlr-gg-matches.yml",
    consumer=consumer,
)

tinybird = ValorantDatasourceApi(os.environ.get("TB_API_TOKEN"))
utc_tz = pendulum.timezone("UTC")
end_day = pendulum.now().start_of("day").subtract(days=2)
end_day_utc = end_day.in_tz(utc_tz).add(seconds=end_day.offset)
start_day_utc = end_day_utc.subtract(days=1)

matches_to_scrape = tinybird.query_matches_played(
    start_date=start_day_utc.to_datetime_string(),
    end_date=end_day_utc.to_datetime_string(),
)
print(matches_to_scrape)
logger.info(
    f"{len(matches_to_scrape['data'])} retrieved for {start_day_utc.isoformat()} to {end_day_utc.isoformat()}"
)

results = []
for match in matches_to_scrape["data"]:
    if match["map_stats"] and match["player_stats"]:
        logger.info(f"Working on: {match['link']}")
        split_link = match["link"].split("/")
        results.append(
            scraper.scrape_match_page(
                match_id=int(split_link[1]), match_stub=split_link[2]
            )
        )
    else:
        logger.warning(f"No map and/or player stats for {match['link']}")

team_results = []
player_results = []
for result in results:
    for game in result["games"]:
        # team_results.append(game["team_results"][0])
        # team_results.append(game["team_results"][1])
        for team_result in game["team_results"]:
            team_results.append(team_result)

        for player in game["player_results"]:
            player_results.append(player)

team_results_dump = "\n".join([json.dumps(result) for result in team_results])
player_results_dump = "\n".join([json.dumps(result) for result in player_results])

# response = tinybird.append_events(
#     name=VALORANT_RESULTS_DATASOURCE.name, wait=True, data=results
# )

tinybird_append = TinyBirdApi(os.environ.get("TB_API_TOKEN"))

response = tinybird_append.append_events(name=VALORANT_MATCH_PLAYER_RESULTS.name, wait=True, data=player_results_dump)
print(response.json())
response = tinybird_append.append_events(name=VALORANT_MATCH_TEAM_RESULTS.name, wait=True, data=team_results_dump)
print(response.json())

