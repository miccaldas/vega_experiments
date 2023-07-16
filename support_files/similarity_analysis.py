"""
Module that'll analyze the note's text of the notes db and
compare it to the tags of the same note, to see if they are
related. A fitness score will be atributed to each post and,
hopefully, steer us to better our tagging game. This is a
complex and large project, so I'll break it down in byte-size
pieces, so as not to overtax the machine.
Its output is used by the 'similarity_vega' module, that'll
handle the visualization of the data.
"""
import contextlib
import os
import pickle
import string
from datetime import datetime

import snoop
import yake
from dotenv import load_dotenv
from mysql.connector import Error, connect
from snoop import pp
from thefuzz import fuzz, process


def type_watch(source, value):
    return f"type({source})", type(value)


load_dotenv()
snoop.install(watch_extras=[type_watch])

# Envirnomental Variables
binaries = os.getenv("BINARIES")
kwdresults = os.getenv("KWDRESULTS")
notespth = os.getenv("NOTESPTH")


# @snoop
def db_data(query):
    """
    Gets the query from the functions that call it,
    downloads the needed data from the db.
    """

    try:
        conn = connect(host="localhost", user="mic", password="xxxx", database="notes")
        cur = conn.cursor()
        cur.execute(query)
        dbdata = cur.fetchall()
    except Error as e:
        print("Error while connecting to db", e)
    finally:
        if conn:
            conn.close()

    with open(f"{binaries}db_data.bin", "wb") as f:
        pickle.dump(dbdata, f)

    return dbdata


# @snoop
def yake_processing(text):
    """
    Each note text will pass through here, the
    Yake keyword creator, to create up to 20
    keywords. It'll be called from the 'readfiles'
    function.
    """
    kw_extractor = yake.KeywordExtractor()
    language = "en"
    max_ngram_size = 1
    deduplication_threshold = 0.9
    numOfKeywords = 20
    custom_kw_extractor = yake.KeywordExtractor(
        lan=language,
        n=max_ngram_size,
        dedupLim=deduplication_threshold,
        top=numOfKeywords,
        features=None,
    )
    # Yake's list of keywords.
    keywords = custom_kw_extractor.extract_keywords(text)
    # Erasing any punctuation that might in the keywords.
    punct_kwds = [
        i[0].translate(str.maketrans("", "", string.punctuation)) for i in keywords
    ]
    # Turning them all to lowercase.
    lower_kwds = [i.lower() for i in punct_kwds]
    # Stripping them of spaces.
    clean_kwds = [i.strip() for i in lower_kwds]

    return clean_kwds


# @snoop
def notefileslocation():
    """
    Defines a paths list to the note's files.
    Called from 'readfiles'.
    """
    # Creates a list with only the filenames in the note's folder.
    noteslst = os.listdir(notespth)
    # List of the filename preceed by the rest of the path.
    # This is to avoid file discovery problems.
    notefiles = [(f"{notespth}/{i}", i) for i in noteslst]

    return notefiles


# @snoop
def readfiles():
    """
    Gets a list of paths to the note's files, iterates through
    them to open them as strings. Runs Yake on these texts, and
    stores the result in a file kept in the 'kwd_files' folder.
    """
    # Calls the 'notefileslocation' function.
    notefiles = notefileslocation()
    # Reads the note's files, turns them to strings, calls yake
    # so it can create its keywords and stores the results in a
    # pickle file, so as to preserve them as lists.
    for file in notefiles:
        with open(file[0], "r", encoding="latin-1") as f:
            text = f.read()
        yake = yake_processing(text)
        with open(f"{kwdresults}/{file[1][:-4]}.bin", "wb") as g:
            kwd = pickle.dump(yake, g)


readfiles()


