import parsel
import pendulum
import requests
import uplink

from loguru import logger
from typing import List
from scrape_projects.valorant.items import ValorantResultItem, try_pendulum_timestamp

BASE_URL = "https://vlr.gg"

leaf_queries = {
    "start_time": "./div[@class='match-item-time']",
    "status": "./div[@class='match-item-eta']/div[contains(@class, 'ml ')]/div[@class='ml-status']",
    "start_date": "../preceding-sibling::div[@class='wf-label mod-large'][1]",
    "stakes": "./div[contains(@class, 'match-item-event')]/div[@class='match-item-event-series text-of']",
    "event": "./div[@class='match-item-event text-of']/*[not(div[@class='match-item-event-series text-of'])]",
    "player_stats": "./div[@class='match-item-vod']/div[@class='wf-tag mod-big'][2]",
    "map_stats": "./div[@class='match-item-vod']/div[@class='wf-tag mod-big'][1]",
}


class ValorantStatistics(uplink.Consumer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(base_url=BASE_URL, *args, **kwargs)

    @uplink.get("/matches/results")
    def get_results(self, page: uplink.Query("page", type=int)) -> requests.Response:
        pass

    @uplink.get("/{match_id}/{match_stub}")
    def get_match(
        self,
        match_id: uplink.Path("match_id", type=int),
        match_stub: uplink.Path("match_stub", type=str),
    ) -> requests.Response:
        pass


class ValorantResults:
    def __init__(self, consumer: uplink.Consumer = ValorantStatistics()) -> None:
        self.consumer = consumer

    def scrape_results_page(self, page: int) -> List[ValorantResultItem]:
        response = self.consumer.get_results(page=page)
        main_selector = parsel.Selector(text=response.text)
        cards = main_selector.xpath("//div[@class='wf-card']")
        dates = (
            main_selector.xpath("//div[@class='wf-label mod-large']")
            .xpath("normalize-space(./text())")
            .getall()
        )

        matches = []
        for date, card in zip(dates, cards):
            for match in card.xpath(
                "./a[contains(@class, 'wf-module-item match-item')]"
            ):
                matches.append(
                    ValorantResultItem(
                        **(
                            {"start_date": date, "link": match.xpath("@href").get()}
                            | {
                                leaf: match.xpath(query)
                                .xpath("normalize-space(./text())")
                                .get()
                                for leaf, query in leaf_queries.items()
                            }
                        )
                    )
                )

        return matches

    def get_matches_in_timeframe(
        self, timestamp_isoformat: str
    ) -> List[ValorantResultItem]:
        end_interval = pendulum.parse(timestamp_isoformat).in_tz(
            pendulum.timezone("UTC")
        )
        start_interval = end_interval.subtract(days=1)
        logger.info(
            f"Scraping results between {end_interval.isoformat()} and {start_interval.isoformat()}"
        )
        interval_started = False
        interval_completed = False
        next_page = 1
        matches_in_range = []

        while not (interval_completed):
            logger.info(
                f"Scraping page: https://vlr.gg/matches/results?page={next_page}"
            )
            matches = self.scrape_results_page(next_page)
            timestamps = [
                pendulum.parse(
                    try_pendulum_timestamp(
                        f"{match.start_date} {match.start_time}",
                        "ddd, MMMM DD, YYYY hh:mm A",
                    )
                )
                for match in matches
            ]

            matches_in_range += [
                match
                for timestamp, match in zip(timestamps, matches)
                if timestamp >= start_interval and timestamp < end_interval
            ]

            if not (interval_started):
                interval_started = len(matches_in_range) != 0

            interval_completed = interval_started and (timestamps[-1] < start_interval)

            next_page += 1

        logger.info(f"Scraped {len(matches_in_range)} matches")

        return matches_in_range
