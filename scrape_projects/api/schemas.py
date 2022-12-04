import datetime
from pydantic import BaseModel


class DateRange(BaseModel):
    date_begin: datetime.datetime
    date_end: datetime.datetime


class NumberMatchesDay(BaseModel):
    match_date: datetime.date
    matches_played: int
