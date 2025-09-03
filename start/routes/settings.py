from start import app
import json
from os import path
import codecs

vocabulary = json.load(codecs.open(path.join(app.config['JSON_FOLDER'], 'scales_lng.json'), 'r', 'utf-8-sig'))
# with open(path.join(app.config['JSON_FOLDER'], 'scales_lng.json')) as jsonfile:
#     vocabulary = load(jsonfile.read().decode('utf-8-sig'))
