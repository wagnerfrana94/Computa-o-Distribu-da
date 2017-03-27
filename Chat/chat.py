from bottle import run, get, post, view, redirect, request 
import requests, bottle, json, threading, time, sys

lock = threading.Lock()

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
	global lock
	time.sleep(5)
	while True:
		time.sleep(1)
		np = []
		for p in peers:
			try:
				r = requests.get(p + '/peers')
				np.append(p)
				np.extend(json.loads(r.text))
			except requests.exceptions.ConnectionError:
				pass

			time.sleep(1)
		with lock:
			peers[:] = list(set(np))

		print(peers)


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


def fault_detector():
    global lock
    time.sleep(5)
    while True:
        time.sleep(1)
        np = set()
        for p in peers:
            try:
                r = requests.get(p + '/peers')
                np.add(p)
            except requests.exceptions.ConnectionError:
                pass
        with lock:
            peers[:] = list(np)		

t1 = threading.Thread(target=clientePeers)
t1.start()

t2 = threading.Thread(target=clienteMessages)
t2.start()

t3 = threading.Thread(target=fault_detector)
t3.start()

run(host='localhost', port=int(sys.argv[1]))
