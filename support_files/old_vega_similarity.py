"""
Module Docstring
"""
import os
import pickle

import jinja2
import pandas as pd
import snoop
from dotenv import load_dotenv
from snoop import pp


def type_watch(source, value):
    return f"type({source})", type(value)


load_dotenv()
snoop.install(watch_extras=[type_watch])


@snoop
def create_dataframe():
    """
    Unpickles the dictionary in 'vagadata.bin'
    and converts it to a dataframe.
    """
    binaries = os.getenv("BINARIES")

    with open(f"{binaries}vegadata.bin", "rb") as f:
        vegadata = pickle.load(f)

    vd = pd.DataFrame(vegadata)

    return vd


@snoop
def select_by_tag(tag):
    """
    Creates Dataframe from rows
    containing a given tag.
    """
    vd = create_dataframe()

    # As we have tags in 3 different columns 'tagscore1/2/3', we
    # need to search for the tag in each one. There are no index
    # methods to search, directly, inside values in a dataframe.
    # What we can use is a function to do it indirectly. As, for
    # some reason, you can't apply the lambda function to a list
    # of columns in one go, we do it separately.
    # The .aplly() dataframe function, applies another function
    # to dataframe data. In this case is applying a lambda
    # function that defines an argument (col), as the first
    # result in the argument, equal to a given tag. As the args
    # used are the 'tagscore*' columns, 'col' equals 'tagscore*'
    msk1 = vd["tagscore1"].apply(lambda col: col[0] == f"{tag}")
    msk2 = vd["tagscore2"].apply(lambda col: col[0] == f"{tag}")
    msk3 = vd["tagscore3"].apply(lambda col: col[0] == f"{tag}")

    # 'msks' unites through the OR ('|') operator the three masks.
    msks = msk1 | msk2 | msk3

    # 'vtg' is a new dataframe that results from the 'msks' expression.
    vt = vd[msks]

    return vt


@snoop
def define_tag():
    return "python"


@snoop
def tag_score(row):
    tag = define_tag()
    tscore = ["tagscore1", "tagscore2", "tagscore3"]
    for col in tscore:
        if row[col][0] == tag:
            return row[col][1]
        return None


@snoop
def dictdata():
    """
    Where we choose data if they have a certain tag..
    """
    tg = "python"
    vtg = select_by_tag(tg)

    # def tag_score(row):
    #     tag = define_tag()
    #     for col in ["tagscore1", "tagscore2", "tagscore3"]:
    #         print(f"row[col][0] is: {row[col][0]}")
    #         print(f"row[col][1] is: {row[col][1]}")
    #         print(f"tag is: {tag}")
    #         if row[col][0] == tag:
    #             return row[col][1]
    #         return None

    vtg["tag_score"] = vtg.apply(tag_score, axis=1)
    pd.set_option("display.max_rows", None)
    print(vtg)
    # graphdata = vtg.to_dict(orient="records")

    # return graphdata


dictdata()


@snoop
def jinjadata():
    """
    Data that'll be passed to Jinja2, for it
    to create a html page with our data.
    """
    graphdata = dictdata()

    pages = os.getenv("PAGES")

    template_loader = jinja2.FileSystemLoader(searchpath="./templates/")
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "base.tpl"
    template = template_env.get_template(template_file)
    output_text = template.render(
        title="tag fitness score",
        description="How well a tag describes the text of the note.",
        page_url="http://localhost/vega_experiments/pages/tagscore.html",
        graphic_title="'Python' Tag Fitness Score",
        graph_width=800,
        dictdata=graphdata,
        xfield={"field": "hour", "type": "quantitative"},
        yfield={},
    )
    html_path = f"{pages}test.html"
    html_file = open(html_path, "w")
    html_file.write(output_text)
    html_file.close()
