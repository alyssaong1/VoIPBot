from luis_sdk import LUISClient

def process_res(res):
    '''
    A function that processes the luis_response object and prints info from it.
    :param res: A LUISResponse object containing the response data.
    '''
    intent = res.get_top_intent().get_name()
    if intent == 'GetWeather':
	reply = 'The weather today is sunny in the morning, cloudy in the afternoon and some light showers in the evening at 5pm'
    elif intent == 'Call':
	reply = 'Unfortunately I am not able to help you make calls yet, sorry!'
    elif intent == 'GetNews':
	reply = "Trump 'shared classified information with Russia'. White House officials dismiss the report relating to talks with Russia's foreign minister as false."
    else:
	reply = "Sorry, I didn't understand your request."
    print(u'Top Scoring Intent: ' + res.get_top_intent().get_name())
    print reply
    return reply

def get_luis_response(text):
    try:
	APPID = 'YOUR_LUIS_APP_ID'
	APPKEY = 'YOUR_LUIS_APP_KEY'
	CLIENT = LUISClient(APPID, APPKEY, True)
	res = CLIENT.predict(text)
	while res.get_dialog() is not None and not res.get_dialog().is_finished():
        	TEXT = raw_input(u'%s\n'%res.get_dialog().get_prompt())
        	res = CLIENT.reply(TEXT, res)
	reply = process_res(res)
	return reply
    except Exception, exc:
	print(exc)
	return "Sorry, something went wrong."
	