# @snoop
def yake_lst():
    """
    Creates a list of paths to the newly created files,
    generates path and file name tuples and stores them
    in a list. From these list, it'll extract the ntid
    value that is part of the filename, by slicing the
    the path string, and append it to each entry.
    Stored in a pickle file, so as not to have to run
    this everytime we need to restart.
    """
    # Calls the database information.
    query = "SELECT ntid, title, tags, time, string_date FROM tags_streamlit"
    dbdata = db_data(query)
    # List of the filenames created by the 'readfiles' function.
    kwlst = os.listdir(kwdresults)
    # Creates a list of tuples consisting in the full path to the
    # Yake files and their filename.
    kwdfiles = [(f"{kwdresults}/{i}", i) for i in kwlst]

    # Creates empty list to house the list with the yake results.
    yakelst = []
    # For each binary file in the 'kwd_files' directory...
    for bin in kwdfiles:
        # Opening the file with the paths we collected...
        with open(bin[0], "rb") as f:
            kwdlst = pickle.load(f)
            # We define 'fileid' as the ntid number that we get from the filename.
            fileid = int(bin[1][:-4])
            # And we append it to the corresponding sublist.
            kwdlst.append(fileid)
            yakelst.append(kwdlst)

    with open(f"{binaries}yakelst.bin", "wb") as f:
        pickle.dump(yakelst, f)


# @snoop
def db_tags():
    """
    Opens the yakelst file and runs through the ntid's values to
    look for the corresponding tags. Stores them, with the ntid
    value, in a pickled file called 'tgcollection.bin'.
    """
    with open(f"{binaries}db_data.bin", "rb") as g:
        dbdata = pickle.load(g)

    with open(f"{binaries}yakelst.bin", "rb") as f:
        yakelst = pickle.load(f)

    tgcollection = []
    # For list of yake keywords...
    for yak in yakelst:
        # 'fileid' is the last entry in each note sublist.
        fileid = yak[-1]
        # The column 'tags' in the db has the index 2. Get
        # the tags if the fileid we're currently looping
        # through is the same as the first value in the row.
        tags = [(i[2]) for i in dbdata if i[0] == fileid]
        # Append to it the 'fileid', so we know what it
        # corresponds to.
        tags = tags + [fileid]
        tgcollection.append(tags)

    with open(f"{binaries}tgcollection.bin", "wb") as h:
        pickle.dump(tgcollection, h)


# @snoop
def append_list():
    """
    Appends the information that was distributed in the two files
    about the notes, into one list with all the information.
    """
    with open(f"{binaries}tgcollection.bin", "rb") as f:
        tgcollection = pickle.load(f)

    with open(f"{binaries}yakelst.bin", "rb") as g:
        yakelst = pickle.load(g)

    # 'tgcollection' will append a 'yakelst' list, minus the fileid, to its own list,
    # where their fileid's are equal.
    tgkwd = [i + [f[:-1]] for i in tgcollection for f in yakelst if i[-1] == f[-1]]

    with open(f"{binaries}tgkwd.bin", "wb") as f:
        pickle.dump(tgkwd, f)


# @snoop
def fuzz_process():
    """
    We'll use the library 'thefuzz' to score each tag
    against Yake's keywords. For each note, we'll
    create a list of tuples with the tag name and their
    score, as well as the fileid.
    """
    with open(f"{binaries}tgkwd.bin", "rb") as f:
        tgkwd = pickle.load(f)

    fuzzlst = []
    for i in tgkwd:
        v1 = process.extractOne(i[0], i[-1])
        v2 = process.extractOne(i[1], i[-1])
        v3 = process.extractOne(i[2], i[-1])
        if v1 is not None:
            fuzzvalues = [[i[0], v1[1]], [i[1], v2[1]], [i[2], v3[1]], i[3]]
            fuzzlst.append(fuzzvalues)

    with open(f"{binaries}fuzzlst.bin", "wb") as g:
        pickle.dump(fuzzlst, g)


