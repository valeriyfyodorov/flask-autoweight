from datetime import datetime
from start import app
from flask import render_template, request, url_for, redirect
import qrcode
import time
from .settings import vocabulary
from .helpers import defaultEn, queryfromArgs, servePILimageAsPNG, dateFromJson, jsonDictFromUrl
from start.intranet import config

# The kiosk keeps its own config.py, which may predate these settings - fall back to the
# defaults instead of failing the import (and with it the whole app) at startup.
EMPTY_ARRIVAL_MIN_TONNES = getattr(config, "EMPTY_ARRIVAL_MIN_TONNES", 10)
EMPTY_ARRIVAL_MAX_TONNES = getattr(config, "EMPTY_ARRIVAL_MAX_TONNES", 30)
CMR_COPIES = getattr(config, "CMR_COPIES", 3)


@app.route('/qrinstructions')
def qrinstructions():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["scales"]
    query = queryfromArgs(request.args)
    api_query = query[1:]
    tranunit_id = request.args.get('tranunit')
    url = app.config['DB_SERVER_API_URL'] + \
        f"&command=tranunit" + f"&id={tranunit_id}"
    tranunit = jsonDictFromUrl(url)
    cargo = jsonDictFromUrl(
        app.config['DB_SERVER_API_URL'] + f"&command=cargo" + f"&id={tranunit['cargoId']}")
    client = jsonDictFromUrl(
        app.config['DB_SERVER_API_URL'] + f"&command=company" + f"&id={tranunit['shipperId']}")
    factory = jsonDictFromUrl(
        app.config['DB_SERVER_API_URL'] + f"&command=company" + f"&id={tranunit['factoryId']}")
    stevedoreInfo = jsonDictFromUrl(
        app.config['DB_SERVER_API_URL'] +
        f"&command=steveinfo" +
        f"&cargo={tranunit['cargoId']}&shipper={tranunit['shipperId']}&factory={tranunit['factoryId']}"
    )
    drivingScheme = stevedoreInfo["drivingScheme"] + ".jpg"
    info = stevedoreInfo["stevedoreInfo"]
    if info is None:
        info = ""
    print_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    netWeightScales = tranunit["weightScales"]
    grossWeightMoment = dateFromJson(tranunit["weightingGrossMoment"])
    grossWeightScales = tranunit["weightingGrossWeight"]
    tareWeightMoment = dateFromJson(tranunit["weightingEmptyMoment"])
    tareWeightScales = tranunit["weightingEmptyWeight"]
    if (grossWeightScales < tareWeightScales):  # loading, not discharging
        grossWeightMoment = dateFromJson(tranunit["weightingEmptyMoment"])
        grossWeightScales = tranunit["weightingEmptyWeight"]
        tareWeightMoment = dateFromJson(tranunit["weightingGrossMoment"])
        tareWeightScales = tranunit["weightingGrossWeight"]
        netWeightScales = -netWeightScales
    showIncomingTitle = (grossWeightScales > tareWeightScales)
    grossWeightScales = "{:.0f}".format(grossWeightScales * 1000)
    issueMoment = grossWeightMoment
    extraHeading = tranunit["declarationNr"] + " // " + \
        "{:.0f}".format(tranunit['weightDeclared'] * 1000) + " kg"
    remark = factory["name"]
    if tranunit["remark"] is not None:
        remark += " " + tranunit["remark"]
    content = {
        "tranunit_id": tranunit["id"],
        "scaleId": tranunit["weightingScaleId"],
        "cargoName": cargo["name"],
        "clientName": client["name"],
        "clientAddress": client["invoiceAddressWording"],
        "clientRegNr": client["officialRegNr"],
        "remark": remark,
        "extraHeading": extraHeading,
        "nr": tranunit["nr"],
        "print_time": print_time,
        "showIncomingTitle": showIncomingTitle,
        "grossWeightScales": grossWeightScales,
        "issueMoment": issueMoment,
        "drivingScheme": drivingScheme,
        "info": info,
    }
    return render_template('disch_in/qrinstructions.html', title='Keep this all time', lng=lng, voc=voc, content=content)


@app.route('/qrimg')
def qrimg():
    code = request.args.get('code')
    img = qrcode.make(code)
    return servePILimageAsPNG(img)


@app.route('/waitprint')
def waitprint():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["waitprint"]
    next_page_name = url_for("index")
    return render_template('prints/waitprint.html', title='Wait', voc=voc, next_page_name=next_page_name)


