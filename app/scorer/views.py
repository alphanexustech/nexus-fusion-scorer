from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify, request

import requests, json

from . import controllers

scorer = Blueprint('scorer', __name__)

@scorer.route('/<fusion_set>/', methods=['POST'])
def analyze_text(fusion_set=None):
    r = request.get_json()
    doc = r.get('doc')
    return jsonify(controllers.analyze_text(fusion_set=fusion_set, doc=doc))
