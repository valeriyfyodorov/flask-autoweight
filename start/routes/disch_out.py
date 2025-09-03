import time
from start import app
from flask import render_template, request, url_for, redirect
from .settings import vocabulary
from .helpers import defaultEn, queryfromArgs, jsonDictFromUrl


@app.route('/qrcode')
def qrcode():
    print(f"entering qrcode def {time.strftime('%H:%M:%S')}")
    query = queryfromArgs(request.args) + "&local=1"
    lng = defaultEn(request.args.get('lng'), vocabulary)
    voc = vocabulary[lng]["qrcode"]
    print(f"loading qr code page {time.strftime('%H:%M:%S')}")
    return render_template('disch_out/qrcode.html', title='Place your code under camera', voc=voc, query=query)
