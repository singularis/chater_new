from flask import  request, jsonify
import logging


log = logging.getLogger("main")

def context_switch(session):
    state = request.json.get('state', 'off')
    session['switch_state'] = state
    return jsonify({'status': 'success', 'state': state})

def use_switch_state(session):
    # Retrieve the switch state from the session
    switch_state = session.get('switch_state', 'off')
    return jsonify({"switch_state": switch_state})