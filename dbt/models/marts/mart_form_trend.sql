with ordered as (
    select
        *,
        row_number() over (
            partition by competition_code, team_id
            order by match_utc desc
        ) as recency
    from {{ ref('int_team_matches') }}
    where is_table_stage
),

agg as (
    select
        competition_code,
        team_id,
        team,
        count(*)                                              as played,
        avg(points::numeric)                                  as season_ppg,
        avg(points::numeric) filter (where recency <= 6)      as recent_ppg,
        count(*) filter (where recency <= 6)                  as recent_matches
    from ordered
    group by 1, 2, 3
)

select
    *,
    recent_ppg - season_ppg as form_change  -- positive: improving; negative: declining
from agg