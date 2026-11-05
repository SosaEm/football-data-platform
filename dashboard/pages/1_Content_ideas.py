import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

st.set_page_config(page_title="Content ideas", layout="wide")


@st.cache_resource
def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
    )
    return create_engine(url)


@st.cache_data(ttl=300)
def run_query(sql, params=None):
    return pd.read_sql(text(sql), get_engine(), params=params)


st.title("Content ideas for Shorts")
st.caption("Data: football-data.org. Always state the criterion on screen.")

codes = run_query("SELECT DISTINCT competition_code FROM analytics.mart_team_rankings ORDER BY 1")
code = st.selectbox("Competition", codes["competition_code"])
min_played = st.slider("Minimum matches played", 1, 38, 8)
params = {"code": code, "min_played": min_played}

tab_rank, tab_luck, tab_form, tab_players = st.tabs(
    ["Best team (3 criteria)", "Lucky / unlucky", "Rising / falling", "Top players"]
)

with tab_rank:
    df = run_query(
        """
        SELECT team, played,
               round(points_per_game, 2)   AS points_per_game,
               round(goal_diff_per_game, 2) AS goal_diff_per_game,
               round(ppg_vs_top_half, 2)   AS ppg_vs_top_half,
               rank_by_points, rank_by_goal_diff, rank_vs_top_half
        FROM analytics.mart_team_rankings
        WHERE competition_code = :code AND played >= :min_played
        ORDER BY rank_by_points
        """,
        params,
    )
    for label, col in [("Points per game", "rank_by_points"),
                       ("Goal difference per game", "rank_by_goal_diff"),
                       ("Points vs top-half teams", "rank_vs_top_half")]:
        leaders = df.loc[df[col] == 1, "team"].tolist()
        st.write(f"**{label}:** {', '.join(leaders) if leaders else '-'}")
    st.dataframe(df, hide_index=True)
    st.download_button("Download CSV", df.to_csv(index=False), f"{code}_team_rankings.csv")

with tab_luck:
    luck = run_query(
        """
        SELECT team, table_position, position_by_goal_diff, luck_gap, points, goal_difference
        FROM analytics.mart_luck_index
        WHERE competition_code = :code AND played >= :min_played
        ORDER BY luck_gap DESC
        """,
        params,
    )
    st.subheader("Luckiest (higher in the table than their goal difference suggests)")
    st.dataframe(luck.head(5), hide_index=True)
    st.subheader("Unluckiest")
    st.dataframe(luck.tail(5).iloc[::-1], hide_index=True)

with tab_form:
    form = run_query(
        """
        SELECT team, played, round(season_ppg, 2) AS season_ppg,
               round(recent_ppg, 2) AS last_6_ppg, round(form_change, 2) AS form_change
        FROM analytics.mart_form_trend
        WHERE competition_code = :code AND played >= :min_played
        ORDER BY form_change DESC
        """,
        params,
    )
    st.subheader("Rising (last 6 matches vs season average)")
    st.dataframe(form.head(5), hide_index=True)
    st.subheader("Falling")
    st.dataframe(form.tail(5).iloc[::-1], hide_index=True)

with tab_players:
    max_age = st.slider("Maximum age (for breakout players)", 16, 45, 45)
    players = run_query(
        """
        SELECT rank_contributions AS rank, player, team, nationality, age,
               played_matches, goals, assists, goal_contributions, contributions_per_match
        FROM analytics.mart_top_players
        WHERE competition_code = :code AND (age IS NULL OR age <= :max_age)
        ORDER BY rank_contributions
        LIMIT 20
        """,
        {"code": code, "max_age": max_age},
    )
    if players.empty:
        st.info("No scorer data for this competition (it may not be included in your API plan).")
    else:
        st.caption("Ranked among the league's top scorers only; assists may be incomplete.")
        st.dataframe(players, hide_index=True)
        st.download_button("Download CSV", players.to_csv(index=False), f"{code}_top_players.csv")