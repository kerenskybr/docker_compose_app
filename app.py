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
es = Elasticsearch(
    ['localhost'],
    http_auth=('elastic', 'aUt85vdmonTV6DxJm7u2H9od'),
    scheme="https",
    port=9200,
)

# client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'],27017)
# client = MongoClient()
#client = MongoClient('mongodb://mongodb:27017/')
#db = client.tododb
mgclient = MongoClient('mongodb://mongodb:27017/')
db = mgclient['light']
col = db['task']


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
    _items = db.tododb.find()

    print("DB GET", _items)
    # _items = es.search(index="tododb", body=_items)
    # items = [item for item in _items]

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

    es.indices.create(index='light', body=request_body, ignore=400)
    res = es.bulk(index='light', body=actions, refresh=True)
    '''
    result = db.find()
    names = []
    for obj in db.find():
        name = obj['name']
        names.append(name)
        print(names)
    '''
    return render_template('todo.html')


@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)

    # Creating mongoddb indexes
    # db.tododb.create_index([('text', pymongo.ASCENDING)])

    # page_sanitized = json.loads(json_util.dumps(item_doc))
    # es.indices.create(index='text', body=page_sanitized)

    # res = es.bulk(index='example_index', body=page_sanitized)
    # page_sanitized = json.loads(json_util.dumps(item_doc))

    # res = es.index(index="text", id=1, body=page_sanitized)
    # print("ELASTIC RESULT", res['result'])

    '''
    #Creating mongoddb indexes
    db.tododb.createIndex({'name':'text', 'content':'text'})

    print("ITEM DOC", item_doc)

    page_sanitized = json.loads(json_util.dumps(item_doc))

    res = es.index(index="name", id=1, body=page_sanitized)
    print("ELASTIC RESULT", res['result'])

    res = es.search(index="name", body={"query": {"match_all": {}}})
    print("Got %d Hits:" % res['hits']['total']['value'])
    for hit in res['hits']['hits']:
        print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
    '''

    return redirect(url_for('todo'))


@app.route('/query')
def Query():
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

'''
  elasticsearch:
    hostname: elasticsearch
    image: elasticsearch:6.8.9
    ports:
      - "9200:9200"
      - "9300:9300"  

networks:
  somenetwork:
    driver: bridge      
'''
