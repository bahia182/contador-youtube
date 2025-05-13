import streamlit as st
import time
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import io

# Configurações
API_KEY = "AIzaSyCbP1ImYpiuWrw0LaRq4K9_L9csu5rRZGs"
VIDEO_ID = "9dgFAzOGM1w"

# Layout da página
st.set_page_config(page_title="TORCIDA EQT", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #1a1a2e;
            color: white;
        }
        .stApp {
            background: linear-gradient(to bottom right, #1f0036, #3d0066);
        }
        .block-container {
            padding: 2rem;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ff66c4;
        }
        .stMetric > div {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 10px;
        }
        input {
            background-color: #333;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📣 TORCIDA EQT")
st.caption("Acompanhe em tempo real as menções no vídeo oficial!")

# Função para buscar comentários do YouTube
@st.cache_data(ttl=300)
def buscar_comentarios():
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        comentarios = []
        autores = []
        timestamps = []  # Lista para armazenar os timestamps dos comentários
        next_page_token = None

        while True:
            resposta = youtube.commentThreads().list(
                part="snippet",
                videoId=VIDEO_ID,
                maxResults=100,
                pageToken=next_page_token
            ).execute()

            for item in resposta["items"]:
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                texto = snippet["textDisplay"].lower()
                autor = snippet["authorDisplayName"]
                data = snippet["publishedAt"]
                comentarios.append(texto)
                autores.append((autor, texto, data))
                timestamps.append(data)  # Armazenar timestamp do comentário

            next_page_token = resposta.get("nextPageToken")
            if not next_page_token:
                break

        return comentarios, autores, timestamps

    except HttpError as e:
        st.error(f"Erro ao acessar a API: {e}")
        return [], [], []

# Função de contagem personalizada
def contar_mencoes_por_hora(comentarios, autores, timestamps):
    # Dicionário para armazenar as contagens por hora
    contagens_por_hora = {'eqt': [], 'lipe': [], 'pike': []}
    autores_eqt = []
    ultimo_eqt = None

    # Inicializa as horas
    horas = pd.to_datetime(timestamps).dt.hour.unique()
    
    # Inicializa os contadores para cada hora
    for hora in horas:
        contagens_por_hora['eqt'].append(0)
        contagens_por_hora['lipe'].append(0)
        contagens_por_hora['pike'].append(0)

    for i, comentario in enumerate(comentarios):
        comentario_lower = comentario.lower()
        hora_comentario = pd.to_datetime(timestamps[i]).hour  # Hora do comentário

        if "elas que toquem" in comentario_lower or "eqt" in comentario_lower:
            contagens_por_hora['eqt'][hora_comentario] += 1
            autores_eqt.append(autores[i][0])
            ultimo_eqt = autores[i]

        if "lipe" in comentario_lower:
            contagens_por_hora['lipe'][hora_comentario] += 1

        if "naquele pike" in comentario_lower or "pike" in comentario_lower:
            contagens_por_hora['pike'][hora_comentario] += 1

    return contagens_por_hora, horas, ultimo_eqt

# ⏳ Contagem regressiva
def contagem_regressiva():
    fuso_brasilia = pytz.timezone("America/Sao_Paulo")
    agora = datetime.datetime.now(fuso_brasilia)
    alvo = fuso_brasilia.localize(datetime.datetime(2025, 5, 12, 18, 0, 0))
    restante = alvo - agora
    return restante

# Interface
with st.spinner("Buscando comentários..."):
    comentarios, autores, timestamps = buscar_comentarios()
    contagens_por_hora, horas, ultimo_eqt = contar_mencoes_por_hora(comentarios, autores, timestamps)

# Gráfico de evolução horária
st.subheader("📊 Evolução Horária das Menções 'Elas que Toquem'")

# Gerar o gráfico
plt.figure(figsize=(10, 6))
plt.plot(horas, contagens_por_hora['eqt'], label="EQT", marker='o', color='magenta')
plt.plot(horas, contagens_por_hora['lipe'], label="Lipe", marker='o', color='cyan')
plt.plot(horas, contagens_por_hora['pike'], label="Pike", marker='o', color='yellow')

plt.title("Evolução Horária das Menções 'Elas que Toquem'")
plt.xlabel("Hora do Comentário")
plt.ylabel("Quantidade de Menções")
plt.xticks(horas, rotation=45)
plt.legend()
plt.grid(True)

# Exibir gráfico
st.pyplot(plt)

# Último comentário relevante
if ultimo_eqt:
    nome, texto, data = ultimo_eqt
    data_formatada = datetime.datetime.fromisoformat(data.replace("Z", "+00:00"))
    data_br = data_formatada.astimezone(pytz.timezone("America/Sao_Paulo")).strftime('%d/%m/%Y %H:%M')
    st.subheader("📌 Último comentário sobre 'Elas que toquem'")
    st.markdown(f"**{nome}** ({data_br}): _{texto}_")

# Rodapé
data = datetime.datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%d/%m/%Y %H:%M:%S')
st.caption(f"📡 Atualizado em {data}")
st.markdown("---")
st.markdown("💬 [Clique aqui para ir ao vídeo e comentar!](https://youtu.be/9dgFAzOGM1w)")
