import parsel
import pendulum
import requests
import uplink
import yaml

from dataclasses import dataclass, asdict
from loguru import logger
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
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


class ValorantMatches:
    team_result_order: Tuple[str] = (
        "team_name",
        "team_result",
        "team_score",
        "team_ct_score",
        "team_t_score",
        "attack_start",
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
        self.selectors = self.config.selector_configs

    def scrape_match_page(self, match_id: int, match_stub: str):
        response = self.consumer.get_match(match_id=match_id, match_stub=match_stub)
        main_selector = parsel.Selector(response.text)

        match_data = {"match_id": match_id} | {
            x: y.get(main_selector, process_text=True)
            for x, y in self.leaf_selectors.items()
            if y.parent is None and y.children is None
        }

        team_ids = [int(x.split("/")[2]) for x in match_data["team_id"]]

        game_ids = [
            int(x)
            for x in self.selectors["games_with_data"].get(main_selector).getall()
        ]

        match_data["games"] = [
            self.scrape_data_from_game(main_selector, match_id, game_id, team_ids)
            for game_id in game_ids
        ]

        return match_data

    def scrape_data_from_game(
        self,
        parent_selector: parsel.Selector,
        match_id: int,
        game_id: int,
        team_ids: Tuple[int, int],
    ):
        game_selector = parent_selector.xpath(
            f"//div[contains(@class, 'vm-stats-game ') and @data-game-id = '{game_id}']"
        )

        teams_selector = self.selectors["teams"].get(game_selector)
        teams_data = {
            attribute: selector.get(teams_selector, process_text=True)
            for attribute, selector in self.leaf_selectors.items()
            if selector.parent == "teams"
        }

        team_results = [
            TeamResult(match_id, game_id, team_id, *data)
            for team_id, data in zip(
                team_ids, zip(*[teams_data[x] for x in self.team_result_order])
            )
        ]

        players_data = {
            attribute: selector.get(game_selector, process_text=True)
            for attribute, selector in self.leaf_selectors.items()
            if selector.parent == "games"
        }

        return {"team_results": [x.export for x in team_results]} | players_data


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


@dataclass
class TeamResult:
    match_id: int
    game_id: int
    team_id: int
    team_name: str
    _result: str
    _score: str
    _defense_score: str
    _attack_score: str
    _start_side: str

    @property
    def result(self) -> int:
        return 1 if "mod-win" in self._result else 0

    @property
    def score(self) -> int:
        return int(self._score)

    @property
    def attack_score(self) -> int:
        return int(self._attack_score)

    @property
    def defense_score(self) -> int:
        return int(self._defense_score)

    @property
    def start_side(self) -> Literal["attack", "defense"]:
        return "attack" if "mod-ct" in self._start_side else "defense"

    @property
    def export_keys(self) -> List[str]:
        return [
            "match_id",
            "game_id",
            "team_id",
            "team_name",
        ]

    @property
    def export(self) -> Dict[str, Any]:
        return {
            "result": self.result,
            "score": self.score,
            "defense_score": self.defense_score,
            "attack_score": self.attack_score,
            "start_side": self.start_side,
        } | {key: self.__dict__[key] for key in self.export_keys}


@dataclass
class PlayerResult:
    match_id: int
    game_id: int
    team_id: int
    player_id: int
    player_name: str
    agent: str
    _kills: str
    _deaths: str
    _assists: str
    _first_bloods: str
    _first_deaths: str
    _acs: str
    _kast: str
    _adr: str
    _hs: str

    def convert_to_int(self, attribute: str) -> int:
        return int(self.__dict__[attribute])

    @property
    def kills(self) -> int:
        return self.convert_to_int("_kills")

    @property
    def deaths(self) -> int:
        return self.convert_to_int("_deaths")

    @property
    def assists(self) -> int:
        return self.convert_to_int("_assists")

    @property
    def first_bloods(self) -> int:
        return self.convert_to_int("_first_bloods")

    @property
    def first_deaths(self) -> int:
        return self.convert_to_int("_first_deaths")

    @property
    def acs(self) -> int:
        return self.convert_to_int("_acs")

    @property
    def kast(self) -> int:
        return int(self._kast[:-1])

    @property
    def adr(self) -> int:
        return self.convert_to_int("_adr")

    @property
    def hs(self) -> int:
        return int(self._hs[:-1])

    def export(self) -> Dict[str, Any]:
        return self.get_properties() | {
            x: y for x, y in asdict(self).items() if not x.startswith("_")
        }

    def get_properties(self) -> Dict[str, Any]:
        properties = {}
        for name in dir(self.__class__):
            obj = getattr(self.__class__, name)
            if isinstance(obj, property):
                properties[name] = obj.__get__(self, self.__class__)
        return properties


@dataclass
class GameMetaData:
    match_id: int
    _blah: int

    @property
    def blah(self) -> int:
        return 2

    def export(self) -> Dict[str, Any]:
        return self.get_properties() | {
            x: y for x, y in asdict(self).items() if not x.startswith("_")
        }

    def get_properties(self) -> Dict[str, Any]:
        properties = {}
        for name in dir(self.__class__):
            obj = getattr(self.__class__, name)
            if isinstance(obj, property):
                properties[name] = obj.__get__(self, self.__class__)
        return properties
