import streamlit as st
import time
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

# Configurações da API
API_KEY = "AIzaSyDLbPSra3ZtCvVz5Zjw9GYIeidTjfvkimY"
VIDEO_ID = "9dgFAzOGM1w"

# Função para buscar comentários
@st.cache_data(ttl=300)  # Atualiza a cada 5 minutos
def buscar_comentarios():
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        comentarios = []
        next_page_token = None

        while True:
            resposta = youtube.commentThreads().list(
                part="snippet",
                videoId=VIDEO_ID,
                maxResults=100,
                pageToken=next_page_token
            ).execute()

            for item in resposta["items"]:
                texto = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"].lower()
                comentarios.append(texto)

            next_page_token = resposta.get("nextPageToken")
            if not next_page_token:
                break

        return comentarios
    except HttpError as e:
        st.error(f"Erro ao acessar a API: {e}")
        return []

# Função de contagem das menções
def contar_mencoes(comentarios):
    eqt = set()
    lipe = set()
    pike = set()

    for i, comentario in enumerate(comentarios):
        if "elas que toquem" in comentario or "eqt" in comentario:
            eqt.add(i)
        if "lipe" in comentario:
            lipe.add(i)
        if "naquele pike" in comentario or "pike" in comentario:
            pike.add(i)

    return len(eqt), len(lipe), len(pike)

# Função para contar usuários que mais comentaram
def contar_usuarios(comentarios):
    usuarios = {}
    for comentario in comentarios:
        if "elas que toquem" in comentario:
            usuario = comentario.split(":")[0]  # Assume que o formato é "Usuário: Comentário"
            usuarios[usuario] = usuarios.get(usuario, 0) + 1
    return dict(sorted(usuarios.items(), key=lambda item: item[1], reverse=True)[:10])

# Contagem regressiva até 18h
def contagem_regressiva():
    horario_brasilia = pytz.timezone('Brazil/East')
    agora = datetime.datetime.now(horario_brasilia)
    alvo = agora.replace(hour=18, minute=0, second=0, microsecond=0)
    if agora >= alvo:
        alvo = alvo + datetime.timedelta(days=1)  # Se já passou das 18h, coloca para o dia seguinte
    delta = alvo - agora
    return str(delta)

# Interface Streamlit
st.set_page_config(page_title="Ranking das Menções - Elas Que Toquem", layout="centered")
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQLLK-4pF1x36fQfCOuIxY4u7hfUfyVNnYdQg&s", use_column_width=True)

# Estilo personalizado para a página
st.markdown("""
    <style>
        .css-18e3th9 { background-color: #F28D35; }  /* Fundo vibrante */
        .css-1v3fvcr { color: #fff; font-family: 'Poppins', sans-serif; font-size: 30px; text-align: center; }
        .css-18e3th9 > .stButton > button { background-color: #F28D35; color: white; }
        .css-18e3th9 > .stButton > button:hover { background-color: #FF6F00; }
        .css-1kyxreq { color: #F28D35; font-size: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔝 Ranking das Menções - Elas Que Toquem 🔝")
st.subheader(f"Contagem regressiva até as 18h (Horário de Brasília): {contagem_regressiva()}")

comentarios = buscar_comentarios()
qtd_eqt, qtd_lipe, qtd_pike = contar_mencoes(comentarios)

# Exibe o último comentário
ultimo_comentario = comentarios[-1] if comentarios else "Nenhum comentário encontrado"
ultimo_usuario = "Usuário Exemplo"  # Ajuste isso com o nome do usuário real se disponível
st.subheader(f"Último comentário por {ultimo_usuario}")
st.write(ultimo_comentario)

# Exibe as menções
st.subheader("Menções:")
st.metric(label="Elas Que Toquem (EQT)", value=qtd_eqt)
st.metric(label="Lipe", value=qtd_lipe)
st.metric(label="Naquele Pike", value=qtd_pike)

# Faltando para EQT ser a mais comentada
total_mais_comentada = 500  # Número de menções necessárias para ser a mais comentada
falta = total_mais_comentada - qtd_eqt
st.metric(label="Faltam para EQT ser a mais comentada", value=f"{falta} menções")

# Ranking de usuários que mais comentaram sobre "
