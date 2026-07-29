import time
from start import app
# from decimal import Decimal
from flask import render_template, request, url_for, redirect
# import urllib.request as urequest
from .settings import vocabulary
from .helpers import defaultEn, queryfromArgs, jsonDictFromUrl, switchBothTrafficLight
from start.intranet.config import SCALES
from start.intranet.defs import getPlatesNumbers, getWeightKg, archivePlates
from start.intranet.picam import camToPilImg
from start.intranet.vision import readQrCodeFromImg


@app.route('/')
def index():
    lngRows = [["lv", "ru"], ["en", "ee"], ["lt", "pl"]]
    return render_template(
        'languages.html', title='Select language', lngRows=lngRows
    )


@app.route('/direction')
def direction():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["direction"]
    print(f"loading direction page {time.strftime('%H:%M:%S')}")
    return render_template(
        'in_or_out.html', title='Choose direction', lng=lng, voc=voc
    )


@app.route('/scales')
def scales():
    print(
        f"starting scales and cameras measurements {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["scales"]
    url = url_for('invoice') if "disch_in" == request.args.get(
        'dir') else url_for('qrcode')
    weightLeft = getWeightKg("north")
    weightRight = getWeightKg("south")
    # weightLeft = 20000 #for test reasons
    # weightRight = 20000
    if weightLeft < 3000 and weightRight < 3000:
        return redirect(
            url_for("unknownerror") + f"?lng={lng}&error=Small weight"
        )
    platesLeft = getPlatesNumbers("north", weight=weightLeft)
    platesRight = getPlatesNumbers("south", weight=weightRight)
    scaleIdLeft = SCALES["north"]["id"]
    scaleIdRight = SCALES["south"]["id"]
    baseQuery = f"?lng={lng}"
    buttons = {
        "left":
        {
            "url": url + baseQuery + f"&sc={scaleIdLeft}&ptf={platesLeft.front}&ptr={platesLeft.rear}&wkg={weightLeft}",
            "textAbove": platesLeft.front,
            "textBelow": platesLeft.rear,
        },
        "right":
        {
            "url": url + baseQuery + f"&sc={scaleIdRight}&ptf={platesRight.front}&ptr={platesRight.rear}&wkg={weightRight}",
            "textAbove": platesRight.front,
            "textBelow": platesRight.rear,
        },
    }
    if weightLeft < 3000:
        print(f"right scale only proceed to plate {time.strftime('%H:%M:%S')}")
        return redirect(buttons["right"]["url"])  # no left weight, no choice
    if weightRight < 3000:
        print(f"left scale only proceed to plate {time.strftime('%H:%M:%S')}")
        return redirect(buttons["left"]["url"])  # no right weight no choice
    print(f"loading scalse choice page {time.strftime('%H:%M:%S')}")
    return render_template(
        'scales.html', title='Choose scale', lng=lng, voc=voc, buttons=buttons
    )


@app.route('/directions')
def directions():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["directions"]
    # next_page_name = app.config['DB_SERVER_URL'] + "weighting-instructions.aspx" # for external server processing
    next_page_name = url_for("qrinstructions")
    return render_template(
        'directions.html',
        title='Proceed to terminal',
        voc=voc,
        next_page_name=next_page_name
    )


@app.route('/unknownerror')
def unknownerror():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["unknownerror"]
    errorTxt = (request.args.get('error') or '')
    # next_page_name = app.config['DB_SERVER_URL'] + "weighting-instructions.aspx"
    return render_template(
        'unknownerror.html', title='Sorry. Error.', voc=voc, errorTxt=errorTxt
    )


@app.route('/farewell')
def farewell():
    print(f"entering farewell {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get('lng'), vocabulary)
    tranunitId = readQrCodeFromImg(camToPilImg())
    voc = vocabulary[lng]["farewell"]
    query = queryfromArgs(request.args)
    if tranunitId == 0:
        return redirect(url_for("qrcode") + query)
    front = (request.args.get('ptf') or '')
    rear = (request.args.get('ptr') or '')
    if len(front) > 3 and len(rear) > 3 and len(front) < 7 and len(rear) < 7:
        print(
            f"getting data from api for truck with id {tranunitId} {time.strftime('%H:%M:%S')}")
        tranunit = jsonDictFromUrl(
            app.config['DB_SERVER_API_URL']
            + f"&command=tranunit" + f"&id={tranunitId}"
        )
        fullPlate = tranunit["nr"]
        if fullPlate is None:
            return redirect(
                url_for("unknownerror")
                + f"?error=The car with this id doesnt exist"
            )
        tareWeightScales = tranunit["weightingEmptyWeight"]
        if (
            (tareWeightScales < 0.1)
            and (len(fullPlate) > 6)
            and (not front[:2] in fullPlate)
            and (not front[-2:] in fullPlate)
            and (not front[1:3] in fullPlate)
            and (not rear[:2] in fullPlate)
            and (not rear[1:3] in fullPlate)
            and (not rear[-2:] in fullPlate)
        ):
            return redirect(
                url_for("unknownerror") +
                f"?error=DB plates differ {front} {rear}"
            )
    api_query = query[1:] + f"&tranunit={tranunitId}"
    api_url = app.config['DB_SERVER_API_URL'] + \
        f"&command=finalweight" + f"&{api_query}"
    print(f"recording weight at api {api_url} {time.strftime('%H:%M:%S')}")
    weighting = jsonDictFromUrl(api_url)
    if weighting["result"] == 2:  # means repeated print out
        print(weighting["error"])
        return redirect(url_for("printout") + f"?{api_query}")
    if weighting["result"] != 0:  # some error
        print(weighting["error"])
        return redirect(
            url_for("unknownerror") + f"?error={weighting['error']}"
        )
    archivePlates(tranunitId, request.args)
    scaleId = request.args.get('sc')
    switchBothTrafficLight(scaleId)
    # next_page_name = app.config['DB_SERVER_URL'] + "weighting-printout.aspx" # in case the printing at amgs
    next_page_name = url_for("printout")
    print(f"loading farewell page {time.strftime('%H:%M:%S')}")
    return render_template(
        'farewell.html',
        title='Get the documents and goodbye',
        voc=voc, next_page_name=next_page_name,
        tranunit=tranunitId
    )
