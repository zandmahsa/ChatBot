from flask import Flask, request, render_template, url_for, redirect
import requests
import urllib.parse
import datetime
import random
import json
import os
app = Flask(__name__)

HUB_AUTHKEY = '1234567890'
HUB_URL = 'http://localhost:5555'

CHANNELS = None
LAST_CHANNEL_UPDATE = None
CHANNEL_FILE = 'messages3.json' 

GAME_DATA = {
    'number_to_guess': random.randint(1, 100),
    'attempts': 0,
    'game_started': False,  
}


def update_channels():
    global CHANNELS, LAST_CHANNEL_UPDATE
    if CHANNELS and LAST_CHANNEL_UPDATE and (datetime.datetime.now() - LAST_CHANNEL_UPDATE).seconds < 60:
        return CHANNELS
    
    response = requests.get(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY})
    if response.status_code != 200:
        print("Error fetching channels: "+str(response.text))  
        CHANNELS = []  
        return CHANNELS
    channels_response = response.json()
    if not 'channels' in channels_response:
        print("No channels in response")  
        CHANNELS = []  
        return CHANNELS
    CHANNELS = channels_response['channels']
    LAST_CHANNEL_UPDATE = datetime.datetime.now()
    return CHANNELS


@app.route('/')
def home_page():
    return render_template("home.html", channels=update_channels())


@app.route('/show', methods=['GET', 'POST'])
def show_channel():
    requested_channel_name = request.args.get('channel', None)
    if not requested_channel_name:
        return "No channel specified", 400
    
    decoded_channel_name = urllib.parse.unquote(requested_channel_name)
    channel = next((c for c in update_channels() if c['name'] == decoded_channel_name), None)
    
    if not channel:
        return "Channel not found", 404
    
    if channel['name'] == "guess number game":
        return redirect(url_for('chatbot_page'))
    else:
        
        response = requests.get(channel['endpoint'], headers={'Authorization': 'authkey ' + channel['authkey']})
        if response.status_code != 200:
            return "Error fetching messages: " + str(response.text), response.status_code
        
        messages = response.json()
        return render_template("channel.html", channel=channel, messages=messages)


@app.route('/post', methods=['POST'])
def post_message():
    post_channel = request.form.get('channel', None)
    if not post_channel:
        return "No channel specified", 400
    decoded_channel_name = urllib.parse.unquote(post_channel)
    channel = next((c for c in update_channels() if c['name'] == decoded_channel_name), None)

    if not channel:
        return "Channel not found", 404
    
    message_content = request.form['content']
    message_sender = request.form['sender']
    message_timestamp = datetime.datetime.now().strftime('%Y-%m-%d Time %H:%M')
    response = requests.post(channel['endpoint'],
                             headers={'Authorization': 'authkey ' + channel['authkey']},
                             json={'content': message_content, 'sender': message_sender, 'timestamp': message_timestamp})
    if response.status_code != 200:
        return "Error posting message: "+str(response.text), 400
    return redirect(url_for('show_channel')+'?channel='+urllib.parse.quote(post_channel))
  
def read_messages():
    if not os.path.exists(CHANNEL_FILE):
        return []
    with open(CHANNEL_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            return []  

def write_messages(messages):
    with open(CHANNEL_FILE, 'w') as file:
        json.dump(messages, file, indent=4)


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot_page():
    messages = read_messages()
    now_formatted = datetime.datetime.now().strftime('%Y-%m-%d Time %H:%M')

    if request.method == 'GET' and not GAME_DATA['game_started']:
        # Game start or page refresh without a game in progress
        welcome_message = "Hello, welcome to our game! Now you can guess a number from 0 to 100. Let's play..."
        messages.append({'sender': 'Chatbot', 'content': welcome_message, 'timestamp': now_formatted})
        GAME_DATA['game_started'] = True  

    if request.method == 'POST':
        guess = int(request.form.get('guess'))
        response, reset = process_guess(guess)
        messages.append({'sender': 'User', 'content': f'Guessed: {guess}', 'timestamp': now_formatted})
        messages.append({'sender': 'Chatbot', 'content': response, 'timestamp': now_formatted})

        if reset:
            # Game won, prepare for a new round
            GAME_DATA['number_to_guess'] = random.randint(1, 100)  # Generate a new number
            GAME_DATA['attempts'] = 0  # Reset attempt count
            GAME_DATA['game_started'] = False  # Reset start flag
            replay_message = "We can play again! I've already guessed another number from 0 to 100. Can you guess?"
            messages.append({'sender': 'Chatbot', 'content': replay_message, 'timestamp': now_formatted})

    write_messages(messages)
    return render_template('message.html', messages=messages)


def process_guess(guess):
    GAME_DATA['attempts'] += 1  
    if guess < GAME_DATA['number_to_guess']:
        return "Too low! Try again.", False
    elif guess > GAME_DATA['number_to_guess']:
        return "Too high! Try again.", False
    else:
        congratulations_message = f"Congratulations! You've guessed the number {GAME_DATA['number_to_guess']} in {GAME_DATA['attempts']} attempts."
        GAME_DATA['game_started'] = False  
        return congratulations_message, True


if __name__ == '__main__':
    app.run(port=5005, debug=True)
