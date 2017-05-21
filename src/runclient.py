import sys
import pjsua as pj
import threading
import bothelper as bot
import time

current_call = None
recorderid = None
playerid = None
call_slot = None

def log_cb(level, str, len):
    print str,

class MyAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def on_incoming_call(self, call):
	global current_call
	if current_call:
	    call.answer(486, "Busy")
	    return

	print "Incoming call from ", call.info().remote_uri

	current_call = call

	call_cb = MyCallCallback(current_call)
	current_call.set_callback(call_cb)

	current_call.answer(180)
	# Hold ringing tone for 3 seconds
	time.sleep(3)
	current_call.answer(200)
	# Listen to user and respond
	listen_and_respond()

def listen_and_respond():
    recorderid = lib.create_recorder("YOUR_FILE_PATH/input.wav")
    recorderslot = lib.recorder_get_slot(recorderid)

    # Connect sound device to wav record file
    lib.conf_connect(0, recorderslot)
    lib.conf_connect(call_slot, recorderslot)

	# Listen for 8 seconds, naive implementation
    time.sleep(8)

    lib.recorder_destroy(recorderid)
    mybot = bot.BotHelper()
    mybot.generate_response()

    # Play wav file back to user
    playerid = lib.create_player('botresponse.wav',loop=False)
    playerslot = lib.player_get_slot(playerid)
    # Connect the audio player to the call
    lib.conf_connect(playerslot,call_slot)

	# Wait for the thing to be read for a few seconds then hang up
	time.sleep(13)
	current_call.hangup()

class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
	pj.CallCallback.__init__(self,call)

    def on_state(self):
		global current_call
		print "Call with", self.call.info().remote_uri,
		print "is", self.call.info().state_text,
		print "last code = ", self.call.info().last_code,
		print "(" + self.call.info().last_reason + ")"

		if self.call.info().state == pj.CallState.DISCONNECTED:
			resetAll()
			print 'Current call is', current_call

    def on_media_state(self):
		global speech_rec
		global recorderid
		global playerid
		global call_slot
		if self.call.info().media_state == pj.MediaState.ACTIVE:
			# connect call to sound device
			call_slot = self.call.info().conf_slot
			pj.Lib.instance().conf_connect(call_slot, 0)
			pj.Lib.instance().conf_connect(0, call_slot)
			lib.set_snd_dev(0, 0)
			print "Media is now active"

		else:
			playerslot = lib.player_get_slot(playerid)
			lib.conf_disconnect(playerslot,0)
			lib.conf_disconnect(0, recorderslot)
			lib.conf_disconnect(call_slot, recorderslot)
			print "Media is inactive"

def resetAll():
	current_call = None
	recorderid = None
	playerid = None
	call_slot = None

lib = pj.Lib()

try:
    mediaconfig = pj.MediaConfig()
    mediaconfig.quality = 10
    lib.init(log_cfg = pj.LogConfig(level=4, callback=log_cb),media_cfg = mediaconfig)
    transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig())
    lib.start()

	# Put your sIP client credentials here
    acc = lib.create_account(pj.AccountConfig("SERVER_IP_ADDRESS", "USERNAME", "PASSWORD"))

    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()

    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
          "(" + acc.info().reg_reason + ")"
    
    if len(sys.argv) > 1:
	lck = lib.auto_lock()

    my_sip_uri = "sip:" + transport.info().host + \
		 ":" + str(transport.info().port)

    # Menu loop
    while True:
	print "My SIP URI is", my_sip_uri
	print "Menu: h=hangup call, q=quit"

	input = sys.stdin.readline().rstrip("\r\n")

	if input == "h":
	    if not current_call:
		print "There is no call"
		continue
	    current_call.hangup()
		resetAll()

	elif input == "q":
	    break

    # shutdown the library
    transport = None

    lib.destroy()
    lib = None

except pj.Error, e:
    print "Exception: " + str(e)
    lib.destroy()
    lib = None
