{{ config(severity='warn') }}

with latest as (
    select competition_code, max(snapshot_date) as snapshot_date
    from {{ ref('stg_standings') }}
    group by 1
),

api as (
    select s.competition_code, s.team_id, s.points, s.played, s.goal_difference
    from {{ ref('stg_standings') }} s
    join latest l using (competition_code, snapshot_date)
    where s.table_type = 'TOTAL'
)

select
    m.competition_code,
    m.team,
    m.points as mart_points,
    a.points as api_points
from {{ ref('mart_league_table') }} m
join api a using (competition_code, team_id)
where m.points <> a.points
   or m.played <> a.played
   or m.goal_difference <> a.goal_difference