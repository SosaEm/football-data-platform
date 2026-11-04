import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

st.set_page_config(page_title="Football Data Platform", layout="wide")


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


@st.cache_data(ttl=300)  # re-query the database at most every 5 minutes
def run_query(sql, params=None):
    return pd.read_sql(text(sql), get_engine(), params=params)


st.title("Football Data Platform")

last_load = run_query("SELECT max(loaded_at) AS last_load FROM raw.matches")
st.caption(f"Data last loaded: {last_load['last_load'][0]}")

competitions = run_query(
    "SELECT DISTINCT competition_code FROM analytics.mart_league_table ORDER BY 1"
)
code = st.selectbox("Competition", competitions["competition_code"])

st.subheader("League table")
table = run_query(
    """
    SELECT position, team, played, won, drawn, lost,
           goals_for, goals_against, goal_difference, points
    FROM analytics.mart_league_table
    WHERE competition_code = :code
    ORDER BY position
    """,
    params={"code": code},
)
st.dataframe(table, hide_index=True)

st.subheader("Upcoming matches")
# TODO (yours): query the matches whose status is still SCHEDULED/TIMED,
# ordered by date, for the selected competition, and show the next 10.