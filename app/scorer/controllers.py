from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify, request
from multiprocessing import Pool
import requests, json

# Date
from datetime import datetime

# Application context
from app import app

# Configuration
from config import configurations

def default():
    return 'Hello Scorers!'

def call_affect_scorer(doc=None):
    payload = {'doc': doc}
    r = requests.post(configurations.affect_endpoint + 'scorer/all_affects/', json=payload)
    if(r.raise_for_status()):
        return 404
    else:
        return {'affect_scores': r.json()}

def call_role_scorer(doc=None):
    payload = {'doc': doc}
    r = requests.post(configurations.role_endpoint + 'scorer/all_roles/', json=payload)
    if(r.raise_for_status()):
        return 404
    else:
        return {'role_scores': r.json()}

def call_percept_scorer(doc=None):
    payload = {'doc': doc}
    r = requests.post(configurations.percept_endpoint + 'scorer/all_percepts/', json=payload)
    if(r.raise_for_status()):
        return 404
    else:
        return {'percept_scores': r.json()}

def worker(input_pair):
    func, arg = input_pair
    return func(arg)

def call_scorers(doc=None):
    result = {}
    # functions = [call_affect_scorer, call_role_scorer, call_percept_scorer]
    # types = ['affect_scores', 'role_scores', 'percept_scores']
    pool = Pool(3)
    # result['affect_scores'] = call_affect_scorer(doc)
    # result['role_scores'] = call_role_scorer(doc)
    # result['percept_scores'] = call_percept_scorer(doc)

    pooled_results = pool.map(worker, [(call_affect_scorer, doc),(call_role_scorer, doc), (call_percept_scorer, doc)])
    pool.close()
    pool.join()

    for r in pooled_results:
        key = list(r.keys())[0] # This is the key of the scorer
        result[key] = r[key]

    return result

def analyze_text(fusion_set=None, doc=None):
    if fusion_set == 'all_data': # Get the common_set
        if doc:
            result = call_scorers(doc)
            return {
                "doc": doc,
                "status": "OK",
                "fusion_set": result,
                "date": [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]]
            }
        else:
            return {
                "status": "OK",
                "message": "The document is missing."
            }
    else:
        return {
            "status": "OK",
            "message": "Not Implemented"
        }
