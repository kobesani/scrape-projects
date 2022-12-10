import dataclasses
import datetime
import json
import pendulum

from pendulum.tz.timezone import Timezone
from typing import Any, Dict, List, Literal, Optional


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


def try_pendulum_timestamp(timestamp: str, format: str):
    try:
        return (
            pendulum.from_format(timestamp, format, tz=pendulum.now().tz)
            .astimezone(pendulum.timezone("UTC"))
            .isoformat()
        )
    except ValueError:
        return None


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

    @property
    def process_item(self) -> str:
        data = dataclasses.asdict(self)
        data["player_stats"] = player_stats_process(data.get("player_stats", None))
        data["map_stats"] = map_stats_process(data.get("map_stats", None))
        data["start_timestamp"] = try_pendulum_timestamp(
            f"{data.get('start_date', None)} {data.get('start_time', None)}",
            "ddd, MMMM DD, YYYY hh:mm A",
        )
        fields_to_pop = ["start_date", "start_time", "current_timezone"]
        for field in fields_to_pop:
            data.pop(field)
        return json.dumps(data)


@dataclasses.dataclass
class TeamResult:
    match_id: int
    patch: float
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
            "patch",
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


@dataclasses.dataclass
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
    def kast(self) -> Optional[int]:
        try:
            return int(self._kast[:-1])
        except ValueError:
            return None
        

    @property
    def adr(self) -> int:
        return self.convert_to_int("_adr")

    @property
    def hs(self) -> int:
        return int(self._hs[:-1])

    # @property
    def export(self) -> Dict[str, Any]:
        return self.get_properties() | {
            x: y for x, y in dataclasses.asdict(self).items() if not x.startswith("_")
        }

    def get_properties(self) -> Dict[str, Any]:
        properties = {}
        for name in dir(self.__class__):
            obj = getattr(self.__class__, name)
            if isinstance(obj, property):
                properties[name] = obj.__get__(self, self.__class__)
        return properties


@dataclasses.dataclass
class GameMetaData:
    match_id: int
    _blah: int

    @property
    def blah(self) -> int:
        return 2

    def export(self) -> Dict[str, Any]:
        return self.get_properties() | {
            x: y for x, y in dataclasses.asdict(self).items() if not x.startswith("_")
        }

    def get_properties(self) -> Dict[str, Any]:
        properties = {}
        for name in dir(self.__class__):
            obj = getattr(self.__class__, name)
            if isinstance(obj, property):
                properties[name] = obj.__get__(self, self.__class__)
        return properties
