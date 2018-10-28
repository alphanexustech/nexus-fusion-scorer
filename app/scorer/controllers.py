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

def get_feature_index():
    feature_index = {}
    # Affect Features
    i = 0;
    affmemdist = get_bucketed_affect_member_distribution()['member_distribution']
    rolmemdist = get_bucketed_role_member_distribution()['member_distribution']
    permemdist = get_bucketed_percept_member_distribution()['member_distribution']
    for key in affmemdist:
        for val in affmemdist[key]:
            if val in feature_index:
                print(val, i)
            else:
                feature_index[val] = i
                i += 1
                # print(val, i)

    for key in rolmemdist:
        for val in rolmemdist[key]:
            if val in feature_index:
                print(val, i)
            else:
                feature_index[val] = i
                i += 1
                # print(val, i)

    for key in permemdist:
        for val in permemdist[key]:
            if val in feature_index:
                print(val, i)
            else:
                feature_index[val] = i
                i += 1
                # print(val, i)

    return {
        "feature_index": feature_index,
        "length": len(feature_index),
        "missing": [value for value in range(600) if value not in list(feature_index.values())]
    }

###
# Distributions
###
def get_bucketed_affect_member_distribution():
    r = requests.get(configurations.affect_endpoint + 'scorer/memberdist/bucketed/')
    if(r.raise_for_status()):
        return 404
    else:
        return r.json()

def get_bucketed_role_member_distribution():
    r = requests.get(configurations.role_endpoint + 'scorer/memberdist/bucketed/')
    if(r.raise_for_status()):
        return 404
    else:
        return r.json()

def get_bucketed_percept_member_distribution():
    r = requests.get(configurations.percept_endpoint + 'scorer/memberdist/bucketed/')
    if(r.raise_for_status()):
        return 404
    else:
        return r.json()


###
# Scorers
###
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
    pool = Pool(3)
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
