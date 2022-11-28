import uplink

from uplink import Body, Consumer, Path, Query, get, post, put, returns
from uplink.auth import BearerToken


class DatasourcesApi(Consumer):
    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(
            base_url="https://api.tinybird.co/",
            auth=BearerToken(token=token),
            *args,
            **kwargs
        )

    @returns.json
    @get("/v0/datasources")
    def get_datasources(self):
        """
        returns all datasources as a json object
        """
        pass

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

    @post("/v0/events")
    def append_datasource(
        self,
        name: Query(name="name", type=str),
        wait: Query(name="wait", type=bool),
        data: Body,
    ):
        """
        Appends events to a datasource as rows, data input format depends
        on the defined datasource format, multiple records should be delimited
        by new lines.
        """
        pass

    @post("/v0/datasources/{name}/truncate")
    def truncate_datasource(self, name: Path(name="name", type=str)):
        pass


class PipeApi(Consumer):
    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(
            base_url="https://api.tinybird.co/",
            auth=BearerToken(token=token),
            *args,
            **kwargs
        )

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

    @returns.json
    @get("/v0/pipes/{name}")
    def get_pipe(self, name: Path(name="name", type=str)):
        pass

    @post("/v0/pipes/{pipe_name}/nodes")
    def append_node(
        self,
        pipe_name: Path(name="pipe_name", type=str),
        node_name: Query(name="name", type=str),
        description: Query(name="description", type=str),
        data: Body(type=str),
    ):
        pass

    @put("/v0/pipes/{pipe}/endpoint")
    def enable_node(self, pipe: uplink.Path(name="pipe", type=str), data: Body):
        """
        Enables a particular transformation for a pipe. This endpoint requires the
        pipe name (param: pipe) and the id of the transformation node for the pipe.
        By default, we enable the original pipe as the transformation node. Only one
        node can be enabled at a time. You can query the pipe to get the ID of the node
        you want to enable via get_pipe or get_pipes method.
        """
        pass


class TinyBirdApi(Consumer):
    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(
            base_url="https://api.tinybird.co/",
            auth=BearerToken(token=token),
            *args,
            **kwargs
        )

    @returns.json
    @get("/v0/datasources")
    def get_datasources(self):
        pass

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

    # @returns.json
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


class ValorantDatasourceApi(Consumer):
    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(
            base_url="https://api.tinybird.co/",
            auth=BearerToken(token=token),
            *args,
            **kwargs
        )

    @returns.json
    @get("/v0/pipes/valorant_results_select_all.json")
    def query_matches_played(
        self,
        start_date: Query(name="start_date", type=str) = "2021-11-03 00:00:00",
        end_date: Query("end_date", type=str) = "2021-11-04 00:00:00",
    ):
        pass

