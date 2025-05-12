import streamlit as st
import time
import datetime
import pytz  # Para manipulação do fuso horário de Brasília

# Função para calcular a contagem regressiva até 18h do dia 12/05/2025 (Horário de Brasília)
def contagem_regressiva():
    # Fuso horário de Brasília
    br_tz = pytz.timezone('America/Sao_Paulo')

    # Data e hora de destino (18h de 12/05/2025 em horário de Brasília)
    data_final = datetime.datetime(2025, 5, 12, 18, 0, 0, 0)
    data_final = br_tz.localize(data_final)  # Certifica-se de que a data está no horário correto

    # Hora atual em Brasília
    agora = datetime.datetime.now(br_tz)

    # Calculando a diferença
    delta = data_final - agora

    # Se já passou da data final
    if delta.total_seconds() <= 0:
        return "O evento já aconteceu!"
    else:
        # Exibe o tempo restante de forma legível
        dias = delta.days
        horas, resto = divmod(delta.seconds, 3600)
        minutos, segundos = divmod(resto, 60)
        return f"{dias} dias, {horas} horas, {minutos} minutos e {segundos} segundos"

# Interface Streamlit
st.set_page_config(page_title="Contador de Comentários YouTube", layout="centered")
st.title("TORCIDA EQT")
st.caption("Atualiza automaticamente a cada 5 minutos")

# Exibe a contagem regressiva
st.subheader("Contagem regressiva até 18h de 12/05/2025 (Horário de Brasília):")
contagem = contagem_regressiva()
st.write(contagem)

# Simula a busca de comentários, você pode adicionar aqui a parte de busca de comentários do YouTube
# Exemplo fictício
st.subheader("Exemplo de resultado de contagem:")
st.metric(label="Comentários 'Elas que toquem' ou 'EQT'", value=1752)
st.metric(label="Comentários 'Lipe'", value=856)
st.metric(label="Comentários 'Naquele Pike' ou 'pike'", value=3498)

# Atualiza a hora de atualização no formato de horário de Brasília
st.caption(f"Atualizado em {datetime.datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')}")
