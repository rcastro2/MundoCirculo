import logging
from random import randint
from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="http://localhost:8000")

players = {}
pellets = {}
sids = []
colors = ["black","red","green","blue","yellow","magenta","cyan","orange","pink","brown","gray"]

@socketio.on('connect')
def connect_handler():
    print("Attempted Connection")
    id = request.args["id"]
    socket_id = request.sid 
    color = request.args["color"]
    if id != "null":
        sids.append(socket_id)
        players[id] = {"id":id,
                        "color":color,
                        "x":0,
                        "y":0,
                        "size":25
                        } 
        data = {"players":players,"pellets":pellets} 
        emit('init', data, to=socket_id)

        other_players = [sid for sid in sids if sid != socket_id]
        emit('players', players[id],to=other_players)
         
        print(f"Client ({id}) connected with socket ID: {socket_id}")

@socketio.on('players')
def players_handler(info):
    players[info["id"]] = {"id":info["id"],
                           "x":info["x"],
                           "y":info["y"],
                           "color":info["color"],
                           "size":info["size"]}  
    
    other_players = [sid for sid in sids if sid != request.sid]
    emit('players', players[info["id"]], to=other_players )

@socketio.on('pellets')
def pellets_handler(info):
    if int(info) in pellets:
        del pellets[int(info)]

    other_players = [sid for sid in sids if sid != request.sid]
    emit('pellets',info,to=other_players)

if __name__ == '__main__':
    #Suppress Flask messages
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  
    app.logger.setLevel(logging.ERROR)
    for i in range(20):
        x = randint(-1000,1000)
        y = randint(-1000,1000)
        pellets[i] = {"x":x,"y":y,"color":colors[randint(0,len(colors)-1)]}
    print(pellets)
    socketio.run(app, port=5000, log_output=False, debug=False)
