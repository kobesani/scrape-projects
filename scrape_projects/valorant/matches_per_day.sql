%
select toDate(start_timestamp) match_date, count() matches_played from valorant_results_select_all_0
    where start_timestamp >= toDateTime({{DateTime(start_date, default='2021-11-03 00:00:00')}}) and
          start_timestamp <= toDateTime({{DateTime(end_date, default='2021-11-05 00:00:00')}})
    group by match_date
