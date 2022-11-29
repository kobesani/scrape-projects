import datetime
from pydantic import BaseModel



class DateRange(BaseModel):
    date_begin: datetime.date
    date_end: datetime.date


class NumberMatchesDay(BaseModel):
    match_date: datetime.date
    matches_played: int
