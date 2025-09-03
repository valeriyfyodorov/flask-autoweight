from start import app
import urllib.parse
from flask import render_template, request, url_for, redirect
from .settings import vocabulary
from .helpers import defaultEn, queryfromArgs, jsonDictFromUrl, splitDictInto3
from start.intranet.defs import getPlatesNumbers, getWeightKg, readInvoice, archivePlates, archiveInvoice


@app.route('/invoice')
def invoice():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["invoice"]
    query = queryfromArgs(request.args)
    return render_template('disch_in/invoice.html', title='Scan invoice or CMR', voc=voc, query=query)


@app.route('/lists')
def lists():
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
    shippersLists = jsonDictFromUrl(api_url)
    if len(shippersLists) == 0:
        return redirect(url_for('unknownerror') + query)
    # allow to choose one and only list available, comment out if direct pass through required
    # if len(shippersLists) == 1 :
    #     return redirect(url_for('factories') + query + f"&list={shippersLists[0]['listId']}")
    return render_template('disch_in/lists.html', title='Choose client and cargo', voc=voc, query=query, shippersLists=shippersLists)


@app.route('/factories')
def factories():
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["factories"]
    shippersList = request.args.get('list')
    query = queryfromArgs(request.args) + f"&list={shippersList}"
    # get one list from api
    api_url = app.config['DB_SERVER_API_URL'] + \
        f"&command=listfactories&list={shippersList}"
    extraDict = {"factoryID": 0, "factoryName": "Cits..Другой..Other"}
    factories = list(splitDictInto3(
        jsonDictFromUrl(api_url), extraDict=extraDict))
    return render_template(
        'disch_in/factories.html', title='Choose your farm/ shipper',
        voc=voc,
        query=query, factories=factories
    )


@app.route('/plates', methods=["GET", "POST"])
def plates():
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
    return render_template(
        'disch_in/plates.html',
        title='Insert plates data',
        front=front, rear=rear,
        voc=voc, query=query, backUrl=backUrl, action=action
    )


@app.route('/cmr', methods=["GET", "POST"])
def cmr():
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
            for i in range(2):
                new_car = jsonDictFromUrl(api_url)
                if new_car is not None:
                    break
        if (new_car) is None:
            return redirect(url_for('unknownerror') + query + f"&error=new car api error {api_url}")
        if len(new_car) < 1:
            return redirect(url_for('unknownerror') + query + f"&error=new car api error {api_url}")
        archivePlates(new_car["id"], request.args)
        archiveInvoice(new_car["id"], request.args, invoiceNr)
        return redirect(url_for('directions') + f"?tranunit={new_car['id']}&local=1&lng={lng}")
    voc = vocabulary[lng]["cmr"]
    action = url_for("cmr") + query
    backUrl = url_for('plates') + queryfromArgs(request.args,
                                                excludeKeysList=["pt"])
    return render_template('disch_in/cmr.html', title='Insert cmr data', voc=voc, query=query, backUrl=backUrl, action=action)
