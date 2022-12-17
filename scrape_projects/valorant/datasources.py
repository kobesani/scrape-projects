import dataclasses

from typing import List, Optional


@dataclasses.dataclass
class Node:
    datasource_name: str
    pipe_name: str
    name: str
    sql: str


@dataclasses.dataclass
class Pipe:
    datasource_name: str
    name: str
    sql: str
    nodes: Optional[List[Node]]


@dataclasses.dataclass
class Datasource:
    name: str
    format: str
    mode: str
    schema: str
    pipes: Optional[List[Pipe]] = None


VALORANT_RESULTS_DATASOURCE = Datasource(
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
    pipes=[
        Pipe(
            datasource_name="valorant_results",
            name="valorant_results_select_all",
            sql="select * from valorant_results",
            nodes=[
                Node(
                    datasource_name="valorant_results",
                    pipe_name="valorant_results_select_all",
                    name="matches_played_per_day",
                    sql=(
                        "select toDate(start_timestamp) match_date, count() matches_played "
                        "from valorant_results_select_all group by date"
                    ),
                )
            ],
        )
    ],
)

VALORANT_MATCH_TEAM_RESULTS = Datasource(
    name="valorant_team_results",
    format="ndjson",
    mode="create",
    schema=(
        "match_id UInt32 `json:$.match_id`, "
        "patch Float32 `json:$.patch`, "
        "game_id UInt32 `json:$.game_id`, "
        "team_id UInt32 `json:$.team_id`, "
        "team_name String `json:$.team_name`, "
        "result UInt8 `json:$.result`, "
        "score UInt8 `json:$.score`, "
        "attack_score UInt8 `json:$.attack_score`, "
        "defense_score UInt8 `json:$.defense_score`, "
        "start_side UInt8 `json:$.start_side`"
    ),
    # engine="MergeTree",
    # engine_sorting_key="match_id, game_id, patch, team_id"
)

VALORANT_MATCH_PLAYER_RESULTS = Datasource(
    name="valorant_player_results",
    format="ndjson",
    mode="create",
    schema=(
        "match_id UInt32 `json:$.match_id`, "
        "game_id UInt32 `json:$.game_id`, "
        "team_id UInt32 `json:$.team_id`, "
        "player_id UInt32 `json:$.player_id`, "
        "player_name String `json:$.player_name`, "
        "agent String `json:$.agent`, "
        "kills UInt8 `json:$.kills`, "
        "deaths UInt8 `json:$.deaths`, "
        "assists UInt8 `json:$.assists`, "
        "first_bloods UInt8 `json:$.first_bloods`, "
        "first_deaths UInt8 `json:$.first_deaths`, "
        "acs UInt32 `json:$.acs`, "
        "kast UInt8 `json:$.kast`, "
        "adr UInt32 `json:$.adr`, "
        "hs UInt8 `json:$.hs`"
    )
)

# DATASOURCES = {
#     "valorant_results": Datasource(
#         name="valorant_results",
#         format="ndjson",
#         mode="create",
#         schema=(
#             "event String `json:$.event`, "
#             "map_stats UInt8 `json:$.map_stats`, "
#             "player_stats UInt8 `json:$.player_stats`, "
#             "stakes String `json:$.stakes`, "
#             "status String `json:$.status`, "
#             "start_timestamp DateTime `json:$.start_timestamp`, "
#             "link String `json:$.link`"
#         ),
#     )
# }
# # results = tb.create_pipe("valorant_results_select_all", "select * from valorant_results_pages")
# PIPES = {
#     "valorant_results": Pipe(
#         datasource_name=DATASOURCES["valorant_results"].name,
#         name="valorant_results_select_all",
#         sql="select * from valorant_results",
#     )
# }


# NODES = {
#     "valorant_results": Node(
#         datasource_name=DATASOURCES["valorant_results"].name,
#         pipe_name=PIPES["valorant_results"].name,
#         name="matches_played_per_day",
#         sql=(
#             "select toDate(start_timestamp) match_date, count() matches_played "
#             "from valorant_results_select_all group by date"
#         ),
#     )
# }
