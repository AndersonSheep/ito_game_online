from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Estado inicial do jogo
def reset_game():
    return {
        "players": {},  # Armazena {player_name: {card: int, revealed: bool}}
        "order": [],  # Ordem dos jogadores
        "available_cards": list(range(1, 101)),  # Lista de cartas disponíveis
    }

game_state = reset_game()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    player_name = data['name']
    if player_name not in game_state["players"]:
        assign_card_to_player(player_name)
        join_room("game")
        game_state["order"].append(player_name)
        emit('your_card', {"card": game_state["players"][player_name]["card"]}, room=request.sid)
    emit('update_state', game_state, room="game")

def assign_card_to_player(player_name):
    random.shuffle(game_state["available_cards"])
    card_value = game_state["available_cards"].pop()
    game_state["players"][player_name] = {"card": card_value, "revealed": False}

@socketio.on('reveal_card')
def handle_reveal(data):
    player_name = data['name']
    if player_name in game_state["players"]:
        game_state["players"][player_name]["revealed"] = True
        emit('update_state', game_state, room="game")

@socketio.on('reset_game')
def handle_reset():
    global game_state
    game_state = reset_game()  # Redefine completamente o estado do jogo
    emit('game_reset', {}, room="game")  # Notifica os clientes sobre o reset

@socketio.on('update_positions')
def handle_update_positions(data):
    game_state["order"] = data["order"]
    emit('update_state', game_state, room="game")

if __name__ == '__main__':
    socketio.run(app, debug=True)
