import streamlit as st
import time
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from collections import Counter

# Configurações
API_KEY = "AIzaSyDLbPSra3ZtCvVz5Zjw9GYIeidTjfvkimY"
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
                comentarios.append(texto)
                autores.append((autor, texto))

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

    for i, comentario in enumerate(comentarios):
        if "elas que toquem" in comentario or "eqt" in comentario:
            eqt_ids.add(i)
            autores_eqt.append(autores[i][0])
        if "lipe" in comentario:
            lipe_ids.add(i)
        if "naquele pike" in comentario or "pike" in comentario:
            pike_ids.add(i)

    total_unico = eqt_ids.union(lipe_ids).union(pike_ids)
    ranking = Counter(autores_eqt).most_common(10)

    return {
        "eqt": len(eqt_ids),
        "lipe": len(lipe_ids),
        "pike": len(pike_ids),
        "total": len(total_unico),
        "ranking": ranking,
        "ultimo_eqt": autores[len(autores) - 1] if autores and (len(autores) - 1) in eqt_ids else None,
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
    st.subheader("📌 Último comentário sobre 'Elas que toquem'")
    st.markdown(f"**{resultado['ultimo_eqt'][0]}**: _{resultado['ultimo_eqt'][1]}_")

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

# Rodapé
data = datetime.datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%d/%m/%Y %H:%M:%S')
st.caption(f"📡 Atualizado em {data}")
st.markdown("---")
st.markdown("💬 [Clique aqui para ir ao vídeo e comentar!](https://youtu.be/9dgFAzOGM1w)")
