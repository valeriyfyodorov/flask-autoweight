import urllib.parse
import time
from start import app
from flask import render_template, request, url_for, redirect
from .settings import vocabulary
from .helpers import (
    defaultEn, queryfromArgs, jsonDictFromUrl, splitDictInto3,
    switchBothTrafficLight, groupByFirstLetter, ALPHABET
)
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
    """Show the farms/ shippers of the chosen list, filtered by one letter A-Z.

    The whole list is fetched from the API in a single call and grouped by the
    first letter here, so that the page can tell which letter buttons have
    factories behind them. Without a "letter" argument every factory is shown.
    """
    print(f"entering factories def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["factories"]
    shippersList = request.args.get('list')
    letterSelected = (request.args.get('letter') or "").upper()
    if len(letterSelected) != 1 or letterSelected not in ALPHABET:
        # anything that is not one letter of the alphabet means "show them all"
        letterSelected = ""
    # the letter is a filter of this page only, it must not travel to the next pages
    # ("list" is already in the arguments, no need to add it again)
    query = queryfromArgs(request.args, excludeKeysList=["letter"])
    # get one list from api, unfiltered - the API letter filters are not reliable
    api_url = app.config['DB_SERVER_API_URL'] + \
        f"&command=listfactories&list={shippersList}"
    print(
        f"loading factories list from api {api_url} {time.strftime('%H:%M:%S')}")
    allFactories = jsonDictFromUrl(api_url)
    # on any API trouble jsonDictFromUrl gives back an error dict instead of a list
    if not isinstance(allFactories, list) or len(allFactories) == 0:
        return redirect(url_for('unknownerror') + query)
    groupedFactories = groupByFirstLetter(allFactories, "factoryName")
    # every letter button is the same page url with just the letter changed
    letterUrlStart = request.base_url + \
        queryfromArgs(request.args, excludeKeysList=["letter"])
    separator = "&" if "?" in letterUrlStart else "?"
    # first button shows everything, then one button per letter of the alphabet
    letterData = [{
        "letter": "A-Z",
        "url": letterUrlStart,
        "state": "" if letterSelected else "active",
        "enabled": True,
    }]
    for letter in ALPHABET:
        letterData.append({
            "letter": letter,
            "url": letterUrlStart + separator + f"letter={letter}",
            "state": "active" if letter == letterSelected else "",
            "enabled": len(groupedFactories[letter]) > 0,
        })
    chosenFactories = groupedFactories.get(letterSelected, allFactories)
    factories = list(splitDictInto3(chosenFactories))
    # factory number 0 means "not in the list", it is always offered as a button
    otherUrl = url_for('plates') + query + "&fr=0"
    print(f"loading factories page {time.strftime('%H:%M:%S')}")
    return render_template(
        'disch_in/factories.html', title='Choose your farm/ shipper',
        voc=voc,
        query=query, factories=factories,
        letterData=letterData, otherUrl=otherUrl,
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
        scaleId = request.args.get('sc')
        switchBothTrafficLight(scaleId)
        return redirect(url_for('directions') + f"?tranunit={new_car['id']}&local=1&lng={lng}")
    voc = vocabulary[lng]["cmr"]
    action = url_for("cmr") + query
    backUrl = url_for('plates') + queryfromArgs(request.args,
                                                excludeKeysList=["pt"])
    print(f"loading cmr page {time.strftime('%H:%M:%S')}")
    return render_template('disch_in/cmr.html', title='Insert cmr data', voc=voc, query=query, backUrl=backUrl, action=action)
