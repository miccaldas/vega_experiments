"""
Module related to visualizing some of the information gleaned
from 'similarity_analysis'.
"""
import json
import os
import pickle

import jinja2
import pandas as pd
import snoop
from dotenv import load_dotenv
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
def create_dataframe():
    """
    Unpickles 'tagdata' and 'notedata' and
    converts them to dataframe.
    """

    with open(f"{binaries}tagdata.bin", "rb") as f:
        vtag = pickle.load(f)
    vt = pd.DataFrame(vtag)
    with open(f"{dfs}vt.bin", "wb") as g:
        pickle.dump(vt, g)

    with open(f"{binaries}notedata.bin", "rb") as h:
        vnote = pickle.load(h)
    vn = pd.DataFrame(vnote)
    with open(f"{dfs}vn.bin", "wb") as i:
        pickle.dump(vn, i)


@snoop
def note_visualization():
    """
    From the data in 'vn', we'll analyze to see
    what we can visualize with Vega-lite.
    """
    with open(f"{dfs}vn.bin", "rb") as f:
        vn = pickle.load(f)

    pd.set_option("display.max_rows", None)

    bad = vn.query("score > 100")
    badsort = bad.sort_values(by=["score"])
    with open(f"{dfs}badnotes.bin", "wb") as g:
        pickle.dump(badsort, g)

    good = vn.query("score == 0")

    print(len(good))
    print(len(bad))


@snoop
def tag_visualization(ltags):
    """
    Data analysis of 'vt'.
    """
    with open(f"{dfs}vt.bin", "rb") as f:
        vt = pickle.load(f)

    pd.set_option("display.max_rows", None)

    tgview = vt[vt["tag"].isin(ltags)]
    return tgview


@snoop
def jinjadata():
    """
    Data that'll be passed to Jinja2, for it
    to create a html page with our data.
    """
    graphdata = tag_visualization()
    pages = os.getenv("PAGES")

    # In Vega-lite, the 'True' boolean is written with a small 't'. As Python
    # won't accept this, I found this work-around.
    true = "true"

    template_loader = jinja2.FileSystemLoader(searchpath="./templates/")
    template_env = jinja2.Environment(loader=template_loader, lstrip_blocks=True, trim_blocks=True)
    template_file = "base.tpl"
    template = template_env.get_template(template_file)
    output_text = template.render(
        title="tag fitness score",
        description="How well a tag describes the text of the note.",
        page_url="http://localhost/vega_experiments/pages/tagscore.html",
        graphic_title="Tag Fitness Score",
        project="vega_experiments",
        mark={"type": "point", "filled": true},
        config={"point": {"size": 100}},
        width=800,
        height=400,
        dictdata=graphdata,
        xfield={"field": "time", "type": "temporal"},
        # I reversed the 'y' axis scale to make it more obvious that a smaller value is
        # preferable that a large one.
        yfield={"field": "value", "type": "quantitative", "scale": {"reverse": true}},
        color={"field": "tag", "type": "nominal"},
    )
    html_path = f"{pages}test1.html"
    html_file = open(html_path, "w")
    html_file.write(output_text)
    html_file.close()


@snoop
def linear_regression():
    """
    Data for a linear regression analysis between
    two tags. Now in json format.
    """
    # Defines the tags that we want to select from 'vt'.
    ltags = ["python", "mysql"]
    # Creates dataframe with that selection.
    linreg = tag_visualization(ltags)

    # We're going to build a new dataframe, where the tag values
    # 'python' and 'mysql', will be columns. But this must be done
    # in stages:

    # First we create a new dataframe with the columns we want, minus
    # the column will use to create new columns. 'tag', in this case.
    # As we want a dataframe with the columns:
    # 'title', 'time', 'mysql', 'python', we first get 'ttle', 'time'.
    lr = linreg[["title", "time"]].copy()

    # Then we create the 'mysql' and 'python' columns, for now with
    # dummy data.
    lr["python"] = 0
    lr["mysql"] = 0

    # Now we'll extract data from "'linreg's" 'tag' column to their
    # corresponding columns in 'lr':

    # We'll iterate through 'linreg' in (index, Series) pairs. It
    # returns a Series per each row.
    for index, row in linreg.iterrows():
        # For all 'python' occurrences in vt's 'tag' column:
        if row["tag"] == "python":
            # add the corresponding data in the 'value' column,
            # to "lr's" 'python' column.
            lr.loc[index, "python"] = row["value"]
        # Ditto for 'mysql'.
        if row["tag"] == "mysql":
            lr.loc[index, "mysql"] = row["value"]

    # Convert the dataframe to dictionary, to be used by Vega-lite.
    lrdict = lr.to_dict("records")

    # Convert dictionary to json file.
    with open("lrg.json", "w") as f:
        json.dump(lrdict, f)


@snoop
def tag_ranking():
    """
    We'll take the score values, add them per tag, to see
    what are the tags that are performing better.
    """
    with open(f"{dfs}vt.bin", "rb") as f:
        vt = pickle.load(f)

    tagrank = vt[["tag", "value", "time"]].copy()

    trank = tagrank.groupby(["tag"]).median()
    pd.set_option("display.max_rows", None)
    tsize = tagrank.groupby(["tag"]).size()
    rnksz = trank.assign(mentions=tsize)
    rnksz["tags"] = rnksz.index
    # print(rnksz.sort_values(by=["mentions"]))
    return rnksz
    # rksz = rnksz.to_dict("records")
    # with open("rksz.json", "w") as f:
    #     json.dump(rksz, f)


@snoop
def main():
    """
    Calls all other functions.
    """
    # # create_dataframe()
    # # note_visualization()
    # # linear_regression()
    # # jinjadata()
    # tag_ranking()


if __name__ == "__main__":
    main()
