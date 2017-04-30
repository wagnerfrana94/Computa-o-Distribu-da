from bottle import run, get, post, view, redirect, request 
import requests, bottle, json, threading, time, sys
from frozendict import frozendict

peers = sys.argv[2:]
porta = int(sys.argv[1])
todasMsgs = []
messages = set([])
print(peers)

class VC:
	def __init__(self, name):
		self.name = name
		self.vClock = { self.name: 0 }

	def __repr__(self):
		return "V%s" % repr(self.vClock)

	def increment(self):
		self.vClock[self.name] += 1
		return self

	def update(self, t):
		self.increment()
		for k, v in t.items():
			if k not in vc.vClock or vc.vClock[k] < t[k]:
				vc.vClock[k] = v



vc = VC('http://localhost:' + sys.argv[1]);

@get('/')
@view('index')
def index():
	global todasMsgs
	todasMsgs = list(messages)
	ordenacaoMsg()
	return dict(mens=list(todasMsgs))

def ordenacaoMsg():
	global todasMsgs
	for i in range(1, len(todasMsgs)):
		mens = todasMsgs[i]
		j = i
		while j > 0 and testeMenor(mens, todasMsgs[j - 1]):
			todasMsgs[j] = todasMsgs[j - 1]
			j -= 1
			todasMsgs[j] = mens

def testeMenor(m1, m2):
	keys  = list(set(m1[2].keys()).union(m2[2].keys()))
	keys.sort()
	m1 = tuple(m1[2][j] if j in m1[2] else 0 for j in keys)
	m2 = tuple(m2[2][j] if j in m2[2] else 0 for j in keys)
	for i in range(0, len(m1)):
		if m1 < m2: return True
		if m2 < m1: return False
	return False
    

@get('/newMessage')
@view('newMessage')
def new():
	return

@post('/sendMessage')
def newMessage():
	user = request.forms.get('user')
	msg = request.forms.get('message')
	global messages
	if user != None and msg != None:
		vc.increment()
		m = (user, msg, frozendict(vc.vClock))
		messages.add(m)
	redirect('/')


@get('/peers')
def index():
	return json.dumps(peers)

@get('/messages')
def index():
	return json.dumps([(user, msg, dict(tmp)) for (user, msg, tmp) in messages])
	


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


def Messages():
	while True:
        	time.sleep(2)
        	global messages
        	for p in peers:
            		time.sleep(2)
            		msg = recebeMsg(p)
            		for (user, msg, tmp) in msg.difference(messages):
                		vc.update(tmp)
                		messages.add((user, msg, tmp))

def recebeMsg(p):
	r = requests.get(p + "/messages")
	obj = json.loads(r.text)
	rm = set((a, b, frozendict(t)) for [a,b,t] in obj)
	return rm
    
	
t1 = threading.Thread(target=clientePeers)
t1.start()

t2 = threading.Thread(target=Messages)
t2.start()



run(host='localhost', port=porta)

