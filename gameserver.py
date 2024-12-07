import logging
from random import randint
from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="http://localhost:8000")

players = {}
pellets = {}

@socketio.on('connect')
def connect_handler():
    print("Attempted Connection")
    id = request.args["id"]
    color = request.args["color"]
    if id != "null":
        players[id] = {"id":id,
                        "color":color,
                        "x":0,
                        "y":0,
                        "size":25
                        }  
        emit('players', players, broadcast=True )
        emit('pellets', pellets, broadcast=True)

        socket_id = request.sid  
        print(f"Client ({id}) connected with socket ID: {socket_id}")

@socketio.on('players')
def players_handler(info):
    players[info["id"]] = {"id":info["id"],
                           "x":info["x"],
                           "y":info["y"],
                           "color":info["color"],
                           "size":info["size"]}  
    #print(players)
    emit('players', players, broadcast=True )

@socketio.on('pellets')
def pellets_handler(info):
    if info in pellets:
        del pellets[info]

    emit('pellets',info,broadcast=True)

if __name__ == '__main__':
    #Suppress Flask messages
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  
    app.logger.setLevel(logging.ERROR)
    for i in range(20):
        x = randint(-1000,1000)
        y = randint(-1000,1000)
        pellets[i] = {"x":x,"y":y,"color":"magenta"}
    print(pellets)
    socketio.run(app, port=5000, log_output=False, debug=False)
