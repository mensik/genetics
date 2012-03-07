##client.py
from socket import *
from prisUtils import *
import pickle
import thread
from warnings import catch_warnings

class GameInfo:
    myMoves = []
    oppMoves = []
    numRounds = 0
 
def sendTheMove(tag, strategy, gameInf = GameInfo()):

    succes = 0
    while succes == 0:
        
        t = strategy(gameInf)
        msg = [MSG_P_MOVE, tag, t]
    
        cli = socket(AF_INET, SOCK_STREAM)
        cli.connect((ADDR))
        cli.send(pickle.dumps(msg))
        sMsg = cli.recv(BUFSIZE)
        msg = pickle.loads(sMsg)
        
        if msg[0] == MSG_S_OK:
            succes = 1
   
        cli.close()
        
def userInput(gameInf):
    succes = 0
    while succes == 0:
        try:
            t = int(raw_input())
        except ValueError:
            continue
        succes = 1
    return t
  
def titForTat(gameInf):
    t = 0
    if len(gameInf.oppMoves) > 0:
        t = gameInf.oppMoves[-1]
    
    return t

def smejd(gameInf):
    t = 0
    if len(gameInf.oppMoves) > 0:
        t = gameInf.oppMoves[-1]
    
    if len(gameInf.oppMoves) + 1== gameInf.numRounds:
        t = 1
    
    return t
      
HOST = 'localhost'
PORT = 29876
ADDR = (HOST, PORT)
BUFSIZE = 4096

cli = socket(AF_INET, SOCK_STREAM)
cli.connect((ADDR))


srv = socket(AF_INET, SOCK_STREAM)
srv.bind(('', 0))
MYPORT = srv.getsockname()[1]

nick = raw_input('Nick: ')

msg = [MSG_P_INIT, nick, MYPORT]
cli.send(pickle.dumps(msg))
sMsg = cli.recv(BUFSIZE)
msg = pickle.loads(sMsg)
cli.close()

completedRound = 0

roundList = []

numRounds = msg[2]
gameInf = GameInfo()
gameInf.numRounds = numRounds

print 'Num rounds {0}'.format(numRounds)

if msg[0] == MSG_S_OK:
    tag = msg[1]
    
    strategy = userInput
    
    if nick == 'tit':
        print 'TITfotTAT'
        strategy = titForTat
    elif nick == 'smejd':
        print 'SMEJD strategy'
        strategy = smejd
        
    srv.listen(2)
    
    sendTheMove(tag, strategy, gameInf)
    
    while 1:
        conn, addr = srv.accept()
        sMsg = conn.recv(BUFSIZE)
        conn.close()
        
        msg = pickle.loads(sMsg)
        #print msg
        print '{0}. round: {1}'.format(msg[1], msg[2])
        completedRound = msg[1]
        roundList.append(msg[2])
        
        if msg[2][0][0] == nick:
            gameInf.myMoves.append(msg[2][0][1])
            gameInf.oppMoves.append(msg[2][1][1])
        else:
            gameInf.myMoves.append(msg[2][1][1])
            gameInf.oppMoves.append(msg[2][0][1])
        
        if completedRound >= numRounds:
            break
        sendTheMove(tag, strategy, gameInf)

#FINISH
                    
for i in range(2):
    score = 0 
    for r in roundList:
        score = score + r[i][2]
    
    print '\nPlayer {0} has score {1}'.format(roundList[0][i][0], score)

srv.close()