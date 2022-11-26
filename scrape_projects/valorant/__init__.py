import dataclasses
import datetime
import parsel
import pendulum
import requests
import uplink

from pendulum.tz.timezone import Timezone
from typing import Optional, Tuple

BASE_URL = "https://vlr.gg"


def player_stats_process(value: Optional[str]) -> Optional[str]:
    return True if value == "Player" else False


def map_stats_process(value: Optional[str]) -> Optional[str]:
    return True if value == "Map" else False


def link_process(value: Optional[str]) -> Optional[str]:
    return value


def start_date_process(value: Optional[datetime.date]) -> Optional[datetime.date]:
    return value


def start_time_process(value: Optional[datetime.time]) -> Optional[datetime.time]:
    return value


def stakes_process(value: Optional[str]) -> Optional[str]:
    return value


def event_process(value: Optional[str]) -> Optional[str]:
    return value


def status_process(value: Optional[str]) -> Optional[str]:
    return value


def current_timezone_process(value: Optional[Timezone]) -> Optional[Timezone]:
    return value


@dataclasses.dataclass
class ValorantResultItem:
    link: Optional[str] = dataclasses.field(default=None)
    start_date: Optional[datetime.date] = dataclasses.field(default=None)
    start_time: Optional[datetime.time] = dataclasses.field(default=None)
    player_stats: bool = dataclasses.field(default=False)
    map_stats: bool = dataclasses.field(default=False)
    stakes: Optional[str] = dataclasses.field(default=None)
    status: Optional[str] = dataclasses.field(default=None)
    event: Optional[str] = dataclasses.field(default=None)
    current_timezone: Timezone = dataclasses.field(default=pendulum.now().tz)


parent_queries = {
    "cards": "//div[@class='wf-card']",
    "matches": "./a[contains(@class, 'wf-module-item match-item')]",
}

leaf_queries = {
    "start_time": "./div[@class='match-item-time']",
    "status": "./div[@class='match-item-eta']/div[contains(@class, 'ml ')]/div[@class='ml-status']",
    "start_date": "../preceding-sibling::div[@class='wf-label mod-large'][1]",
    "stakes": "./div[contains(@class, 'match-item-event')]/div[@class='match-item-event-series text-of']",
    "event": "./div[@class='match-item-event text-of']/*[not(div[@class='match-item-event-series text-of'])]",
    "player_stats": "./div[@class='match-item-vod']/div[@class='wf-tag mod-big'][2]",
    "map_stats": "./div[@class='match-item-vod']/div[@class='wf-tag mod-big'][1]",
}


class ValorantResults(uplink.Consumer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(base_url=BASE_URL, *args, **kwargs)

    @uplink.get("/matches/results")
    def get_results(self, page: uplink.Query("page", type=int)) -> requests.Response:
        pass

    def scrape_results_page(self, page: int):
        response = self.get_results(page=page)
        main_selector = parsel.Selector(text=response.text)


#     def scrape_results_in_page_range(self, start: int = 1, end: int = 1):
#         results = []
#         for page in range(start, end + 1):
#             print(f"Scraping page {page}")
#             results += self.scrape_single_results_page(page)

#         return results

#     def scrape_single_results_page(self, page_number: int):
#         data = self.scrape_endpoint("get_results_page", page_number)
#         data["start_timestamp"] = [
#             try_pendulum_timestamp(f"{d} {t}", "ddd, MMMM DD, YYYY hh:mm A")
#             for d, t in zip(data["start_date"], data["start_time"])
#         ]
#         data["player_stats"] = [
#             True if x == "Player" else False for x in data["player_stats"]
#         ]
#         data["map_stats"] = [True if x == "Map" else False for x in data["map_stats"]]
#         data.pop("start_date", None)
#         data.pop("start_time", None)
#         return [
#             {attribute: value for attribute, value in zip(data.keys(), row)}
#             for row in zip(*data.values())
#         ]

#     def get_matches_in_timeframe(self, timestamp_isoformat: str) -> List[ResultData]:
#         end_interval = pendulum.parse(timestamp_isoformat).in_tz(
#             pendulum.timezone("UTC")
#         )
#         start_interval = end_interval.subtract(days=1)
#         interval_started = False
#         interval_completed = False
#         next_page = 1
#         matches_in_range = []

#         while not (interval_completed):
#             print(f"Starting parsing page={next_page}")
#             matches = self.scrape_single_results_page(next_page)

#             matches_in_range += filter(
#                 lambda x: x["start_timestamp"] >= start_interval
#                 and x["start_timestamp"] < end_interval,
#                 matches,
#             )

#             if not (interval_started):
#                 interval_started = len(matches_in_range) != 0

#             interval_completed = interval_started and (
#                 matches[-1]["start_timestamp"] < start_interval
#             )

#             next_page += 1

#         return matches_in_range
