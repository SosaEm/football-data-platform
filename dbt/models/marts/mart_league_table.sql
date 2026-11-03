with finished as (
    select *
    from {{ ref('stg_matches') }}
    where status = 'FINISHED'
      and stage = 'REGULAR_SEASON'
),

results as (
    select competition_code, home_team_id as team_id, home_team as team,
           home_goals as goals_for, away_goals as goals_against
    from finished
    union all
    select competition_code, away_team_id, away_team,
           away_goals, home_goals
    from finished
),

aggregated as (
    select
        competition_code,
        team_id,
        team,
        count(*)                                           as played,
        count(*) filter (where goals_for > goals_against)  as won,
        count(*) filter (where goals_for = goals_against)  as drawn,
        count(*) filter (where goals_for < goals_against)  as lost,
        sum(goals_for)                                     as goals_for,
        sum(goals_against)                                 as goals_against,
        sum(goals_for - goals_against)                     as goal_difference,
        sum(case when goals_for > goals_against then 3
                 when goals_for = goals_against then 1
                 else 0 end)                               as points
    from results
    group by 1, 2, 3
)

select
    *,
    rank() over (
        partition by competition_code
        order by points desc, goal_difference desc, goals_for desc
    ) as position
from aggregated