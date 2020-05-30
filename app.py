import os
from flask import Flask, redirect, url_for, request, render_template, jsonify
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import pymongo
from bson import json_util, ObjectId
import json
import tqdm
# 53f4q253642gf55437v54utjujthy vhj563f426536f422536f4g
# elastic_deploy
import time
app = Flask(__name__)

mgclient = MongoClient('mongodb://mongodb:27017/')
db = mgclient['light']
col = db['task']

es = Elasticsearch(
    ['elasticsearch'],
    http_auth=('elastic', 'aUt85vdmonTV6DxJm7u2H9od')
    )

dummy_data = {
    'name': 'dummy_data',
    'description': 'dummy_data'
}

col.insert_one(dummy_data)

@app.route('/', methods=['GET'])
def todo():

    # Pull from mongo and dump into ES using bulk API
    # Here, name will become an index in es
    #ES stuff
    actions = []
    for data in col.find():
        data.pop('_id')
        action = {
            "index": {
                "_index": 'description',
                "_type": 'text',
            }
        }
        actions.append(action)
        actions.append(data)
    # delete = es1.indices.delete(index = 'light')
    request_body = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }

    es.indices.create(index='light', body=request_body, ignore=400)
    res = es.bulk(index='light', body=actions, refresh=True)

    _items = col.find()
    items = [item for item in _items]

    return render_template('todo.html', items=items)


@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }

    col.insert_one(item_doc)

    return redirect(url_for('todo'))


@app.route('/query')
def query():
    a = es.search(index='light', body={
        'query': {
            'match': {
                'name': 'test',
            }
        }
    })
    return jsonify(query=a)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

'''
PUT /inspections - to create indexes

POST /inspections/_doc - to post indexes

GET /inspections/_search - to grab indexes


Examples:
POST /inspections/_doc
{"index":{"_id": 1},
  "name": "Jane Calamidy",
  "description": "Nice hat"
}

GET /inspections/_search
{
  "query":{
    "match":{
      "description": "Nice"
    }
  }
}
'''

