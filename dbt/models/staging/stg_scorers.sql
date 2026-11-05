select
    competition_code,
    snapshot_date,
    player_id,
    payload -> 'player' ->> 'name'                  as player,
    (payload -> 'player' ->> 'dateOfBirth')::date   as date_of_birth,
    payload -> 'player' ->> 'nationality'           as nationality,
    payload -> 'player' ->> 'position'              as position,
    (payload -> 'team' ->> 'id')::bigint            as team_id,
    payload -> 'team' ->> 'name'                    as team,
    (payload ->> 'playedMatches')::int              as played_matches,
    (payload ->> 'goals')::int                      as goals,
    (payload ->> 'assists')::int                    as assists,
    (payload ->> 'penalties')::int                  as penalties
from {{ source('raw', 'scorers') }}