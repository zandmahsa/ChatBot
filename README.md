# Chatbot 

This project is a simple AI chatbot that includes channels for communication, including a Guess Number Game and an NLP Channel for sentiment analysis. The chatbot and channels are built using Flask, and the NLP Channel leverages the `TextBlob` library to analyze the sentiment of messages.

## Features

- **NLP Sentiment Analysis**: Messages sent through the NLP Channel are analyzed for sentiment (positive, neutral, or negative) using the `TextBlob` library. Polarity scores are also provided.
- **Guess Number Game**: The chatbot includes a simple game where users guess a number, and the bot responds with feedback on whether their guess was too high, too low, or correct.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or later installed
- Pip (Python package manager) installed
- Flask and dependencies listed in `requirements.txt`
- TextBlob for sentiment analysis

### Install dependencies

You can install the dependencies using pip:

```bash
pip install -r requirements.txt
```

### How to Run the Project
1. Start the Hub and client
First, start the hub that manages the channels.

```bash
python hub.py
python client.py

```
This will start the hub on http://localhost:5555. The hub allows channels to register and manage communication with the client.
The chatbot and the game run on http://localhost:5005.

2. Start Channels
Run channels for each of them open new terminal:

```bash
python nlp_channel.py
python channel.py
python channel2.py
python chatbot.py
```
The NLP channel runs on http://localhost:5008 and listens for incoming messages for sentiment analysis.

4. Access the Client
After registering the NLP channel, you can access the web client by navigating to:

```bash
http://localhost:5005/
```
This will list the available channels, including the NLP channel and the Guess Number game. You can interact with each channel by clicking on it.


### Customization
Adding New Channels
You can add more channels by creating new Flask apps (similar to nlp_channel.py) and registering them with the hub. Each channel can have its own unique functionality.
#### Register the new Channel
Once the channel is running, register it with the hub using the following command:

```bash
flask --app new_channel:app register
```

#### Modifying the Frontend
The HTML files for the chat interfaces are located in the templates/ directory. You can modify the CSS and HTML to customize the user interface.

License
This project is open-source and free to use under the MIT License.

