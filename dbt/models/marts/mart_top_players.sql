with latest as (
    select competition_code, max(snapshot_date) as snapshot_date
    from {{ ref('stg_scorers') }}
    group by 1
)

select
    s.competition_code,
    s.player,
    s.nationality,
    s.position,
    s.team,
    date_part('year', age(current_date, s.date_of_birth))::int as age,
    s.played_matches,
    s.goals,
    s.assists,
    s.penalties,
    s.goals + s.assists as goal_contributions,
    round((s.goals + s.assists)::numeric / nullif(s.played_matches, 0), 2) as contributions_per_match,
    rank() over (
        partition by s.competition_code
        order by s.goals + s.assists desc nulls last, s.goals desc
    ) as rank_contributions
from {{ ref('stg_scorers') }} as s
join latest as l
  on l.competition_code = s.competition_code
 and l.snapshot_date = s.snapshot_date