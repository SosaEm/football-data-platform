with finished as (
    select *
    from {{ ref('stg_matches') }}
    where status = 'FINISHED'
      and home_goals is not null
      and away_goals is not null
),

home as (
    select competition_code, match_id, match_utc, matchday, stage,
           home_team_id as team_id, home_team as team, true as is_home,
           away_team_id as opponent_id, away_team as opponent,
           home_goals as goals_for, away_goals as goals_against
    from finished
),

away as (
    select competition_code, match_id, match_utc, matchday, stage,
           away_team_id, away_team, false,
           home_team_id, home_team,
           away_goals, home_goals
    from finished
)

select
    *,
    stage in ('REGULAR_SEASON', 'LEAGUE_STAGE') as is_table_stage,
    case when goals_for > goals_against then 3
         when goals_for = goals_against then 1
         else 0 end as points
from (select * from home union all select * from away) as t