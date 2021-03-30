from flask_cors.decorator import cross_origin
import requests
import json
from booliapi import BooliApi
from flask import Flask, render_template, jsonify, make_response
from typing import List
from flask_cors import CORS
from expiringdict import ExpiringDict
cache = ExpiringDict(max_len=100, max_age_seconds=60*60*24)

app = Flask(__name__)
CORS(app)
app.run(debug=True)

with open('config.json') as config_file:
    config = json.load(config_file)

booli_api = BooliApi(
    user_agent='Isak Friis-Jespersen',
    base_url='https://api.booli.se',
    id_caller=config.get('callerId'),
    private_key=config.get('privateKey')
)


@app.route('/get-booli-data/<resource>/<q>', methods=['GET'])
@cross_origin()
def get_booli_data(resource, q):
    if cache.get(f'/get-booli-data/{resource}/{q}'):
        return cache.get(f'/{resource}/{q}')
    max_objects_to_fetch = 5000
    limit: int = 500
    offset: int = 0
    next_links: bool = True
    data: List[dict] = []
    while(next_links):
        url: str = '{}{}'.format(
            booli_api.base_url,
            booli_api.create_booli_parameters(
                resource=resource,
                q=q,
                limit=limit,
                offset=offset
            )
        )
        response = requests.get(url, headers=booli_api.headers)
        response: json = response.json()
        data += booli_api.extract_date_price(data=response.get('sold'))
        if (
            offset >= response.get('totalCount') or
            offset >= max_objects_to_fetch
        ):
            next_links: bool = False
        offset: int = booli_api.get_offset(
            count=response.get('count'),
            offset=offset
        )
    res: json = jsonify({'res': data})
    cache[f'/get-booli-data/{resource}/{q}'] = res
    return make_response(res, 200)


@app.route('/')
def index():
    return render_template('index.html')
