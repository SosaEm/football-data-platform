select
    match_id,
    competition_code,
    (payload ->> 'utcDate')::timestamptz            as match_utc,
    payload ->> 'status'                            as status,
    (payload ->> 'matchday')::int                   as matchday,
    payload ->> 'stage'                             as stage,
    (payload -> 'homeTeam' ->> 'id')::bigint        as home_team_id,
    payload -> 'homeTeam' ->> 'name'                as home_team,
    (payload -> 'awayTeam' ->> 'id')::bigint        as away_team_id,
    payload -> 'awayTeam' ->> 'name'                as away_team,
    payload -> 'score' ->> 'winner'                 as winner,
    (payload -> 'score' -> 'fullTime' ->> 'home')::int as home_goals,
    (payload -> 'score' -> 'fullTime' ->> 'away')::int as away_goals,
    loaded_at
from {{ source('raw', 'matches') }}