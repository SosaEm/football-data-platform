select
    s.competition_code,
    s.snapshot_date,
    st ->> 'type'                             as table_type,
    (t ->> 'position')::int                   as position,
    (t -> 'team' ->> 'id')::bigint            as team_id,
    t -> 'team' ->> 'name'                    as team,
    (t ->> 'playedGames')::int                as played,
    (t ->> 'won')::int                        as won,
    (t ->> 'draw')::int                       as drawn,
    (t ->> 'lost')::int                       as lost,
    (t ->> 'points')::int                     as points,
    (t ->> 'goalsFor')::int                   as goals_for,
    (t ->> 'goalsAgainst')::int               as goals_against,
    (t ->> 'goalDifference')::int             as goal_difference
from {{ source('raw', 'standings') }} as s,
     jsonb_array_elements(s.payload -> 'standings') as st,
     jsonb_array_elements(st -> 'table') as t