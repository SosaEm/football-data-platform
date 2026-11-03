select *
from {{ ref('stg_matches') }}
where status = 'FINISHED'
  and (home_goals is null or away_goals is null)