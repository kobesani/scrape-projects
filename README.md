# Scrape Projects

Each project corresponds to a series of requests (via the uplink python modules), HTML page scrapes and data pushes to TinyBird via a scheduled Github Action.

## Valorant Results

This project currently scrapes https://vlr.gg/matches/results?page={page_number}
to get basic information about matches played on a daily basis at the higher
levels of valorant competition (i.e. teams good enough to be tracked by the
community). There is a day lag and the github action is currently scheduled to
run around 16-ish UTC time and pulls matches from the previous day (00:01 -
00:00, 12:01 AM - 12:00 AM).
