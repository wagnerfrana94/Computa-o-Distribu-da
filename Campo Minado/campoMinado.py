from random import *
from bottle import run, get, post, view, redirect, request 
import requests, bottle, json, threading, time, sys
from frozendict import frozendict

tabuleiro = []
tabuleiroView = []

peers = sys.argv[2:]
porta = int(sys.argv[1])
pontos = 0
estado="jogando"
meuHash = {}

caminho_porta ="http://localhost:" + str(porta) 

seed(5)

print(peers)

@get('/')
@view('campo_minado')
def criaCampoMinado():
	global tabuleiroView
	global tabuleiro
	tabuleiroView  = [[ '-' for x in range(10)] for x in range(10)]
	tabuleiro  = [[ randint(0,3) for x in range(10)] for x in range(10)]
	#print (tabuleiroView)
	
	# print (len(tabuleiro))
	for i in range(len(tabuleiro)):
		for j in range(len(tabuleiro)):
			if tabuleiro[i][j] != 1:
				tabuleiro[i][j] = 0

	for i in range(len(tabuleiro)):
		for j in range(len(tabuleiro)):
			if tabuleiro[i][j] == 1:
				tabuleiro[i][j] = 10

	# print (tabuleiro)
	for i in range(len(tabuleiro)):
		for j in range(len(tabuleiro)):
			if tabuleiro[i][j] >= 10 and j > 0: #soma no lado esquerdo da bomba 
				tabuleiro[i][j-1]+=1

			if tabuleiro[i][j] >= 10 and j > 0 and i < 9: #soma no lado esquerdo pra baixo 
				tabuleiro[i+1][j-1]+=1

			if tabuleiro[i][j] >= 10 and j > 0 and i > 0: #soma no lado esquerdo pra cima
				tabuleiro[i-1][j-1]+=1

			if tabuleiro[i][j] >= 10 and j < 9: #soma na direita 
				tabuleiro[i][j+1]+=1

			if tabuleiro[i][j] >= 10 and j < 9 and i < 9: #soma na direita pra baixo 
				tabuleiro[i+1][j+1]+=1

			if tabuleiro[i][j] >= 10 and j < 9 and i > 0: #soma na direita pra cima 
				tabuleiro[i-1][j+1]+=1

			if tabuleiro[i][j] >= 10 and i > 0: #soma em cima
				tabuleiro[i-1][j]+=1

			if tabuleiro[i][j] >= 10 and i < 9: #soma embaixo
				tabuleiro[i+1][j]+=1


	#print ("\nTabuleiro com as Bombas e Aviso de Quantidades")
	#print ("Valores menores de 10 são as quantidades de bombas no entorno")
	#print ("valores maior ou igual a 10 são bombas somadas de quantidades no entorno")
	#for i in range(len(tabuleiro)):
		#print('\n')
		#for j in range(len(tabuleiro)):

			#print("  %d  " %tabuleiro[i][j], end = "")

	#print('\n')
	

	#print (tabuleiro)
	redirect('/tabuleiro')

@get('/tabuleiro')
@view('campo_minado')
def retornaTabuleiroview():
	return {'tabuleiroView': tabuleiroView, 'pontos': pontos, 'hash': meuHash}

@get('/perdeu')
@view('perdeu')
def retornaTabuleiroview():
	return {'tabuleiroView': tabuleiroView, 'porta': porta, 'pontos': pontos, 'hash': meuHash}


@post('/jogada')
def atualizaTabuleiroView():
    global pontos
    global estado
    
    x = int(request.forms.get('x'))-1
    y = int(request.forms.get('y'))-1

    if (tabuleiro[x][y] < 10 and tabuleiro[x][y] != 0):
    	tabuleiroView[x][y] = tabuleiro[x][y]
    	pontos = pontos + tabuleiro[x][y]
    if (tabuleiro[x][y] >= 10):
    	for i in range(len(tabuleiro)):
    		for j in range(len(tabuleiro)):
    			if tabuleiro[i][j] >= 10:
    				tabuleiroView[i][j] = '*'
    	
    	estado="morto"			
    	redirect('/perdeu')

    if (tabuleiro[x][y] == 0):
    	verificaVizinho(x,y)

    #print(tabuleiroView)	
    redirect('/tabuleiro')


def verificaVizinho(x,y):

	if tabuleiro[x][y] == 0:
		tabuleiroView[x][y] = 0
		tabuleiro[x][y] = -1
		if y > 0:
			if tabuleiro[x][y-1] == 0:
				verificaVizinho(x,y-1)
		if y < 9:
			if tabuleiro[x][y+1] == 0:
				verificaVizinho(x,y+1)
		if x > 0:
			if tabuleiro[x-1][y] == 0:
				verificaVizinho(x-1,y)
		if x < 9:
			if tabuleiro[x+1][y] == 0:
				verificaVizinho(x+1,y)
		if x > 0 and y > 0:
			if tabuleiro[x-1][y-1] == 0:
				verificaVizinho(x-1,y-1)
		if x > 0 and y < 9:
			if tabuleiro[x-1][y+1] == 0:
				verificaVizinho(x-1,y+1)
		if x < 9 and y > 0:
			if tabuleiro[x+1][y-1] == 0: #aqui
				verificaVizinho(x+1,y-1)
		if x < 9 and y < 9:
			if tabuleiro[x+1][y+1] == 0:
				verificaVizinho(x+1,y+1)

@get('/peers')
def index():
	return json.dumps(peers)

@get('/campo')
def index():
	return json.dumps(tabuleiroView)

@get('/pontos')
def index():
	return json.dumps(pontos)

@get('/estado')
def index():
	return json.dumps(estado)		

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
	time.sleep(7)
	

	while True:
		 
		nm = []
		for p in peers:
			print("entrouuuuuuuuuuu")
			m = requests.get(p + '/campo')
			pon = requests.get(p + '/pontos')
			e = requests.get(p + '/estado')

			e = json.loads(e.text)
			valor = json.loads(m.text)
			ponts = json.loads(pon.text)

			print(valor)
			
			prencheTabuleiro(valor)
			atualizaPontos(ponts, p, e)

		time.sleep(2)

def prencheTabuleiro(valor):
	i=0
	j=0
	for i in range (len(tabuleiroView)):
		for j in range (len(valor)):
			if tabuleiroView[i][j] != valor[i][j] and (valor[i][j]!='-' and tabuleiroView[i][j] =='-') and valor[i][j]!='*':
				tabuleiroView[i][j] = valor[i][j]		

	
def atualizaPontos(pt, p, e):
	global meuHash
	st = str(pt)
	st = st + "  | " + "  Estado : " + e 
	meuHash[p] = st 
	#meuHash.add((p, pt))
		
			
t1 = threading.Thread(target=clientePeers)
t1.start()

t2 = threading.Thread(target=clienteMessages)
t2.start()


run(host='localhost', port=porta)
