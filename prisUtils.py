class ServerState:
    WAITING_FOR_PLAYERS = 0
    PLAYING = 1
    GAME_OVER = 2
    

MSG_P_INIT = 'player_init'         #Player asking for permision to play
MSG_S_FULL = 'server_full'         #Server anoucing full
MSG_S_OK = 'ok'                    #Server agrees

MSG_P_REQ_SCORE = 'what is my score'      #Player asking for current score
MSG_REQ_GAME_LIST = 'get me the gamelist' #Ask server for the game list
MSG_S_ILEGAL = 'ilegal request'

MSG_P_MOVE = 'move'                     #Sending player's move
MSG_S_MOVE_RESULTS = 'move results'


MSG_TERMINATE_SERVER = 'kill_server'    #Bad Bad server