def apiAnswer(command):
    """Call the API with one command (e.g. "&command=cargo&id=5") and give back its answer.

    jsonDictFromUrl does not raise on a timeout or an empty reply, it quietly gives back
    {"result": 100, "error": "unknown error"} instead. Printing that would put blank or
    missing fields on paper, so here it is turned into an error the caller can retry.
    """
    answer = jsonDictFromUrl(app.config['DB_SERVER_API_URL'] + command)
    if answer.get("error") == "unknown error":
        raise ValueError(f"no answer from the API for {command}")
    return answer


def printDataFromApi(tranunit_id):
    """Fetch everything a printed document needs about one truck, or None on a bad connection.

    Gives back a dict with the API answers "tranunit", "cargo", "client" (the shipper),
    "factory" (the farm/ company chosen on arrival) and "stevedoreInfo". The whole set is
    tried up to 3 times, because the kiosk network drops a call now and then.
    """
    for i in range(3):
        try:
            tranunit = apiAnswer(f"&command=tranunit&id={tranunit_id}")
            time.sleep(0.002)
            cargo = apiAnswer(f"&command=cargo&id={tranunit['cargoId']}")
            time.sleep(0.0002)
            client = apiAnswer(f"&command=company&id={tranunit['shipperId']}")
            time.sleep(0.0002)
            factory = apiAnswer(f"&command=company&id={tranunit['factoryId']}")
            time.sleep(0.0002)
            stevedoreInfo = apiAnswer(
                f"&command=steveinfo"
                f"&cargo={tranunit['cargoId']}&shipper={tranunit['shipperId']}&factory={tranunit['factoryId']}"
            )
            return {
                "tranunit": tranunit,
                "cargo": cargo,
                "client": client,
                "factory": factory,
                "stevedoreInfo": stevedoreInfo,
            }
        # OSError covers the network: timeouts, refused connections and HTTP errors
        # (urllib's URLError/HTTPError are OSErrors). ValueError covers a damaged JSON
        # reply and the quiet failure apiAnswer raises.
        except (OSError, ValueError) as error:
            print(f"printDataFromApi. try {i + 1} failed: {error} {time.strftime('%H:%M:%S')}")
    return None


def arrivedEmptyLeftLoaded(tranunit):
    """Tell whether the truck came in empty and went out loaded - cargo shipped from the port.

    The API keeps the first weighing in "weightingGrossWeight" and the second one in
    "weightingEmptyWeight" (0 until the truck is weighed the second time), both in tonnes.
    "Came in empty" means the first weight lies in the EMPTY_ARRIVAL_... range of config.py.
    An empty truck that goes out no heavier is not loaded, it keeps the usual receipt.
    """
    firstWeight = tranunit["weightingGrossWeight"]
    secondWeight = tranunit["weightingEmptyWeight"]
    arrivedEmpty = EMPTY_ARRIVAL_MIN_TONNES < firstWeight < EMPTY_ARRIVAL_MAX_TONNES
    return arrivedEmpty and secondWeight > firstWeight


