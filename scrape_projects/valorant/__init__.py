import parsel
import pendulum
import requests
import uplink
import yaml

from dataclasses import dataclass, asdict
from loguru import logger
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from scrape_projects.valorant.items import (
    ValorantResultItem,
    try_pendulum_timestamp,
    TeamResult,
    PlayerResult,
)

BASE_URL = "https://vlr.gg"

stats_table_map = {
    "Rating": "rating",
    "Average Combat Score": "acs",
    "Kills": "kills",
    "Assists": "assists",
    "Kill, Assist, Trade, Survive %": "kast",
    "Average Damage per Round": "adr",
    "Headshot %": "hs",
    "First Kills": "first_bloods",
    "First Deaths": "first_deaths",
}

special_stats_columns = [
    "player_id",
    "player_name",
    "agent",
    "deaths",
    # "first_bloods",
    # "first_deaths",
]

leaf_queries = {
    "start_time": "./div[@class='match-item-time']",
    "status": "./div[@class='match-item-eta']/div[contains(@class, 'ml ')]/div[@class='ml-status']",
    "start_date": "../preceding-sibling::div[@class='wf-label mod-large'][1]",
    "stakes": "./div[contains(@class, 'match-item-event')]/div[@class='match-item-event-series text-of']",
    "event": "./div[@class='match-item-event text-of']/*[not(div[@class='match-item-event-series text-of'])]",
    "player_stats": "./div[@class='match-item-vod']/div[@class='wf-tag mod-big'][2]",
    "map_stats": "./div[@class='match-item-vod']/div[@class='wf-tag mod-big'][1]",
}

player_stats_query = "./div/div/table/tbody/tr/td[{position}]/span/span[contains(@class, 'mod-both')]/text()"


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


class ValorantMatches:
    team_result_order: Tuple[str] = (
        "team_name",
        "team_result",
        "team_score",
        "team_ct_score",
        "team_t_score",
        "attack_start",
    )

    player_result_order: Tuple[str] = (
        "team_id",
        "player_id",
        "player_name",
        "agent",
        "kills",
        "deaths",
        "assists",
        "first_bloods",
        "first_deaths",
        "acs",
        "kast",
        "adr",
        "hs",
    )

    def __init__(
        self,
        config_path: Path = Path(__file__).parent / "configs" / "vlr-gg-matches.yml",
        consumer: uplink.Consumer = ValorantStatistics(),
    ) -> None:
        self.config = ScrapeConfig(config_path=config_path)
        self.consumer: ValorantStatistics = consumer
        self.leaf_selectors = {
            attribute: selector
            for attribute, selector in self.config.selector_configs.items()
            if selector.children is None
        }
        self.selectors: Dict[str, SelectorConfig] = self.config.selector_configs

    def scrape_match_page(self, match_id: int, match_stub: str):
        response = self.consumer.get_match(match_id=match_id, match_stub=match_stub)
        main_selector = parsel.Selector(response.text)

        match_data = {"match_id": match_id} | {
            x: y.get(main_selector, process_text=True)
            for x, y in self.leaf_selectors.items()
            if y.parent is None and y.children is None
        }

        match_data["patch"] = (
            self.leaf_selectors["patch"]
            .get(main_selector)
            .xpath("normalize-space(text()[1])")
            .getall()
        )

        if len(match_data["patch_old"]) != 0:
            match_data["patch"] = match_data["patch_old"]

        match_data.pop("patch_old")

        patch = float(match_data["patch"][0].split()[-1])

        team_ids = [int(x.split("/")[2]) for x in match_data["team_id"]]

        game_ids = [
            int(x)
            for x in self.selectors["games_with_data"].get(main_selector).getall()
        ]

        match_data["games"] = [
            self.scrape_data_from_game(
                main_selector, match_id, game_id, team_ids, patch
            )
            for game_id in game_ids
        ]

        return match_data

    def scrape_data_from_game(
        self,
        parent_selector: parsel.Selector,
        match_id: int,
        game_id: int,
        team_ids: Tuple[int, int],
        patch: float,
    ):
        game_selector = parent_selector.xpath(
            f"//div[contains(@class, 'vm-stats-game ') and @data-game-id = '{game_id}']"
        )

        box_score_header = self.selectors["stats_table_header"].get(
            game_selector, process_text=True
        )
        # enumerate starts from 2 because the first column (player) doesn't have a header
        # and position is 1-based
        positions = {
            stats_table_map.get(y): x
            for (x, y) in enumerate(box_score_header, start=2)
            if stats_table_map.get(y) is not None
        }

        teams_selector = self.selectors["teams"].get(game_selector)
        teams_data = {
            attribute: selector.get(teams_selector, process_text=True)
            for attribute, selector in self.leaf_selectors.items()
            if selector.parent == "teams"
        }

        team_results = [
            TeamResult(match_id, patch, game_id, team_id, *data)
            for team_id, data in zip(
                team_ids, zip(*[teams_data[x] for x in self.team_result_order])
            )
        ]

        players_data = {
            attribute: game_selector.xpath(
                player_stats_query.format(position=positions.get(attribute))
            ).getall()
            for attribute, selector in self.leaf_selectors.items()
            if positions.get(attribute) is not None
            # if selector.parent == "games" and selector.attribute != "stats_table_header"
        }

        players_data |= {
            attribute: self.leaf_selectors[attribute].get(
                game_selector, process_text=True
            )
            for attribute in special_stats_columns
        }

        players_data["team_id"] = [team_ids[0]] * 5 + [team_ids[1]] * 5
        players_data["player_id"] = [
            int(player_id.split("/")[2]) for player_id in players_data["player_id"]
        ]

        player_results = [
            PlayerResult(match_id, game_id, *data)
            for data in zip(*[players_data[x] for x in self.player_result_order])
        ]

        return {
            "team_results": [x.export for x in team_results],
            "player_results": [x.export() for x in player_results],
        }


@dataclass
class SelectorConfig:
    attribute: str
    query: str
    query_type: str = "xpath"
    text_processing: Optional[Literal["raw", "normalized", "direct"]] = None
    count: Optional[int] = None
    parent: Optional[str] = None
    children: Optional[List[str]] = None

    def get(
        self,
        parent: Union[parsel.Selector, parsel.SelectorList],
        process_text: bool = False,
    ) -> List[str]:
        selector = getattr(parent, self.query_type)(self.query)
        if not process_text:
            return selector

        match self.text_processing:
            case "raw":
                return selector.xpath("./text()").getall()
            case "normalized":
                return selector.xpath("normalize-space(./text())").getall()
            case "direct":
                return selector.getall()
            case other:
                return selector

    def validate(self, result: List[str]) -> bool:
        if not self.count:
            logger.warning(
                f"Validation not possible because self.count = None -> validation is always passing"
            )
            return True

        return len(result) % self.count == 0


class ScrapeConfig:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        with config_path.open(mode="r") as config_file:
            parsed_yaml = yaml.safe_load(config_file)

        self.base_url = parsed_yaml["base_url"]
        self.selector_configs = {
            selector["attribute"]: SelectorConfig(**selector)
            for selector in parsed_yaml["selectors"]
        }
