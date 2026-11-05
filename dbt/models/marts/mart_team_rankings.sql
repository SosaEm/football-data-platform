with table_matches as (
    select * from {{ ref('int_team_matches') }} where is_table_stage
),

standings as (
    select competition_code, team_id, position,
           count(*) over (partition by competition_code) as n_teams
    from {{ ref('mart_league_table') }}
),

base as (
    select
        m.competition_code,
        m.team_id,
        m.team,
        count(*)                                                       as played,
        sum(m.points)::numeric / count(*)                              as points_per_game,
        sum(m.goals_for - m.goals_against)::numeric / count(*)         as goal_diff_per_game,
        count(*) filter (where o.position <= o.n_teams / 2.0)          as matches_vs_top_half,
        sum(m.points) filter (where o.position <= o.n_teams / 2.0)     as points_vs_top_half
    from table_matches m
    join standings o
      on o.competition_code = m.competition_code
     and o.team_id = m.opponent_id
    group by 1, 2, 3
)

select
    *,
    points_vs_top_half::numeric / nullif(matches_vs_top_half, 0) as ppg_vs_top_half,
    rank() over (partition by competition_code order by points_per_game desc)    as rank_by_points,
    rank() over (partition by competition_code order by goal_diff_per_game desc) as rank_by_goal_diff,
    rank() over (
        partition by competition_code
        order by points_vs_top_half::numeric / nullif(matches_vs_top_half, 0) desc nulls last
    ) as rank_vs_top_half
from base