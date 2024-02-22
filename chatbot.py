from flask import Flask, request,render_template, jsonify, redirect, url_for
import random
import requests
import json
import datetime
import random
import os


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'


app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  
app.app_context().push()  


# Configuration for the chatbot channel
HUB_URL = 'http://localhost:5555'
HUB_AUTHKEY = '1234567890'
CHANNEL_AUTHKEY = '9876543210'

CHANNEL_NAME = "guess number game"
CHANNEL_ENDPOINT = "http://localhost:5007"

# Store the number to guess and the number of attempts
GAME_DATA = {
    'number_to_guess': random.randint(1, 100),
    'attempts': 0,
    'game_started': False,
}

@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
            "name": CHANNEL_NAME,
            "endpoint": CHANNEL_ENDPOINT,
            "authkey": CHANNEL_AUTHKEY}))

    if response.status_code != 200:
        print("Error creating channel: "+str(response.status_code))
        return

def check_authorization(request):
    global CHANNEL_AUTHKEY
    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name':CHANNEL_NAME}),  200










    






if __name__ == '__main__':
    app.run(port=5007, debug=True)
