# This is the server side script for an Alexa Skill I created that grabs and converts cryptocurrency prices on the fly.
# It uses the cryptocompare API to fetch the latest price of several cryptocurrencies, and can also calculate dollar amounts from coin amounts.
# Ex1. "Alexa, ask coinprice what the price of bitcoin is"
# Ex2. "Alexa, ask coinprice how much my 2 bitcoins are worth"
# Ex3. "Alexa, ask coinprice to read me the latest crypto news"

from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import datetime
import unidecode
import requests
import time

app = Flask(__name__)
ask = Ask(app, "/reddit_reader")
headline_msg = ""
global lastTime

def checkTime():
	FMT = '%H:%M:%S'
	tdelta = datetime.strptime( datetime.datetime.now().time(), FMT) - datetime.strptime(lastTime, FMT)
	if tdelta.seconds > 60:
		return True
	else:
		return False

def coinWrapper(coinType):
	if coinType == "bitcoin":
		return "BTC"
	elif coinType == "ethereum":
		return "ETH"
	elif coinType == "zcash":
		return "ZEC"
	elif coinType == "lisk":
		return "LSK"

def getData(coinType):
	result = coinWrapper(coinType)
	response = requests.get("https://min-api.cryptocompare.com/data/price?fsym={0}&tsyms=USD".format(result))
	lastTime = datetime.datetime.now().time()
	return response.text

@app.route('/')
def homepage():
	return "hi there, how ya doin?"

@ask.launch
def start_skill():
	welcome_message = 'What would you like to do?'
	return question(welcome_message)

@ask.intent("GetNews")
def get_headlines():
	# If you want to self host this, put your Reddit API username and password here.
	user_pass_dict = {'user': 'usernameGoesHere',
	'passwd': 'passwordGoesHere',
	'api_type': 'json'}
	sess = requests.Session()
	sess.headers.update({'User-Agent': 'I am testing Alexa: Trevor'})
	sess.post('https://www.reddit.com/api/login', data=user_pass_dict)
	time.sleep(1)
	url = 'https://reddit.com/r/cryptocurrency/.json?limit=10'
	html = sess.get(url)
	data = json.loads(html.content.decode('utf-8'))
	titles = [unidecode.unidecode(listing['data']['title']) for listing in data['data']['children']]
	titles = '... '.join([i for i in titles])
	return statement(titles)

@ask.intent("PriceIntent")
def share_headlines(coinType):
	try:
		if lastTime == None:
			headline_msg = getData(coinType)
		elif checkTime():
			headline_msg = getData(coinType)
	except:
			headline_msg = getData(coinType)
	return statement("The price of " + coinType + " is " + headline_msg[7:-4] + " dollars, and " + headline_msg[-3] + "cents.")

@ask.intent("CalcIntent")
def calculate_coin(coinType, amount):
	coinPrice = getData(coinType)
	amountCoin = int(amount)
	total = amountCoin * float(coinPrice[7:-1])
	return statement(str(amount) + " " + str(coinType) + " is equal to " + str(total) + " dollars.. give or take a few cents")

@ask.intent("NoIntent")
def no_intent():
	bye_text = 'I am not sure why you asked me to run then, but okay... bye'
	return statement(bye_text)

if __name__ == '__main__':
	app.run(debug=True)
