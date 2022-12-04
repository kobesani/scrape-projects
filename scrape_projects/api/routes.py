import os
import pendulum

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scrape_projects.api.schemas import DateRange, NumberMatchesDay
from scrape_projects.tinybird import ValorantDatasourceApi

UTC_OFFSET = datetime.now(timezone.utc).astimezone().utcoffset() // timedelta(seconds=1)

app = FastAPI(title="Valorant Tracker")
templates_path = Path(__file__).parent / "react-scrapes/build"
templates = Jinja2Templates(directory=templates_path)

app.mount("/static", StaticFiles(directory=templates_path), name="static")


@app.get("/", response_class=FileResponse)
def root():
    return FileResponse(f"{templates_path}/index.html", media_type="text/html")


matches_per_day_consumer = ValorantDatasourceApi(os.environ.get("TB_API_TOKEN"))


@app.post("/valorant/matches-per-day.json")
def matches_per_day(date_range: DateRange) -> List[NumberMatchesDay]:
    date_begin = pendulum.instance(date_range.date_begin).add(seconds=UTC_OFFSET)
    date_end = pendulum.instance(date_range.date_end).add(seconds=UTC_OFFSET)
    response = matches_per_day_consumer.query_matches_played(
        start_date=f"{date_begin.date().isoformat()} 00:00:00",
        end_date=f"{date_end.date().isoformat()} 23:59:59",
    )
    print(response.status_code)
    print(response.json())

    return [NumberMatchesDay(**result) for result in response.json()["data"]]
