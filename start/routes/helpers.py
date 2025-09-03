from datetime import datetime
from flask import send_file
import json
import urllib.request as urequest
from socket import timeout
from io import BytesIO
from PIL import Image
from urllib.parse import urlencode as encode
from start.intranet.config import TRAFFIC_LIGHT_API_URL, TRAFFIC_LIGHT_API_AUTH, SCALES_NAME_FOR_ID, SCALES


def dateFromJson(jsonStr):
    return datetime.strptime(jsonStr, '%Y-%m-%dT%H:%M:%S')


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
                        'jsonDictFromUrl. When trying to read data from server API zero length response received')
            else:
                print(
                    'jsonDictFromUrl. An error occurred while attempting to retrieve lists data from the API.')
    except timeout:
        print(
            'jsonDictFromUrl. Timeout error when trying API call'
        )
    return result


def splitDictInto3(dictionary, extraDict=None):
    dict1 = []
    dict2 = []
    dict3 = []
    if extraDict is not None:
        dictionary.append(extraDict)
    if len(dictionary) < 1:
        return dict1, dict2, dict3
    elif len(dictionary) == 1:
        return dictionary, dict2, dict3
    elif len(dictionary) == 2:
        return dictionary[0:1], dictionary[1:], dict3
    divResult = int(len(dictionary) / 3)
    return dictionary[0:divResult], dictionary[divResult: divResult * 2], dictionary[divResult * 2:]


def servePILimageAsPNG(img):
    file_object = BytesIO()
    # img.save(file_object, 'JPEG', quality=70) for jpg
    img.save(file_object, 'PNG')
    file_object.seek(0)
    return send_file(file_object, mimetype='image/PNG')


def switchTrafficLight(scaleId, payload="green", topic="light_topic_front"):
    scaleId = str(scaleId)
    scale = SCALES[SCALES_NAME_FOR_ID[scaleId]]
    body = {"payload": payload, "topic": scale[topic]}
    req = urequest.Request(TRAFFIC_LIGHT_API_URL)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Authorization', TRAFFIC_LIGHT_API_AUTH)
    jsondataasbytes = json.dumps(body).encode('utf-8')
    req.add_header('Content-Length', len(jsondataasbytes))
    try:
        with urequest.urlopen(req, jsondataasbytes) as response:
            if response.getcode() == 200:
                source = response.read()
                if len(source) > 0:
                    result = json.loads(source)
                else:
                    print(
                        'switchTrafficLight. When trying to read data from server API zero length response received')
            else:
                print(
                    'switchTrafficLight. An error occurred while attempting to retrieve lists data from the API.')
    except timeout:
        print(
            'switchTrafficLight. Timeout error when trying API call'
        )
    return result


def switchBothTrafficLight(scaleId, payload="green"):
    topic = "light_topic_front"
    switchTrafficLight(scaleId, payload, topic)
    topic = "light_topic_rear"
    return switchTrafficLight(scaleId, payload, topic)
