import streamlit as st
import time
import datetime
import pytz
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from collections import Counter

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
                autor = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                comentarios.append((texto, autor))

            next_page_token = resposta.get("nextPageToken")
            if not next_page_token:
                break

        return comentarios

    except HttpError as e:
        st.error(f"Erro ao acessar a API: {e}")
        return []

# Função de contagem personalizada
def contar_mencoes(comentarios):
    eqt = []
    lipe = []
    pike = []
    autores_eqt = Counter()

    for texto, autor in comentarios:
        if "elas que toquem" in texto or "eqt" in texto:
            eqt.append((texto, autor))
            autores_eqt[autor] += 1
        if "lipe" in texto:
            lipe.append((texto, autor))
        if "naquele pike" in texto or "pike" in texto:
            pike.append((texto, autor))

    total_eqt = len(eqt)
    total_lipes = len(lipe)
    total_pike = len(pike)
    total_unico = set(eqt + lipe + pike)

    return {
        "Elas que toquem / EQT": total_eqt,
        "Lipe": total_lipes,
        "Naquele Pike / Pike": total_pike,
        "Total (comentários únicos)": len(total_unico),
        "Último comentário 'Elas que toquem'": eqt[-1] if eqt else ("Nenhum comentário", ""),
        "Ranking dos 10 usuários mais comentados (EQT)": autores_eqt.most_common(10)
    }, eqt

# Função de contagem regressiva
def contagem_regressiva():
    br_tz = pytz.timezone('America/Sao_Paulo')
    data_final = datetime.datetime(2025, 5, 12, 18, 0, 0, 0)
    data_final = br_tz.localize(data_final)

    agora = datetime.datetime.now(br_tz)
    delta = data_final - agora

    if delta.total_seconds() <= 0:
        return "O evento já aconteceu!"
    else:
        dias = delta.days
        horas, resto = divmod(delta.seconds, 3600)
        minutos, segundos = divmod(resto, 60)
        return f"{dias} dias, {horas} horas, {minutos} minutos e {segundos} segundos"

# Interface Streamlit
st.set_page_config(page_title="TORCIDA EQT - Contador de Comentários YouTube", layout="centered")
st.title("TORCIDA EQT")
st.caption("Atualiza automaticamente a cada 5 minutos")

# Exibe a contagem regressiva
st.subheader("Contagem regressiva até 18h de 12/05/2025 (Horário de Brasília):")
contagem = contagem_regressiva()
st.write(contagem)

# Busca e processa os comentários
with st.spinner("Buscando e contando comentários..."):
    comentarios = buscar_comentarios()
    resultados, eqt = contar_mencoes(comentarios)

# Exibe o último comentário do "Elas que toquem"
st.subheader("Último comentário 'Elas que toquem':")
ultimo_comentario, autor = resultados["Último comentário 'Elas que toquem'"]
st.write(f"Comentado por: {autor}")
st.write(ultimo_comentario)

# Exibe a contagem das menções
st.subheader("Resultados da contagem:")
for chave, valor in resultados.items():
    if chave != "Último comentário 'Elas que toquem'" and chave != "Ranking dos 10 usuários mais comentados (EQT)":
        st.metric(label=chave, value=valor)

# Exibe o ranking dos 10 usuários mais comentados relacionados ao "Elas que toquem"
st.subheader("Ranking dos 10 usuários que mais comentaram 'Elas que toquem' ou 'EQT':")
for i, (usuario, contagem) in enumerate(resultados["Ranking dos 10 usuários mais comentados (EQT)"]):
    st.write(f"{i+1}. {usuario}: {contagem} comentários")

# Exibe a projeção de quando "Elas que toquem" terá mais comentários
total_eqt = resultados["Elas que toquem / EQT"]
total_pike = resultados["Naquele Pike / Pike"]
if total_pike > total_eqt:
    falta_para_eqt = total_pike - total_eqt
    st.write(f"Faltam {falta_para_eqt} comentários para 'Elas que toquem' se tornar a menção com mais comentários.")
else:
    st.write("'Elas que toquem' já é a menção com mais comentários.")

# Atualiza a hora de atualização no formato de horário de Brasília
st.caption(f"Atualizado em {datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')}")
