import urllib.parse
import time
from start import app
from flask import render_template, request, url_for, redirect
from .settings import vocabulary
from .helpers import defaultEn, queryfromArgs, jsonDictFromUrl, splitDictInto3
from start.intranet.defs import (
    readInvoice, archivePlates, archiveInvoice, archiveCargoImage
)


@app.route('/invoice')
def invoice():
    print(f"entering invoice def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["invoice"]
    query = queryfromArgs(request.args)
    print(f"loading invoices page {time.strftime('%H:%M:%S')}")
    return render_template('disch_in/invoice.html', title='Scan invoice or CMR', voc=voc, query=query)


@app.route('/lists')
def lists():
    print(f"entering lists def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["lists"]
    okInvoice, invoiceFileName = readInvoice()
    query = queryfromArgs(request.args)
    if not okInvoice:
        return redirect(url_for('invoice') + query)
    query = queryfromArgs(request.args) + f"&ifn={invoiceFileName}"
    # get lists from api
    api_url = app.config['DB_SERVER_API_URL'] + \
        f"&command=todaylists&lng={lng}"
    print(
        f"loading shippers list from api {api_url} {time.strftime('%H:%M:%S')}")
    shippersLists = jsonDictFromUrl(api_url)
    if len(shippersLists) == 0:
        return redirect(url_for('unknownerror') + query)
    # allow to choose one and only list available, comment out if direct pass through required
    # if len(shippersLists) == 1
    #     return redirect(url_for('factories') + query + f"&list={shippersLists[0]['listId']}")
    print(f"loading lists page {time.strftime('%H:%M:%S')}")
    return render_template('disch_in/lists.html', title='Choose client and cargo', voc=voc, query=query, shippersLists=shippersLists)


@app.route('/factories')
def factories():
    print(f"entering factories def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["factories"]
    shippersList = request.args.get('list')
    blockSelected = request.args.get('block')
    blockUrlStart = request.base_url + \
        queryfromArgs(request.args, excludeKeysList=["block"])
    blockData = {
        "0":
        {
            "url": blockUrlStart,
            "state": "active",
        },
        "1":
        {
            "url": blockUrlStart + "&block=1",
            "state": "",
        },
        "2":
        {
            "url": blockUrlStart + "&block=2",
            "state": "",
        },
    }
    query = queryfromArgs(request.args) + f"&list={shippersList}"
    # get one list from api
    api_url = app.config['DB_SERVER_API_URL'] + \
        f"&command=listfactories&list={shippersList}"
    extraDict = {"factoryID": 0, "factoryName": "Cits..Другой..Other"}
    if (blockSelected == "1"):
        api_url += f"&greaterthan=i&lessthan=p"
        blockData["0"]["state"] = ""
        blockData["1"]["state"] = "active"
    if (blockSelected == "2"):
        api_url += f"&greaterthan=p"
        blockData["0"]["state"] = ""
        blockData["2"]["state"] = "active"
    else:
        api_url += f"&lessthan=i"
        extraDict = None
    print(
        f"loading factories list from api {api_url} {time.strftime('%H:%M:%S')}")
    factories = list(splitDictInto3(
        jsonDictFromUrl(api_url), extraDict=extraDict))
    print(f"loading factories page {time.strftime('%H:%M:%S')}")
    return render_template(
        'disch_in/factories.html', title='Choose your farm/ shipper',
        voc=voc,
        query=query, factories=factories,
        blockData=blockData,
    )


@app.route('/plates', methods=["GET", "POST"])
def plates():
    print(f"entering plates def {time.strftime('%H:%M:%S')}")
    query = queryfromArgs(request.args)
    if request.method == 'POST':
        plate = request.form.get('ptf') + "/" + request.form.get('ptr')
        if len(plate) < 7:
            return redirect(url_for('invoice') + query)
        query += f"&pt={plate}"
        return redirect(url_for('cmr') + query)
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["plates"]
    front = (request.args.get('ptf') or '')
    rear = (request.args.get('ptr') or '')
    action = url_for("plates") + query
    backUrl = url_for('factories') + \
        queryfromArgs(request.args, excludeKeysList=["fr", "pt"])
    print(f"loading plates page {time.strftime('%H:%M:%S')}")
    return render_template(
        'disch_in/plates.html',
        title='Insert plates data',
        front=front, rear=rear,
        voc=voc, query=query, backUrl=backUrl, action=action
    )


@app.route('/cmr', methods=["GET", "POST"])
def cmr():
    print(f"entering cmr def {time.strftime('%H:%M:%S')}")
    query = queryfromArgs(request.args)
    lng = defaultEn(request.args.get('lng'), vocabulary)
    if request.method == 'POST':
        invoiceNr = request.form.get('inr')
        # invoiceNr = invoiceNr.replace(
        # "/", "").replace("\\", "").replace(" ", "")
        # alphanumeric_filter = filter(str.isalnum, invoiceNr)
        # invoiceNr = "".join(alphanumeric_filter)
        invoiceNr = urllib.parse.quote(invoiceNr, safe='')
        invoiceWeight = request.form.get('iwt')
        api_query = query[1:] + f"&inr={invoiceNr}&iwt={invoiceWeight}"
        api_url = app.config['DB_SERVER_API_URL'] + \
            f"&command=newunitweight" + f"&{api_query}"
        new_car = jsonDictFromUrl(api_url)
        if (new_car) is None:
            for i in range(5):  # retry API
                print(f"getting new car from api {api_url}")
                new_car = jsonDictFromUrl(api_url)
                if new_car is not None:
                    break
        if (new_car) is None:
            return redirect(url_for('unknownerror') + query + f"&error=new car api error {api_url}")
        if len(new_car) < 1:
            return redirect(url_for('unknownerror') + query + f"&error=new car api error {api_url}")
        if "id" not in new_car:
            return redirect(url_for('unknownerror') + query + f"&error=probably repeated nr {api_url}")
        archivePlates(new_car["id"], request.args)
        archiveCargoImage(new_car["cargoId"], request.args)
        archiveInvoice(new_car["id"], request.args, invoiceNr)
        return redirect(url_for('directions') + f"?tranunit={new_car['id']}&local=1&lng={lng}")
    voc = vocabulary[lng]["cmr"]
    action = url_for("cmr") + query
    backUrl = url_for('plates') + queryfromArgs(request.args,
                                                excludeKeysList=["pt"])
    print(f"loading cmr page {time.strftime('%H:%M:%S')}")
    return render_template('disch_in/cmr.html', title='Insert cmr data', voc=voc, query=query, backUrl=backUrl, action=action)
