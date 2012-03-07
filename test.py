##client.py
from socket import *
import pickle

cli = socket( AF_INET,SOCK_STREAM)
cli.connect(('localhost', 59937))
cli.send(pickle.dumps('HERE'))
cli.close()
    