from socket import *
import thread
from prisUtils import *
import pickle
import uuid

class Game:
    """Basic information about the game
    
    Class holding all relevant information about the game. You can
    describe different games and put it the initialization of the server
    """
    numPlayers = 2	
    numRounds = 150
    payofs = [[(1,1), (0,2)], [(2,0), (0,0)]]
    
    def getResults(self, strat): # strategies is vector of played strategies
        return self.payofs[strat[0]][strat[1]]

    def isValid(self, pIndex, strategy):
        return strategy == 0 or strategy == 1

class Player:
#	""" Class holding information about the player"""
    def __init__(self, n, addr, p, ind):
        self.tag = str(uuid.uuid4())
        self.points = 0
        self.nick = n
        self.addr = addr
        self.port = p
        self.index = ind
        
    def __str__(self):
        return 'Name : {0} \t Addr : {1}:{2} \t Points : {3} '.format(self.nick, self.addr, self.port, self.points)

class PrisServer:
    def __init__(self, p, game):
        self.game = game
        self.MAX_PLAYER = game.numPlayers
        self.PORT = p
        self.HOST = ''
        self.ADDR = (self.HOST, self.PORT)
        self.BUFSIZE = 4096
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.ADDR))
        
        self.moveLock = thread.allocate_lock()
        self.playerLocl = thread.allocate_lock()
        
        self.restartGame()
        
    def restartGame(self):
        self.state = ServerState.WAITING_FOR_PLAYERS
        self.playerList = {}
        self.gameSheet = []   
        self.currentRound = {}
        
    def listen(self):
        self.sock.listen(5)    #5 is the maximum number of queued connections we'll allow
        while 1:
            conn, addr = self.sock.accept() #accept the connection
            thread.start_new_thread(self.handleConnection, (conn, addr))
        
    def start(self):
        thread.start_new_thread(self.listen, ())
        print 'Server started '
        while 1:
            r = raw_input()
            if r in ['quit', 'exit', 'q']:
                break
            elif r in ['reset', 'restart', 'r']:
                self.restartGame()
            elif r == 'lp':
                for p in self.playerList.itervalues():
                    print p
            elif r == 'lg':
                for i,r in enumerate(self.gameSheet):
                    print '{0}. {1}'.format(i+1, r)
            elif r in ['help', 'h']:
                pass
            else:
                print 'Unknown command'
        
        print 'Server ending'
        self.sock.close()
        
    def changeState(self, nState):
        print 'STATE CHANGE'
        self.state = nState
    
    def addMove(self, pTag, pMove):
        
        self.moveLock.acquire()
        
        if pTag in self.playerList: 
            self.currentRound[pTag] = pMove
            
        
        if len(self.currentRound) == len(self.playerList): #Round complete
            print 'Round complete'
            
            resVector = range(self.MAX_PLAYER)
            for p in self.playerList.itervalues():
                resVector[p.index] = self.currentRound[p.tag]
            
            result = self.game.getResults(resVector)
            roundSummary = []
            for p in self.playerList.itervalues():
                roundSummary.append([p.nick, self.currentRound[p.tag], result[p.index]])
                p.points = p.points + result[p.index]
            
            msg = [MSG_S_MOVE_RESULTS, len(self.gameSheet) + 1, roundSummary]
            
            addList = []
            for p in self.playerList.itervalues():
                addList.append((p.addr, p.port))
                
            self.sendToAll(addList, pickle.dumps(msg))
            
            self.gameSheet.append(roundSummary)
            self.currentRound = {}
            
            if len(self.gameSheet) == self.game.numRounds:
                self.changeState(ServerState.GAME_OVER)
                
        self.moveLock.release()
            
    def sendToAll(self, adrList, msg):
        for address in adrList:
            cli = socket( AF_INET,SOCK_STREAM)
            cli.connect((address))
            cli.send(msg)
            cli.close() 
            
    def handleConnection(self, clientSocket, clientAddr):
        sMsg = clientSocket.recv(self.BUFSIZE)
        msg = pickle.loads(sMsg)
        
        if msg[0] == MSG_TERMINATE_SERVER:
            print 'Please don\'t kill me!'
            
            
        elif msg[0] == MSG_P_INIT: #New player asking for right to play
            if self.state == ServerState.WAITING_FOR_PLAYERS:
                self.playerLocl.acquire()
                nPlayer = Player(msg[1], clientAddr[0], msg[2],len(self.playerList))
                self.playerList[nPlayer.tag] = nPlayer
                clientSocket.send(pickle.dumps([MSG_S_OK, nPlayer.tag, self.game.numRounds]))
                        
                if len(self.playerList) == self.MAX_PLAYER: 
                    self.changeState(ServerState.PLAYING) 
                self.playerLocl.release()
            else:
                clientSocket.send(pickle.dumps([MSG_S_FULL]))
        elif msg[0] == MSG_P_MOVE:
            if self.state == ServerState.PLAYING:
                if msg[1] in self.playerList and self.game.isValid(self.playerList[msg[1]].index, msg[2]):
                    clientSocket.send(pickle.dumps([MSG_S_OK]))
                    self.addMove(msg[1], msg[2])
                else:
                    clientSocket.send(pickle.dumps([MSG_S_ILEGAL]))
            else:
                clientSocket.send(pickle.dumps([MSG_S_ILEGAL]))
        else:
            print 'ILEGAL'
            clientSocket.send(pickle.dumps([MSG_S_ILEGAL]))
            
        clientSocket.close()
        
            
server = PrisServer(29876, Game())
server.start()
