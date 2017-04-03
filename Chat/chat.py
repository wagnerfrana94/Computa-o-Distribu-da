from bottle import run, get, post, view, redirect, request 
import requests, bottle, json, threading, time, sys


messages = []
peers = sys.argv[2:]
print(peers)

@get('/')
@view('index')
def index():
    return {'messages': messages}
    

@get('/newMessage')
@view('newMessage')
def new():
	return

@post('/sendMessage')
def newMessage():
    user = request.forms.get('user')
    msg = request.forms.get('message')
    messages.append([user, msg])
    redirect('/')


@get('/peers')
def index():
	return json.dumps(peers)

@get('/messages')
def index():
	return json.dumps(messages)

def clientePeers():
	time.sleep(5)
	while True:
		time.sleep(1)
		np = []
		for p in peers:
			r = requests.get(p + '/peers')
			np = np + json.loads(r.text)
		peers[:] = list(set(np + peers))
		print(peers)
		time.sleep(2)


def clienteMessages():
	time.sleep(5)
	while True:
		nm = []
		for p in peers:
			m = requests.get(p + '/messages')
			nms = json.loads(m.text)
			for msg in nms:
					if msg not in messages:
						messages.append(msg)
	
		time.sleep(2)

	

t1 = threading.Thread(target=clientePeers)
t1.start()

t2 = threading.Thread(target=clienteMessages)
t2.start()



run(host='localhost', port=int(sys.argv[1]))