# @snoop
def tagresults():
    """
    With the results of 'fuzzlst', sums up all
    points and sees how far it is from a perfect
    score, 300. This is the note's score.
    """
    with open(f"{binaries}fuzzlst.bin", "rb") as f:
        fuzzlst = pickle.load(f)

    tgresults = []
    noneresults = []
    for f in fuzzlst:
        if f[0] is not None:
            tagresult = f[0][1] + f[1][1] + f[2][1]
            tgscore = 300 - tagresult
            tgresults.append((f[0], f[1], f[2], tgscore, f[-1]))
        else:
            f.append(noneresults)

    with open(f"{binaries}tgresults.bin", "wb") as g:
        pickle.dump(tgresults, g)

    with open(f"{binaries}noneresults.bin", "wb") as e:
        pickle.dump(noneresults, e)


# @snoop
def note_data():
    """
    We'll combine the 'tgresults' as well as 'completefuzz'
    data, with db information on the 'title', 'string_date'
    and 'time' columns. This info will be used to create
    visualizations with Vega-lite, based on note analysis.
    """
    query = "SELECT ntid, title, time, string_date FROM tags_streamlit"
    dbdata = db_data(query)

    with open(f"{binaries}tgresults.bin", "rb") as f:
        tgresults = pickle.load(f)

    # Creates a new list of dictionaries, where they're divided by note.
    vn = [
        {
            "ntid": i[4],
            "score": i[3],
            "title": f[1],
            "time": f[2],
            "string_date": f[3],
        }
        for i in tgresults
        for f in dbdata
        if i[4] == f[0]
    ]

    # As we've been using 'tags_streamlit' data, we have now in 'vg', three identical
    # entries per 'ntid', as the tags values are not on a 'tags' field, but each on
    # its own 'tagscore' field. The newxt is a dictionary comprehension that uses as
    # key the 'ntid' field; and as dict keys can't repeat themselves, we have a set of
    # entries. '.values()', creates a view of the data.
    notedata = list({i["ntid"]: i for i in vn}.values())

    with open(f"{binaries}notedata.bin", "wb") as h:
        pickle.dump(notedata, h)


# @snoop
def tagbin():
    """
    Creates a data file, specifically geared to tag anaylsis.
    """
    with open(f"{binaries}tgresults.bin", "rb") as f:
        tgresults = pickle.load(f)

    tagtups = []
    for i in tgresults:
        tagtups.append((i[0], i[4]))
        tagtups.append((i[1], i[4]))
        tagtups.append((i[2], i[4]))

    with open(f"{binaries}tagtups.bin", "wb") as f:
        pickle.dump(tagtups, f)


# @snoop
def tag_data():
    """
    Creates a list with three rows per note, one per each
    tag. The tag name and value are now two separated
    fields, so we can create columns from them.
    We change 'time'format, so it can be used by Vega-lite.
    """
    query = "SELECT ntid, title, time FROM notes"
    dbdata = db_data(query)

    with open(f"{binaries}tagtups.bin", "rb") as f:
        tagtups = pickle.load(f)

    tag_data = [
        (
            d[0],
            d[1],
            t[0][0],
            t[0][1],
            d[2].strftime("%d-%m-%Y"),
        )
        for d in dbdata
        for t in tagtups
        if d[0] == t[1]
    ]

    with open(f"{binaries}tag_data.bin", "wb") as f:
        pickle.dump(tag_data, f)


# @snoop
def tag_dict():
    """
    Creates dictionary from the data in tagdata.
    """
    with open(f"{binaries}tag_data.bin", "rb") as f:
        tag_data = pickle.load(f)

    vt = [
        {"ntid": t[0], "title": t[1], "tag": t[2], "value": t[3], "time": t[4]}
        for t in tag_data
    ]

    with open(f"{binaries}tagdata.bin", "wb") as g:
        pickle.dump(vt, g)


# @snoop
def main():
    """
    Starts the process by calling all other functions.
    """
    readfiles()
    yake_lst()
    db_tags()
    append_list()
    fuzz_process()
    tagresults()
    note_data()
    tagbin()
    tag_data()
    tag_dict()


# if __name__ == "__main__":
#     main()
