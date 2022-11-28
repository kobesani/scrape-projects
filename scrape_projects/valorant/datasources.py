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
    pipes: Optional[List[Pipe]]


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
