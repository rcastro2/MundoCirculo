from gamelib import *
import socketio

server_url = "http://127.0.0.1:5000"  
#server_url = "https://a9e22df4-6d38-4800-81fe-76912e39e471-00-3nlo3futsk1a7.janeway.repl.co/"
sio = socketio.Client()

@sio.event
def players(info):
    global members
    members = info

@sio.event
def pellets(info):
    global pellets
    if type(info) is dict:
        pellets = info
    elif info in pellets:
        del pellets[info]
    print(info)

colors = {"black":black,"white":white,"red":red,"green":green,"blue":blue,"yellow":yellow,"magenta":magenta,"cyan":cyan,"orange":orange,"pink":pink,"brown":brown,"gray":gray}

game = Game(800,600,"Delta Fighter")
bk = Image("grid.png",game)
game.setBackground(bk)
ball = Shape("ellipse",game,50,50,orange)

you = {"id":0,"color":"black","x":0,"y":0,"size":25}
members = {}
pellets = {}

direction = ""
def player_controls():
    global direction
    direction = ""
    speed = 2
    if keys.Pressed[K_LEFT]:
        you["x"] -=speed
        direction += "right"
    if keys.Pressed[K_RIGHT]:
        you["x"] +=speed
        direction += "left"
    if keys.Pressed[K_UP]:
        you["y"] -=speed 
        direction += "down"
    if keys.Pressed[K_DOWN]:
        you["y"] +=speed
        direction += "up"
    info = {"id":you["id"], 
            "x":you["x"],
            "y":you["y"],
            "color":you["color"],
            "size":you["size"]
    }
    if direction != "":
        sio.emit('players', info)
    

def display_members():
    global members
    for key in members:
        player = members[key]
        screenX = player["x"] - you["x"] + game.width / 2
        screenY = player["y"] - you["y"] + game.height / 2
        if player["id"] == you["id"]:
            screenX = game.width / 2
            screenY = game.height / 2

        width,height = player["size"],player["size"]
        left, top  = screenX-width/2,screenY-height/2
        rect = pygame.Rect(left,top,width,height)

        color = player["color"] if player["color"] in colors else white
        pygame.draw.ellipse(game.screen,color,rect)
        offsetX = len(player["id"])*4.5 
        offsetY = 40 + player["size"] / 3
        game.drawText(player["id"],screenX - offsetX,screenY - offsetY, Font(color))
        offsetX = len(f"({player['x']},{player['y']})")*3.2 + player["size"] / 8
        game.drawText(f"({player['x']},{player['y']})",screenX-offsetX,screenY + offsetY - 10,Font(color))

def display_pellets():
    global pellets
    for key in pellets:
        pellet = pellets[key]
        screenX = pellet["x"] - you["x"] + game.width / 2
        screenY = pellet["y"] - you["y"] + game.height / 2
        
        width,height = 25,25
        left, top  = screenX-width/2,screenY-height/2
        rect = pygame.Rect(left,top,width,height)

        pygame.draw.ellipse(game.screen,pellet["color"],rect)
        game.drawText(f'({key})',screenX - 10,screenY - 40, Font(pellet["color"]))
        if distance(pellet,you) < you["size"]:
            del pellets[key]
            print(f'Collision with pellet {key}')
            you["size"] += 5
            sio.emit('pellets',key)
            info = {"id":you["id"], 
                    "x":you["x"],
                    "y":you["y"],
                    "color":you["color"],
                    "size":you["size"]
                    }
            sio.emit('players', info)
            break


def game_screen():
    global direction
    while not game.over:
        game.processInput()
        game.scrollBackground(direction)
        player_controls()
        display_members()
        display_pellets()
        game.update(60)
    game.quit()

def distance(obj1, obj2):
    return math.sqrt(math.pow(obj1["x"] - obj2["x"],2) + math.pow(obj1["y"] - obj2["y"],2) )

if __name__ == "__main__":
    you["id"] = input("Enter Name: ")
    color = input("Enter Color: ")
    you["color"] = color if color in colors else "white"
    if color != you["color"]: print(f"{color} replaced with {you['color']}")
    sio.connect(server_url+f"?id={you['id']}&color='{you['color']}'")
    game_screen() 
    sio.wait()  