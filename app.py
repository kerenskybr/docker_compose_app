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

'''
Username
    elastic
Password
    aUt85vdmonTV6DxJm7u2H9od
'''

# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

app = Flask(__name__)


#es = Elasticsearch(['https://localhost:9200/'], timeout=300)
'''
es = Elasticsearch(
    ['elasticsearch'],
    http_auth=('elastic', 'aUt85vdmonTV6DxJm7u2H9od'),
    scheme="https",
    port=9200,
    use_ssl=False,
    verify_certs=False,timeout=30, max_retries=10, retry_on_timeout=True
)
'''
# client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'],27017)
# client = MongoClient()
#client = MongoClient('mongodb://mongodb:27017/')
#db = client.tododb
mgclient = MongoClient('mongodb://mongodb:27017/')
db = mgclient['light']
col = db['task']

es = Elasticsearch(
    ['elasticsearch'],
    http_auth=('elastic', 'aUt85vdmonTV6DxJm7u2H9od')
)

new_posts = [{"author": "Mike",
              "text": "Another post!",
              "tags": ["bulk", "insert"],
              "date": "datetime.datetime(2009, 11, 12, 11, 14)"},
            {"author": "Eliot",
               "title": "MongoDB is fun",
               "text": "and pretty easy too!",
               "date": "datetime.datetime(2009, 11, 10, 10, 45)"}]
post_id = col.insert_many(new_posts)

@app.route('/', methods=['GET'])
def todo():
    _items = db.col.find()

    print("DB GET", _items)
    # _items = es.search(index="tododb", body=_items)
    items = [item for item in _items]

    # Pull from mongo and dump into ES using bulk API
    actions = []
    for data in col.find():
        data.pop('_id')
        action = {
            "index": {
                "_index": 'light',
                "_type": 'task',
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

    es.indices.create(index='machine learning', body=request_body, ignore=400)
    res = es.bulk(index='machine learning', body=actions, refresh=True)


    return render_template('todo.html', items=items)


@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }

    db.col.insert_one(item_doc)

    return redirect(url_for('todo'))


@app.route('/query')
def Query():
    a = es.search(index='machine learning', body={
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

