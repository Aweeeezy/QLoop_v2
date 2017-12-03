import json
import os
from bson import Binary
from __main__ import app
from flask import request, session, redirect, url_for, render_template, flash, send_from_directory
from models import db, User, Song
from util import send_email, allowed_file
from itsdangerous import URLSafeTimedSerializer
from werkzeug import secure_filename
from queue_manager import Booth, BoothRegistry

ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])  # Tokenize acct. mgmt. emails
booth_registry = BoothRegistry()


"""
   ***************************************
    Creating, finding, and joining booths
   ***************************************
"""


@app.route('/api/create_booth/', methods=['POST'])
def create_booth():
    """
        Create a new booth using the request's ACCESS_LEVEL parameter and the
        name of the user stored in the session. Returns the booth ID of the
        newly created booth.
    """

    req = request.get_json()
    access_level = req['access_level']
    user = User.from_json(session['user'])
    bid = booth_registry.add_booth(user.username, access_level)
    user.update(creator_status=bid) # Use BID as req param for JOIN_BOOTH view
    return json.dumps({'booth_id': bid})


@app.route('/api/booths/', methods=['GET'])
def fetch_public_booths():
    """
        Fetch all the public and password protected booths. Returns a list of
        tuples of the form (BOOTH_ID, CREATOR, CURRENT_SONG, ACCESS_LEVEL).
    """

    data = booth_registry.show_booths()
    return json.dumps({'data': data})


@app.route('/api/booths/<bid>/', methods=['GET'])
def join_booth(bid):
    """
        Join a booth by adding the username of the user stored in the session
        into that booth's DJ list. Requires the booth ID. Returns the relevant
        details needed to render the booth view.
    """

    user = User.from_json(session['user'])
    booth_details = booth_registry.join_booth(bid, user.username)
    return json.dumps({'data': booth_details})