import streamlit as st
import time
import datetime
import pandas as pd
import altair as alt
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configurações da API
API_KEY = "AIzaSyDLbPSra3ZtCvVz5Zjw9GYIeidTjfvkimY"
VIDEO_ID = "9dgFAzOGM1w"

# Inicializa a API
@st.cache_data(ttl=300)
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

# Função de contagem personalizada
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

    total_unico = eqt.union(lipe).union(pike)
    return {
        "Elas que toquem / EQT": len(eqt),
        "Lipe": len(lipe),
        "Naquele Pike / Pike": len(pike),
        "Total (comentários únicos)": len(total_unico)
    }

# Gerar gráfico de barras
def gerar_grafico(resultados):
    data = {
        'Categoria': ['Elas que toquem / EQT', 'Lipe', 'Naquele Pike / Pike', 'Total (comentários únicos)'],
        'Contagem': [resultados["Elas que toquem / EQT"], resultados["Lipe"], resultados["Naquele Pike / Pike"], resultados["Total (comentários únicos)"]]
    }
    df = pd.DataFrame(data)
    
    chart = alt.Chart(df).mark_bar().encode(
        x='Categoria',
        y='Contagem'
    )
    st.altair_chart(chart, use_container_width=True)

# Interface Streamlit
st.set_page_config(page_title="Contador de Comentários YouTube", layout="centered")
st.title("Contador de Comentários no YouTube")
st.caption("Atualiza automaticamente a cada 5 minutos")

with st.spinner("Buscando e contando comentários..."):
    comentarios = buscar_comentarios()
    resultados = contar_mencoes(comentarios)

st.subheader("Resultados")
for chave, valor in resultados.items():
    st.metric(label=chave, value=valor)

# Exibir gráfico
gerar_grafico(resultados)

st.caption(f"Atualizado em {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
