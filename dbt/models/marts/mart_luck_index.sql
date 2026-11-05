with ranked as (
    select
        competition_code,
        team_id,
        team,
        played,
        points,
        goal_difference,
        position as table_position,
        rank() over (
            partition by competition_code
            order by goal_difference desc, goals_for desc
        ) as position_by_goal_diff
    from {{ ref('mart_league_table') }}
)

select
    *,
    -- positive: sits higher in the table than its goal difference suggests (lucky)
    position_by_goal_diff - table_position as luck_gap
from ranked