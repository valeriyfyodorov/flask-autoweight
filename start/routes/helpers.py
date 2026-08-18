from datetime import datetime
from flask import send_file
import json
import unicodedata
import urllib.request as urequest
from socket import timeout
from io import BytesIO
from PIL import Image
from urllib.parse import urlencode as encode
from start.intranet.config import (
    TRAFFIC_LIGHT_API_URL,
    TRAFFIC_LIGHT_API_AUTH,
    SCALES_NAME_FOR_ID,
    SCALES,
)


def dateFromJson(jsonStr):
    return datetime.strptime(jsonStr, "%Y-%m-%dT%H:%M:%S")


def defaultEn(lng, dictionary):
    if lng is None:
        return "en"
    return "en" if lng not in dictionary else lng


def queryfromArgs(args, excludeKeysList=None):
    query = "?"
    convertedDict = args.to_dict(flat=True)
    if excludeKeysList is not None:
        for item in excludeKeysList:
            convertedDict.pop(item, None)
    query += encode(convertedDict)
    if len(query) < 2:
        return ""
    return query


def jsonDictFromUrl(api_url):
    result = {
        "result": 100,
        "error": "unknown error",
    }
    try:
        with urequest.urlopen(api_url) as response:
            if response.getcode() == 200:
                source = response.read()
                if len(source) > 0:
                    result = json.loads(source)
                else:
                    print(
                        "jsonDictFromUrl. When trying to read data from server API zero length response received"
                    )
            else:
                print(
                    "jsonDictFromUrl. An error occurred while attempting to retrieve lists data from the API."
                )
    except timeout:
        print("jsonDictFromUrl. Timeout error when trying API call")
    return result


def splitDictInto2(dictionary):
    """Cut a list of rows into the two columns of the factories page."""
    # rounding up, so that an odd row goes to the left column - the driver reads
    # the left column top to bottom first
    divResult = (len(dictionary) + 1) // 2
    return dictionary[0:divResult], dictionary[divResult:]


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# the bucket for names that sort before "A": digits, punctuation, anything not A-Z.
# It is a key of the grouped dict and the "letter" argument value of its own button,
# so it must stay a plain word - a "#" in a url would start a fragment.
NON_LETTER_KEY = "OTHER"


def firstLetterOf(name):
    """Return the A-Z letter a name should be filed under, or "" if it has none.

    Names coming from the API often have a leading space (" Abra, LPKS") and may
    start with a Latvian letter (Š, Ģ, Ķ). We trim the name and strip the accent
    marks, so that "Šķibe" is filed under "S" - which is where a driver looks for it.
    """
    name = (name or "").strip()
    if len(name) < 1:
        return ""
    # NFD splits an accented letter into base letter + combining mark, then we
    # drop the marks and keep the plain base letter.
    letter = unicodedata.normalize("NFD", name[0])[0].upper()
    return letter if letter in ALPHABET else ""


def letterFromArg(letterArg, default="A"):
    """Return the group key the page's "letter" argument asks for.

    Anything that is neither one letter of the alphabet nor the non-letter bucket -
    including no argument at all, which is the first page load - gives the default.
    """
    letterArg = (letterArg or "").upper()
    if letterArg == NON_LETTER_KEY or (len(letterArg) == 1 and letterArg in ALPHABET):
        return letterArg
    return default


def groupByFirstLetter(rows, nameKey):
    """Group API rows into a dict with one entry per letter: {"A": [...], "B": [...], ...}.

    All 26 letters are always present, an empty list means no rows for that letter -
    the page uses that to grey out the letter buttons a driver cannot press.
    Rows starting with a digit or any other non-letter go under NON_LETTER_KEY,
    the bucket behind the "123#!" button.
    """
    grouped = {letter: [] for letter in ALPHABET}
    grouped[NON_LETTER_KEY] = []
    for row in rows:
        letter = firstLetterOf(row.get(nameKey))
        grouped[letter or NON_LETTER_KEY].append(row)
    return grouped


def distinctByKey(rows, keyName):
    """Keep only the first row of every distinct value of one key, in the original order.

    Rows that repeat a value the caller is grouping by - the same shipper in
    three lists, for example - collapse into their first row, which keeps all of
    its other fields.
    """
    seen = set()
    distinctRows = []
    for row in rows:
        value = row.get(keyName)
        if value not in seen:
            seen.add(value)
            distinctRows.append(row)
    return distinctRows


def servePILimageAsPNG(img):
    file_object = BytesIO()
    # img.save(file_object, 'JPEG', quality=70) for jpg
    img.save(file_object, "PNG")
    file_object.seek(0)
    return send_file(file_object, mimetype="image/PNG")


def switchTrafficLight(scaleId, payload="green", topic="light_topic_front"):
    scaleId = str(scaleId)
    scale = SCALES[SCALES_NAME_FOR_ID[scaleId]]
    body = {"payload": payload, "topic": scale[topic]}
    req = urequest.Request(TRAFFIC_LIGHT_API_URL)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("Authorization", TRAFFIC_LIGHT_API_AUTH)
    jsondataasbytes = json.dumps(body).encode("utf-8")
    req.add_header("Content-Length", len(jsondataasbytes))
    try:
        with urequest.urlopen(req, jsondataasbytes) as response:
            if response.getcode() == 200:
                source = response.read()
                if len(source) > 0:
                    result = json.loads(source)
                else:
                    print(
                        "switchTrafficLight. When trying to read data from server API zero length response received"
                    )
            else:
                print(
                    "switchTrafficLight. An error occurred while attempting to retrieve lists data from the API."
                )
    except timeout:
        print("switchTrafficLight. Timeout error when trying API call")
    return result


def switchBothTrafficLight(scaleId, payload="green"):
    topic = "light_topic_front"
    switchTrafficLight(scaleId, payload, topic)
    topic = "light_topic_rear"
    return switchTrafficLight(scaleId, payload, topic)
