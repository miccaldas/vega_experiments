"""
Most of what's in here is trash but, as it's always
the case, in my way to defeat, I found some interesting
stuff that's worth remembering.
"""
import json
import os
import pickle

import jinja2
import pandas as pd
import snoop
from dotenv import load_dotenv
from mysql.connector import Error, connect
from sklearn import linear_model
from snoop import pp


def type_watch(source, value):
    return f"type({source})", type(value)


snoop.install(watch_extras=[type_watch])

load_dotenv()
binaries = os.getenv("BINARIES")
dfs = os.getenv("DATAFRAMES")
pages = os.getenv("PAGES")


@snoop
def db_data(query):
    """
    Collects db data.
    """
    try:
        conn = connect(
            host="localhost",
            user="mic",
            password="xxxx",
            database="notes",
            use_pure=True,
        )
        cur = conn.cursor(buffered=True)
        cur.execute(query)
        timedf = cur.fetchall()
    except Error as e:
        print("Error while connecting to db", e)
    finally:
        if conn:
            conn.close()

    return timedf


@snoop
def db_dump():
    """
    The following function needs a db call and some
    data wrangling. We put it here and make it
    available as a pickle file, so as not to keep
    repeating long operations.
    """
    with open(f"{binaries}tagtups.bin", "rb") as f:
        tagtups = pickle.load(f)

    query = "SELECT ntid, title, time FROM notes"
    dbdata = db_data(query)
    with open(f"{binaries}dbhourvalue.bin", "wb") as g:
        pickle.dump(dbdata, g)

    tag_data = [
        (
            d[0],
            d[1],
            t[0][0],
            t[0][1],
            d[2],
        )
        for d in dbdata
        for t in tagtups
        if d[0] == t[1]
    ]

    with open(f"{binaries}tgdt.bin", "wb") as f:
        pickle.dump(tag_data, f)


def db_dump_dict():
    """
    Turns the list created by the last function to
    a dictionary.
    """
    with open(f"{binaries}tgdt.bin", "rb") as f:
        tgdict = pickle.load(f)

    tdict = [{"ntid": i[0], "title": i[1], "tag": i[2], "score": i[3], "time": i[4]} for i in tgdict]

    with open(f"{binaries}tdict.bin", "wb") as f:
        pickle.dump(tdict, f)


@snoop
def hour_value_comparison():
    """
    Check if the hour that a tag is created affects its value.
    """
    with open(f"{binaries}tdict.bin", "rb") as g:
        tgdt = pickle.load(g)

    tg = pd.DataFrame(tgdt)
    # This method of creating hourly intervals, creates a scale of
    # 24 hours. Unlike the 'to_period' method, who creates hourly
    # intervals in a week, month, year...
    tg["hour"] = tg["time"].dt.hour
    tg["hour"] = tg["hour"].astype("int")

    tagrank = tg[["tag", "score", "hour", "time"]].copy()
    rnktghr = tagrank.groupby(["tag", "hour"]).median().reset_index(drop=False)
    rnkhr = tagrank.groupby(["score"]).median().reset_index(drop=False)

    pd.set_option("display.max_rows", None)
    print(rnktghr.sort_values(by=["score"]))

    # Creates a series with the frequence of the tags.
    tsize = tagrank.groupby(["tag"]).size()

    tm = pd.DataFrame(tgdt)
    tm["month"] = tm["time"].dt.to_period("M")
    trk = tm[["tag", "score", "month"]].copy()
    trkm = trk.groupby(["score", "month"]).median().reset_index(drop=False)
    trkm["intmonth"] = trkm["month"].astype("int")

    # We turned 'month' to string because it wouldn't serialize to json otherwise.
    trkst = trkm[["score", "month"]].copy()
    trkst["month"] = trkst["month"].astype("str")

    lin = linear_model.LinearRegression()
    lin.fit(trkm[["score"]], trkm["intmonth"])
    print(lin.score(trkm[["score"]], trkm["intmonth"]))

    trkdict = trkst.to_dict("records")
    with open("trk.json", "w") as f:
        json.dump(trkdict, f)


@snoop
def main():
    """
    Calls all other functions.
    """
    # db_dump()
    # db_dump_dict()
    hour_value_comparison()


if __name__ == "__main__":
    main()
