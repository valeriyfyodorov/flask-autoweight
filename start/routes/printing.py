from datetime import datetime
from start import app
from flask import render_template, request, url_for, redirect
import qrcode
from socket import error as SocketError
import time
from .settings import vocabulary
from .helpers import defaultEn, queryfromArgs, servePILimageAsPNG, dateFromJson, jsonDictFromUrl


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


@app.route('/printout')
def printout():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["printout"]
    query = queryfromArgs(request.args)
    api_query = query[1:]
    tranunit_id = request.args.get('tranunit')
    tranunit = None
    cargo = None
    client = None
    factory = None
    stevedoreInfo = None
    for i in range(3):
        try:
            tranunit = jsonDictFromUrl(
                app.config['DB_SERVER_API_URL'] + f"&command=tranunit" + f"&id={tranunit_id}")
            time.sleep(0.002)
            cargo = jsonDictFromUrl(
                app.config['DB_SERVER_API_URL'] + f"&command=cargo" + f"&id={tranunit['cargoId']}")
            time.sleep(0.0002)
            client = jsonDictFromUrl(
                app.config['DB_SERVER_API_URL'] + f"&command=company" + f"&id={tranunit['shipperId']}")
            time.sleep(0.0002)
            factory = jsonDictFromUrl(
                app.config['DB_SERVER_API_URL'] + f"&command=company" + f"&id={tranunit['factoryId']}")
            time.sleep(0.0002)
            stevedoreInfo = jsonDictFromUrl(
                app.config['DB_SERVER_API_URL'] +
                f"&command=steveinfo" +
                f"&cargo={tranunit['cargoId']}&shipper={tranunit['shipperId']}&factory={tranunit['factoryId']}"
            )
            break
        except SocketError as e:
            continue
    if (tranunit is None) or (cargo is None) or (client is None) or (factory is None) or (stevedoreInfo is None):
        return redirect(url_for('unknownerror') + query + f"&error=Bad internet connection")
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
    return render_template(
        'prints/printout.html',
        title='Alpha-Osta: Noliktavas svēršanas/glabājuma kvīts',
        voc=voc,
        content=content,
        next_page_name=next_page_name
    )
