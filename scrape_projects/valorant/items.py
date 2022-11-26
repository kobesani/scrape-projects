import dataclasses
import datetime
import json
import pendulum

from pendulum.tz.timezone import Timezone
from typing import Optional


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

