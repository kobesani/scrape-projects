import dataclasses


@dataclasses.dataclass
class Datasource:
    name: str
    format: str
    mode: str
    schema: str


DATASOURCES = {
    "valorant_results": Datasource(
        name="valorant_results",
        format="ndjson",
        mode="create",
        schema=(
            "event String `json:$.event`, "
            "map_stats UInt8 `json:$.map_stats`, "
            "player_stats UInt8 `json:$.player_stats`, "
            "stakes String `json:$.stakes`, "
            "status String `json:$.status`, "
            "start_timestamp DateTime `json:$.start_timestamp`, "
            "link String `json:$.link`"
        ),
    )
}
