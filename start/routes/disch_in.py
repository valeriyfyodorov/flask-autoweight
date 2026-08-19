import urllib.parse
import time
from start import app
from flask import render_template, request, url_for, redirect
from .settings import vocabulary
from .helpers import (
    defaultEn,
    queryfromArgs,
    jsonDictFromUrl,
    distinctByKey,
    splitDictInto2,
    switchBothTrafficLight,
    groupByFirstLetter,
    letterFromArg,
    ALPHABET,
    NON_LETTER_KEY,
)
from start.intranet.config import STORED_IMAGES_KIOSK_IP
from start.intranet.defs import readInvoice, archivePlates, archiveInvoice, archiveCargoImage


@app.route("/invoice")
def invoice():
    print(f"entering invoice def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get("lng"), vocabulary)
    voc = vocabulary[lng]["invoice"]
    query = queryfromArgs(request.args)
    print(f"loading invoices page {time.strftime('%H:%M:%S')}")
    return render_template(
        "disch_in/invoice.html", title="Scan invoice or CMR", voc=voc, query=query
    )


def todayListsFromApi(lng):
    """Fetch today's lists from the API, or an empty list when the call fails.

    The lists page and the cargoes page work from the same rows, one per shipper
    x cargo pair. jsonDictFromUrl survives a timeout only, and on a quiet failure
    it gives back an error dict instead of a list. Anything that is not a real
    list of rows comes back from here empty, which both pages answer with the
    error page instead of a flask traceback.
    """
    api_url = app.config["DB_SERVER_API_URL"] + f"&command=todaylists&lng={lng}"
    print(f"loading shippers list from api {api_url} {time.strftime('%H:%M:%S')}")
    try:
        todayLists = jsonDictFromUrl(api_url)
    except (OSError, ValueError) as error:
        # a timeout, a refused connection and an http error are all OSError,
        # a damaged answer raises ValueError out of the json parser
        print(f"todayListsFromApi. API call failed: {error} {time.strftime('%H:%M:%S')}")
        return []
    return todayLists if isinstance(todayLists, list) else []


@app.route("/lists")
def lists():
    """Show one button per shipper that has a list open today.

    The API gives one row per shipper x cargo pair, so a shipper with three
    cargoes comes back three times. Here the rows are reduced to one per shipper
    and the first list id of that shipper travels on as "list" - the cargoes page
    only needs it to find the shipper again, the driver picks the real list there.
    """
    print(f"entering lists def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get("lng"), vocabulary)
    voc = vocabulary[lng]["lists"]
    query = queryfromArgs(request.args)
    # the invoice is photographed once, on the way in. Coming back from the cargoes
    # page "ifn" already says so, and the camera must not overwrite that photo
    invoiceFileName = request.args.get("ifn")
    if invoiceFileName is None:
        okInvoice, invoiceFileName = readInvoice()
        if not okInvoice:
            return redirect(url_for("invoice") + query)
    query = (
        queryfromArgs(request.args, excludeKeysList=["ifn"])
        + f"&ifn={invoiceFileName}"
        + f"&kiosk_ip={STORED_IMAGES_KIOSK_IP}"
    )
    todayLists = todayListsFromApi(lng)
    if len(todayLists) == 0:
        return redirect(url_for("unknownerror") + query)
    # allow to choose one and only shipper available, comment out if direct pass through required
    # if len(todayLists) == 1:
    #     return redirect(url_for('cargoes') + query + f"&list={todayLists[0]['listId']}")
    distinctShippersShippersLists = distinctByKey(todayLists, "shipperId")
    # sorted by the same text the page shows: the custom heading wins over the shipper name
    distinctShippersShippersLists.sort(
        key=lambda row: (row["truckScalesHeading"] or row["shipperName"]).strip().lower()
    )
    print(f"loading lists page {time.strftime('%H:%M:%S')}")
    return render_template(
        "disch_in/lists.html",
        title="Choose client",
        voc=voc,
        query=query,
        distinctShippersShippersLists=distinctShippersShippersLists,
    )


@app.route("/cargoes")
def cargoes():
    """Show one button per cargo of the shipper chosen on the lists page.

    The lists page hands over the first list id of that shipper in "list".
    Today's lists are fetched again here, the shipper is looked up by that id,
    and every list of the same shipper becomes one cargo button. A shipper never
    has the same cargo twice, so those rows are already distinct.
    """
    print(f"entering cargoes def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get("lng"), vocabulary)
    voc = vocabulary[lng]["cargoes"]
    selectedListId = request.args.get("list")
    # every cargo button appends its own "list", so the shipper's one must not travel on
    query = queryfromArgs(request.args, excludeKeysList=["list"])
    todayLists = todayListsFromApi(lng)
    if len(todayLists) == 0:
        return redirect(url_for("unknownerror") + query)
    # the list ids from the api are numbers, the query string gives text - compare as text
    selectedList = next(
        (row for row in todayLists if str(row["listId"]) == str(selectedListId)), None
    )
    if selectedList is None:
        # no "list" argument at all, or the list has been closed since the lists page
        return redirect(url_for("unknownerror") + query + "&error=list not in today lists")
    distinctCargoesShippersLists = [
        row for row in todayLists if row["shipperId"] == selectedList["shipperId"]
    ]
    distinctCargoesShippersLists.sort(key=lambda row: row["cargoName"].strip().lower())
    # the back button returns to the shipper choice, without the shipper picked here
    backUrl = url_for("lists") + query
    print(f"loading cargoes page {time.strftime('%H:%M:%S')}")
    return render_template(
        "disch_in/cargoes.html",
        title="Choose cargo",
        voc=voc,
        query=query,
        backUrl=backUrl,
        distinctCargoesShippersLists=distinctCargoesShippersLists,
    )


@app.route("/factories")
def factories():
    """Show the farms/ shippers of the chosen list, filtered by one letter A-Z.

    The whole list is fetched from the API in a single call and grouped by the
    first letter here, so that the page can tell which letter buttons have
    factories behind them. Names that start with a digit or any other non-letter
    sort before "A" and live behind their own "123#!" button ("letter=other").
    Without a "letter" argument - the first page load - "A" is shown.
    """
    print(f"entering factories def {time.strftime('%H:%M:%S')}")
    lng = defaultEn(request.args.get("lng"), vocabulary)
    voc = vocabulary[lng]["factories"]
    shippersList = request.args.get("list")
    # the letter is a filter of this page only, it must not travel to the next pages
    # ("list" is already in the arguments, no need to add it again)
    query = queryfromArgs(request.args, excludeKeysList=["letter"])
    # get one list from api, unfiltered - the API letter filters are not reliable
    api_url = app.config["DB_SERVER_API_URL"] + f"&command=listfactories&list={shippersList}"
    print(f"loading factories list from api {api_url} {time.strftime('%H:%M:%S')}")
    allFactories = jsonDictFromUrl(api_url)
    # on any API trouble jsonDictFromUrl gives back an error dict instead of a list
    if not isinstance(allFactories, list) or len(allFactories) == 0:
        return redirect(url_for("unknownerror") + query)
    groupedFactories = groupByFirstLetter(allFactories, "factoryName")
    letterSelected = letterFromArg(request.args.get("letter"))
    # every button is the same page url with just the letter changed. First comes the
    # button of the names sorting before "A", then one button per letter of the alphabet
    letterUrlStart = request.base_url + query
    separator = "&" if "?" in letterUrlStart else "?"
    letterButtons = [(NON_LETTER_KEY, "123#!")] + [(letter, letter) for letter in ALPHABET]
    letterData = [
        {
            "letter": label,
            "url": f"{letterUrlStart}{separator}letter={key.lower()}",
            "state": "active" if key == letterSelected else "",
            "enabled": len(groupedFactories[key]) > 0,
        }
        for key, label in letterButtons
    ]
    # letterSelected is always one of the keys, so no fallback is needed
    factories = list(splitDictInto2(groupedFactories[letterSelected]))
    # the page appends "&fr=<factoryID>" to this. It is built here and not in the
    # template, so that the template keeps no quotes inside the onclick attribute
    platesUrl = url_for("plates") + query
    # factory number 0 means "not in the list", it is always offered as a button
    otherUrl = platesUrl + "&fr=0"
    print(f"loading factories page {time.strftime('%H:%M:%S')}")
    return render_template(
        "disch_in/factories.html",
        title="Choose your farm/ shipper",
        voc=voc,
        query=query,
        factories=factories,
        letterData=letterData,
        platesUrl=platesUrl,
        otherUrl=otherUrl,
    )


@app.route("/plates", methods=["GET", "POST"])
def plates():
    print(f"entering plates def {time.strftime('%H:%M:%S')}")
    query = queryfromArgs(request.args)
    if request.method == "POST":
        plate = request.form.get("ptf") + "/" + request.form.get("ptr")
        if len(plate) < 7:
            return redirect(url_for("invoice") + query)
        query += f"&pt={plate}"
        return redirect(url_for("cmr") + query)
    lng = defaultEn(request.args.get("lng"), vocabulary)
    voc = vocabulary[lng]["plates"]
    front = request.args.get("ptf") or ""
    rear = request.args.get("ptr") or ""
    action = url_for("plates") + query
    backUrl = url_for("factories") + queryfromArgs(request.args, excludeKeysList=["fr", "pt"])
    print(f"loading plates page {time.strftime('%H:%M:%S')}")
    return render_template(
        "disch_in/plates.html",
        title="Insert plates data",
        front=front,
        rear=rear,
        voc=voc,
        query=query,
        backUrl=backUrl,
        action=action,
    )


@app.route("/cmr", methods=["GET", "POST"])
def cmr():
    print(f"entering cmr def {time.strftime('%H:%M:%S')}")
    query = queryfromArgs(request.args)
    lng = defaultEn(request.args.get("lng"), vocabulary)
    if request.method == "POST":
        invoiceNr = request.form.get("inr")
        # invoiceNr = invoiceNr.replace(
        # "/", "").replace("\\", "").replace(" ", "")
        # alphanumeric_filter = filter(str.isalnum, invoiceNr)
        # invoiceNr = "".join(alphanumeric_filter)
        invoiceNr = urllib.parse.quote(invoiceNr, safe="")
        invoiceWeight = request.form.get("iwt")
        api_query = query[1:] + f"&inr={invoiceNr}&iwt={invoiceWeight}"
        api_url = app.config["DB_SERVER_API_URL"] + f"&command=newunitweight" + f"&{api_query}"
        new_car = jsonDictFromUrl(api_url)
        if (new_car) is None:
            for i in range(5):  # retry API
                print(f"getting new car from api {api_url}")
                new_car = jsonDictFromUrl(api_url)
                if new_car is not None:
                    break
        if (new_car) is None:
            return redirect(url_for("unknownerror") + query + f"&error=new car api error {api_url}")
        if len(new_car) < 1:
            return redirect(url_for("unknownerror") + query + f"&error=new car api error {api_url}")
        if "id" not in new_car:
            return redirect(
                url_for("unknownerror") + query + f"&error=probably repeated nr {api_url}"
            )
        archivePlates(new_car["id"], request.args)
        archiveCargoImage(new_car["cargoId"], request.args)
        archiveInvoice(new_car["id"], request.args, invoiceNr)
        scaleId = request.args.get("sc")
        switchBothTrafficLight(scaleId)
        return redirect(url_for("directions") + f"?tranunit={new_car['id']}&local=1&lng={lng}")
    voc = vocabulary[lng]["cmr"]
    action = url_for("cmr") + query
    backUrl = url_for("plates") + queryfromArgs(request.args, excludeKeysList=["pt"])
    print(f"loading cmr page {time.strftime('%H:%M:%S')}")
    return render_template(
        "disch_in/cmr.html",
        title="Insert cmr data",
        voc=voc,
        query=query,
        backUrl=backUrl,
        action=action,
    )
