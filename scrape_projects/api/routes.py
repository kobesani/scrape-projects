import os

from typing import List

from fastapi import FastAPI
from fastapi.responses import FileResponse

from scrape_projects.api.schemas import DateRange, NumberMatchesDay
from scrape_projects.tinybird import ValorantDatasourceApi

app = FastAPI(title="Valorant Tracker")

matches_per_day_consumer = ValorantDatasourceApi(os.environ.get("TB_API_TOKEN"))


@app.post("/valorant/matches-per-day")
def matches_per_day(date_range: DateRange) -> List[NumberMatchesDay]:
    response = matches_per_day_consumer.query_matches_played(
        start_date=f"{date_range.date_begin.isoformat()} 00:00:00",
        end_date=f"{date_range.date_end.isoformat()} 00:00:00",
    )

    return [NumberMatchesDay(**result) for result in response.json()["data"]]
