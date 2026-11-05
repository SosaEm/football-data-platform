with agg as (
    select
        competition_code,
        team_id,
        team,
        count(*)                                  as played,
        count(*) filter (where points = 3)        as won,
        count(*) filter (where points = 1)        as drawn,
        count(*) filter (where points = 0)        as lost,
        sum(goals_for)                            as goals_for,
        sum(goals_against)                        as goals_against,
        sum(goals_for - goals_against)            as goal_difference,
        sum(points)                               as points
    from {{ ref('int_team_matches') }}
    where is_table_stage
    group by 1, 2, 3
)

select
    *,
    rank() over (
        partition by competition_code
        order by points desc, goal_difference desc, goals_for desc
    ) as position
from agg