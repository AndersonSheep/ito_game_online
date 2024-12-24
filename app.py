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


temas_do_jogo = {
    1: "Mangá / anime famoso (1 desconhecido ---- 100 famoso)",
    2: "Pessoas famosas que você gostaria de ser (1 não gostaria de ser ---- 100 gostaria de ser)",
    3: "Coisas que te dão medo (1 nem um sustinho ---- 100 morreria de medo)",
    4: "Coisas que você gostaria de fotografar (1 não vale o clique ---- 100 faria um book)",
    5: "Coisas importantes na vida (1 não é nada ---- 100 importantíssimo)",
    6: "Esportes mais conhecidos (1 pouca gente conhece ---- 100 muito popular)",
    7: "Contos de fadas populares (1 desconhecido ---- 100 popular)",
    8: "Personagens da ficção com quem você gostaria de ter um encontro (1 não valeria um encontro ---- 100 provavelmente casaria)",
    9: "Lugares onde você gostaria de morar (1 não ficaria lá 5 minutos ---- 100 passaria lá a eternidade)",
    10: "Poderes especiais que você gostaria de ter (1 não gostaria ---- 100 gostaria)",
    11: "Filmes conhecidos (1 ninguém viu ---- 100 todo mundo assistiu)",
    12: "Itens do dia a dia que poderiam ser boas armas (1 nem arranha ---- 100 arma forte)",
    13: "Coisas que você não conseguiria perdoar (1 nada demais ---- 100 imperdoável)",
    14: "Coisas nas quais você gostaria de ficar em imersão (1 não, obrigado ---- 100 quero uma piscina cheia disso)",
    15: "Coisas que você ficaria olhando com admiração o dia inteiro (1 nem pararia pra olhar ---- 100 ficaria olhando por horas)",
    16: "Mentiras que você acreditaria (1 não acreditaria ---- 100 acreditaria com certeza)",
    17: "Sabores de sorvete que poderiam ser deliciosos (1 credo, horrível ---- 100 comeria toneladas)",
    18: "Habilidades importantes para ser líder (1 não é nada ---- 100 essencial)",
    19: "Coisas que te fazem feliz (1 não te faz feliz ---- 100 felicidade pura)",
    20: "Itens / armas que você gostaria de ter para lutar contra zumbis (1 é pra fazer cosquinha ---- 100 adiós, zumbi!)",
    21: "Atletas famosos (1 sei nem quem é ---- 100 grande campeão)",
    22: "Comidas famosas (1 desconhecido ---- 100 encontradas em todo o mundo)",
    23: "Personagens da ficção que você gostaria de ser (1 não seria ---- 100 seria muito)",
    24: "Celebridades de filmes e séries mais conhecidas da atualidade (1 fez poucas participações ---- 100 está sempre nos lançamentos)",
    25: "Coisas que cheiram bem (1 cheiro normal ---- 100 faria um perfume disso)",
    26: "Coisas que você gostaria de ter como souvenir (1 não teria ---- 100 teria mais de mil)",
    27: "Coisas que você gostaria de fazer quando se aposentar (1 não faria ---- 100 faria com toda certeza)",
    28: "Coisas difíceis de suportar (1 nem tão difícil ---- 100 praticamente impossível)",
    29: "Coisas importantes para fazer sucesso nas mídias sociais (1 pouco importante ---- 100 obrigatório)",
    30: "Habilidades essenciais para um comediante (1 desnecessária ---- 100 obrigatória)",
    31: "Coisas pesadas (1 levinho ---- 100 pesado)",
    32: "Canções famosas (1 ninguém conhece ---- 100 todo mundo canta junto)",
    33: "Figuras históricas populares (1 sei nem quem é ---- 100 figura importante)",
    34: "Marcas mais valiosas (1 vale pouco ---- 100 vale bilhões)",
    35: "Coisas que você desejava quando criança (1 nem queria ---- 100 queria pra caramba)",
    36: "Coisas que você quer fazer logo quando acorda (1 não quero fazer ---- 100 quero muito)",
    37: "Coisas úteis em uma casa (1 inútil ---- 100 muito útil)",
    38: "Sons que te fazem feliz (1 nem é som ---- 100 felicidade para os ouvidos)",
    39: "Coisas que fazem você se sentir amado(a) (1 não faz ---- 100 é puro amor)",
    40: "Pense como um estudante do ensino médio: o que é legal? (1 cringe ---- 100 super legal)",
    41: "Presentes de aniversário mais comuns (1 ninguém ganha ---- 100 todo mundo já ganhou)",
    42: "Vilões mais temíveis (1 até eu encarava ---- 100 me faz ter pesadelos)",
    43: "Países populares para viajar (1 ninguém vai ---- 100 todo mundo já foi)",
    44: "Coisas fofinhas (1 pouco fofinho ---- 100 um cuti-cuti)",
    45: "Coisas que te fazem feliz quando feitas pelo seu amor (1 pouco feliz ---- 100 muito feliz)",
    46: "Atividades difíceis de serem feitas sozinho(a) (1 dá pra fazer ---- 100 impossível)",
    47: "Animais nos quais você gostaria de montar (1 não gostaria ---- 100 queria demais)",
    48: "Habilidades úteis para o trabalho (1 inútil ---- 100 muito útil)",
    49: "Pense como uma criança: o que te faz feliz? (1 não te faz muito feliz ---- 100 isso sim é felicidade)",
    50: "Pense como um gato: os lugares mais confortáveis do mundo (1 pouco confortável ---- 100 muito confortável)",
    51: "Tamanho de animais (1 pequeno ---- 100 enorme)",
    52: "Lugares onde você vai com frequência (1 vai pouco ---- 100 vai muito)",
    53: "Brinquedos mais conhecidos (1 desconhecido ---- 100 toda criança já teve um)",
    54: "Palavras que você gostaria de ouvir (1 praticamente uma ofensa ---- 100 mais que um elogio)",
    55: "Coisas leves (1 pouco leve ---- 100 levíssimo)",
    56: "Drinques populares (1 ninguém bebe isso ---- 100 todo mundo já bebeu)",
    57: "Coisas que te deixam com sono (1 acordadíssimo ---- 100 zzzzz…)",
    58: "Veículos mais comuns (1 nunca vi ---- 100 tem um em cada esquina)",
    59: "Frases estranhas se ditas por uma criança de 5 anos (1 normal ---- 100 muito estranho)",
    60: "Pedidos de casamento que te fariam feliz (1 aquele de passar vergonha ---- 100 algo memorável)",
    61: "Itens úteis quando você está perdido(a) no deserto (1 não serve para nada ---- 100 salvaria sua vida)",
    62: "Coisas que te surpreenderiam se saíssem do seu corpo (1 algo comum ---- 100 não dá pra imaginar isso)",
    63: "Algo que te surpreenderia se fosse achado embaixo de uma pedra no parque (1 algo comum ---- 100 algo surpreendente)",
    64: "Itens encontrados em um baú do tesouro que você gostaria de ter (1 não gostaria ---- 100 queria muito)",
    65: "Momentos históricos que você visitaria se tivesse uma máquina do tempo (1 fuja, louco! ---- 100 iria agora)",
    66: "Alimentos que fazem bem (1 nada saudável ---- 100 puro suco de saúde)",
    67: "Coisas confiáveis por todo o sempre (1 pouco confiável ---- 100 confiável eternamente)",
    68: "Tipos de festivais que você gostaria de participar (1 não iria nem pagando ---- 100 gastaria o salário pra ir)",
    69: "Pense como um vilão: qual seria o personagem heróico que você menos gostaria de enfrentar? (1 derrotaria facilmente ---- 100 tenho medo até da sombra)",
    70: "Pense como um cientista: o que você gostaria de descobrir? (1 não gostaria de descobrir ---- 100 merece um Nobel)",
    71: "Itens úteis para levar a uma ilha deserta (1 inútil ---- 100 muito útil)",
    72: "Melhores jogos de tabuleiro já lançados (1 aquele que flopou ---- 100 digno de um prêmio Spiel)",
    73: "Piadas mais engraçadas (1 isso é ofensivo ---- 100 ri litros)",
    74: "Itens diferentões que você gostaria de ter (1 nem tanto ---- 100 isso é muito legal)",
    75: "Melhores nomes de golpes especiais para gritar (1 não botou medo ---- 100 isso sim impõe respeito)",
    76: "Características de pessoas que você gostaria de ter em seu círculo de amizade (1 ninguém se importa ---- 100 BFF na certa)",
    77: "Títulos de livros que te deixariam curioso para saber seu conteúdo (1 isso é ridículo ---- 100 vou comprar)",
    78: "Pense como um mago: qual seria o seu feitiço favorito? (1 feitiço comum ---- 100 usaria toda hora)",
    79: "Pense como um cachorro: o que te faz feliz? (1 nada AU-AUdacioso ---- 100 de balançar a cauda)",
    80: "Coisas que surpreenderiam se fossem ditas por um professor (1 faz parte da aula ---- 100 por essa ninguém esperava)",
    81: "As coisas mais bonitas do mundo (1 ok ---- 100 visão do paraíso)",
    82: "Coisas populares com crianças (1 pouco conhecida ---- 100 muito famosa)",
    83: "Os doces mais conhecidos (1 nunca vi, nem comi ---- 100 vende em todo lugar)",
    84: "Os nomes mais legais (1 muito comum ---- 100 meu filho vai ter)",
    85: "Amor verdadeiro ou apenas uma aventura? (1 aventura ---- 100 amor verdadeiro)",
    86: "Coisas que você faz quando está de bom humor (1 nunca faço ---- 100 faço muito)",
    87: "Pense como um herói: qual seria sua pose? (1 lamentável ---- 100 épica)",
    88: "Pense como um explorador: que lugares te deixam animado? (1 que desânimo ---- 100 bora lá, agora?)",
    89: "Mundos imaginários que você gostaria de visitar (1 não gostaria ---- 100 viveria lá o resto da vida)",
    90: "Habilidades úteis em relacionamentos (1 inútil ---- 100 essencial)",
    91: "Personagens mais fortes da ficção (1 fraco demais ---- 100 indestrutível)",
    92: "Coisas que você ficaria feliz em encontrar no seu bolso ou bolsa (1 nada feliz ---- 100 alegria pura)",
    93: "Lugares onde mais acontecem encontros românticos (1 poucos encontros ---- 100 está acontecendo um agora)",
    94: "Caretas engraçadas (1 isso é ridículo ---- 100 muito engraçado!)",
    95: "Um único prato pra comer até o fim da vida (1 não escolheria ---- 100 comeria agora, inclusive)",
    96: "Ações e atitudes que exigem coragem (1 nada corajoso ---- 100 pura coragem)",
    97: "Pense como um adolescente: o que seria algo ruim se acontecesse durante a aula? (1 nem tão ruim ---- 100 que vergonha!)",
    98: "Se você tivesse um alter ego, o que gostaria que ele fosse? (1 não gostaria ---- 100 é meu tipo)",
    99: "Personagens fictícios com os piores temperamentos (1 de boas ---- 100 explosivo)",
    100: "Habilidades importantes para um streamer (1 desnecessária ---- 100 obrigatória)"
}


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

@socketio.on('generate_theme')
def handle_generate_theme():
    numero_aleatorio = random.randint(1, 100)
    tema = temas_do_jogo.get(numero_aleatorio, "Sem tema para esse número :(")
    emit('new_theme', {"numero": numero_aleatorio, "tema": tema}, room="game")

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