@app.route('/printout')
def printout():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["printout"]
    query = queryfromArgs(request.args)
    api_query = query[1:]
    tranunit_id = request.args.get('tranunit')
    printData = printDataFromApi(tranunit_id)
    if printData is None:
        return redirect(url_for('unknownerror') + query + f"&error=Bad internet connection")
    tranunit = printData["tranunit"]
    cargo = printData["cargo"]
    client = printData["client"]
    factory = printData["factory"]
    stevedoreInfo = printData["stevedoreInfo"]
    drivingScheme = stevedoreInfo["drivingScheme"] + ".jpg"
    info = stevedoreInfo["stevedoreInfo"]
    if info is None:
        info = ""
    print_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    netWeightScales = tranunit["weightScales"]
    grossWeightMoment = dateFromJson(tranunit["weightingGrossMoment"])
    tareWeightMoment = dateFromJson(tranunit["weightingEmptyMoment"])
    grossWeightScales = tranunit["weightingGrossWeight"]
    tareWeightScales = tranunit["weightingEmptyWeight"]
    docTitle = "Kravas pieņemšanas glabājumā kvīts"
    if (grossWeightScales < tareWeightScales):  # loading, not discharging
        grossWeightMoment = dateFromJson(tranunit["weightingEmptyMoment"])
        grossWeightScales = tranunit["weightingEmptyWeight"]
        tareWeightMoment = dateFromJson(tranunit["weightingGrossMoment"])
        tareWeightScales = tranunit["weightingGrossWeight"]
        netWeightScales = -netWeightScales
        docTitle = "Kravas izsniegšanas no glabājumā pavadzīme"
    showIncomingTitle = (grossWeightScales > tareWeightScales)
    grossWeightScales = "{:.0f}".format(grossWeightScales * 1000)
    tareWeightScales = "{:.0f}".format(tareWeightScales * 1000)
    netWeightScales = "{:.0f}".format(netWeightScales * 1000)
    issueMoment = tareWeightMoment
    extraHeading = tranunit["declarationNr"] + " // " + \
        "{:.0f}".format(tranunit['weightDeclared'] * 1000) + " kg"
    remark = factory["name"]
    if tranunit["remark"] is not None:
        remark += " " + tranunit["remark"]
    content = {
        "tranunit_id": tranunit["id"],
        "scaleId": tranunit["weightingScaleId"],
        "cargoName": cargo["name"],
        "clientName": client["name"],
        "clientAddress": client["invoiceAddressWording"],
        "clientRegNr": client["officialRegNr"],
        "remark": remark,
        "extraHeading": extraHeading,
        "nr": tranunit["nr"],
        "print_time": print_time,
        "showIncomingTitle": showIncomingTitle,
        "issueMoment": issueMoment.strftime("%d/%m/%Y %H:%M"),
        "grossWeightMoment": grossWeightMoment.strftime("%d/%m/%Y %H:%M"),
        "grossWeightScales": grossWeightScales,
        "tareWeightMoment": tareWeightMoment.strftime("%d/%m/%Y %H:%M"),
        "tareWeightScales": tareWeightScales,
        "netWeightScales": netWeightScales,
        "drivingScheme": drivingScheme,
        "info": info,
        "docTitle": docTitle,
    }
    next_page_name = url_for("waitprint")
    # a truck that came in empty and leaves loaded gets this receipt AND, right after it,
    # the waybill: the receipt page moves on to /pavadzimeprintout instead of /waitprint
    if arrivedEmptyLeftLoaded(tranunit):
        print(f"truck arrived empty and left loaded, pavadzime follows {time.strftime('%H:%M:%S')}")
        next_page_name = url_for("pavadzimeprintout")
    return render_template(
        'prints/printout.html',
        title='Alpha-Osta: Noliktavas svēršanas/glabājuma kvīts',
        voc=voc,
        content=content,
        next_page_name=next_page_name
    )


@app.route('/pavadzimeprintout')
def pavadzimeprintout():
    """Show and print the waybill ("Kravas pavadzīme") of a truck loaded at the port.

    The weighing receipt page (/printout) moves on to here, after printing itself, when
    the truck arrived empty and left loaded. The sender is
    always Alpha Osta, the receiver is the factory the driver chose on arrival, with the
    full name and address from the factory's "invoiceAddressWording". The page holds
    CMR_COPIES copies of the form, one per printed sheet, so a single print job gives them all.
    """
    print(f"entering pavadzimeprintout def {time.strftime('%H:%M:%S')}")
    query = queryfromArgs(request.args)
    tranunit_id = request.args.get('tranunit')
    printData = printDataFromApi(tranunit_id)
    if printData is None:
        return redirect(url_for('unknownerror') + query + f"&error=Bad internet connection")
    tranunit = printData["tranunit"]
    cargo = printData["cargo"]
    factory = printData["factory"]
    # "invoiceAddressWording" is the name and address on separate lines, e.g.
    # "B Port Remars terminal\r\nGāles iela 2, Rīga, \r\nLV-1015, Latvia".
    # Factory 0 ("not in the list") has no address - its lines stay empty to fill in by hand.
    receiverText = factory.get("invoiceAddressWording") or factory.get("name") or ""
    receiverLines = [line.strip() for line in receiverText.splitlines() if line.strip()]
    content = {
        "tranunit_id": tranunit["id"],
        # dated with the second weighing, the moment the loaded truck leaves
        "loadedMoment": dateFromJson(tranunit["weightingEmptyMoment"]),
        "receiverLines": receiverLines,
        "receiverRegNr": factory.get("officialRegNr") or "",
        "cargoName": cargo["name"],
        # weightScales is first minus second weighing in tonnes, negative for a loaded truck
        "netWeightKg": -tranunit["weightScales"] * 1000,
        "nr": tranunit["nr"],
    }
    print(f"loading pavadzime printout page {time.strftime('%H:%M:%S')}")
    return render_template(
        'prints/pavadzime.html',
        title='Alpha-Osta: Kravas pavadzīme',
        content=content,
        copies=CMR_COPIES,
    )
