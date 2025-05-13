import streamlit as st
import time
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from collections import Counter
import pandas as pd
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

            next_page_token = resposta.get("nextPageToken")
            if not next_page_token:
                break

        return comentarios, autores

    except HttpError as e:
        st.error(f"Erro ao acessar a API: {e}")
        return [], []

# Função de contagem personalizada

def contar_mencoes(comentarios, autores):
    eqt_ids, lipe_ids, pike_ids = set(), set(), set()
    autores_eqt = []
    ultimo_eqt = None

    for i, comentario in enumerate(comentarios):
        comentario_lower = comentario.lower()
        if "elas que toquem" in comentario_lower or "eqt" in comentario_lower:
            eqt_ids.add(i)
            autores_eqt.append(autores[i][0])
            ultimo_eqt = autores[i]
        if "lipe" in comentario_lower:
            lipe_ids.add(i)
        if "naquele pike" in comentario_lower or "pike" in comentario_lower:
            pike_ids.add(i)

    total_unico = eqt_ids.union(lipe_ids).union(pike_ids)
    ranking = Counter(autores_eqt).most_common(10)

    return {
        "eqt": len(eqt_ids),
        "lipe": len(lipe_ids),
        "pike": len(pike_ids),
        "total": len(total_unico),
        "ranking": ranking,
        "ultimo_eqt": ultimo_eqt,
        "faltam_para_liderar": max(0, max(len(pike_ids), len(lipe_ids)) - len(eqt_ids))
    }

# ⏳ Contagem regressiva
def contagem_regressiva():
    fuso_brasilia = pytz.timezone("America/Sao_Paulo")
    agora = datetime.datetime.now(fuso_brasilia)
    alvo = fuso_brasilia.localize(datetime.datetime(2025, 5, 12, 18, 0, 0))
    restante = alvo - agora
    return restante

# Interface
with st.spinner("Buscando comentários..."):
    comentarios, autores = buscar_comentarios()
    resultado = contar_mencoes(comentarios, autores)

# Último comentário relevante
if resultado["ultimo_eqt"]:
    nome, texto, data = resultado["ultimo_eqt"]
    data_formatada = datetime.datetime.fromisoformat(data.replace("Z", "+00:00"))
    data_br = data_formatada.astimezone(pytz.timezone("America/Sao_Paulo")).strftime('%d/%m/%Y %H:%M')
    st.subheader("📌 Último comentário sobre 'Elas que toquem'")
    st.markdown(f"**{nome}** ({data_br}): _{texto}_")

# Contagem principal
st.subheader("📊 Contagem de Menções")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Elas que toquem (EQT)", resultado["eqt"], f"-{resultado['faltam_para_liderar']} para liderar")
col2.metric("Lipe", resultado["lipe"])
col3.metric("Naquele Pike", resultado["pike"])
col4.metric("Total únicos", resultado["total"])

# ⏱️ Contagem regressiva
tempo = contagem_regressiva()
st.markdown(f"🕒 **Faltam** `{str(tempo).split('.')[0]}` **para 18h de 12/05/2025 (horário de Brasília)**")

# 🏆 Ranking dos fãs da EQT
st.subheader("🔥 TOP 10 - Quem mais comenta 'Elas que toquem'")
for i, (autor, contagem) in enumerate(resultado["ranking"], start=1):
    st.markdown(f"{i}. **{autor}** – {contagem} menções")

# 🔍 Busca personalizada com autocomplete
st.subheader("🔎 Verifique suas menções 'Elas que toquem'")
nomes_disponiveis = sorted(set([autor for autor, _, _ in autores]))
nome_busca = st.selectbox("Digite seu nome de usuário:", nomes_disponiveis)
quantidade = sum(1 for a, c, _ in autores if a == nome_busca and ("elas que toquem" in c.lower() or "eqt" in c.lower()))
st.markdown(f"**{nome_busca}** comentou 'Elas que toquem' **{quantidade}** vezes.")

# Rodapé
data = datetime.datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%d/%m/%Y %H:%M:%S')
st.caption(f"📡 Atualizado em {data}")
st.markdown("---")
st.markdown("💬 [Clique aqui para ir ao vídeo e comentar!](https://youtu.be/9dgFAzOGM1w)")
