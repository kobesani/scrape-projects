import uplink

from uplink import Body, Consumer, Query, get, post, put, returns
from uplink.auth import BearerToken


class TinyBirdApi(Consumer):
    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(
            base_url="https://api.tinybird.co/",
            auth=BearerToken(token=token),
            *args,
            **kwargs
        )

    @returns.json
    @post("/v0/datasources")
    def create_datasource(
        self,
        format: Query(name="format", type=str),
        name: Query(name="name", type=str),
        mode: Query(name="mode", type=str),
        schema: Query(name="schema", type=str),
    ):
        pass

    @returns.json
    @post("/v0/events")
    def append_events(
        self,
        name: Query(name="name", type=str),
        wait: Query(name="wait", type=bool),
        data: Body,
    ):
        pass

    # @delete("/v0/datasources")

    @post("/v0/pipes")
    def create_pipe(
        self, name: Query("name", type=str), sql: Query(name="sql", type=str)
    ):
        pass

    @get("/v0/sql")
    def query_pipe(self, sql: Query(name="q", type=str)):
        pass

    @get("/v0/pipes")
    def get_pipes(self):
        pass

    @put("/v0/pipes/{pipe}/endpoint")
    def enable_node(self, pipe: uplink.Path(name="pipe", type=str), data: Body):
        pass
