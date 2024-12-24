FROM python:3.10-slim

# Atualizar o sistema e instalar dependências essenciais
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho
WORKDIR /app

# Instalar Flask e Flask-SocketIO
RUN pip install --no-cache-dir flask flask_socketio

# Clonar o repositório do GitHub
RUN git clone https://github.com/AndersonSheep/ito_game_online .

# Expor a porta 5000 para o Flask
EXPOSE 5111

# Comando para iniciar o servidor
CMD ["python", "app.py"]
