import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="🌊 Previsão de Clima e Marés - Recife", layout="wide")
st.title("🌊 Previsão de Clima e Marés - Recife")

# Função para buscar dados de clima da API Open-Meteo
def get_weather_data():
    url = "https://api.open-meteo.com/v1/forecast?latitude=-8.05&longitude=-34.88&hourly=temperature_2m,precipitation,relative_humidity_2m,windspeed_10m&timezone=America%2FSao_Paulo"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao buscar dados de clima: Status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro de conexão com clima: {e}")
        return None

# Função para buscar dados de marés da API NOAA (ajuste a station ID para Recife)
def get_tide_data():
    # NOTA: Substitua 'your-station-id' por uma ID válida da NOAA para Recife (ex.: procure em https://tidesandcurrents.noaa.gov/)
    station_id = "your-station-id"  # Exemplo: para Recife, pode ser necessário usar uma estação próxima (ex.: 8735180 - Fernando de Noronha)
    url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?station={station_id}&date=latest&units=metric&product=predictions&interval=hilo&format=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('predictions'):
                predictions = data['predictions']
                tide_data = {
                    "mare_atual": {"altura": float(predictions[0]['v']), "status": "subindo" if predictions[0]['type'] == 'H' else "descendo"},
                    "proxima_mare": {
                        "tipo": "Alta" if predictions[1]['type'] == 'H' else "Baixa",
                        "altura": float(predictions[1]['v']),
                        "hora": predictions[1]['t'].split(' ')[1][:5]  # Extrai apenas HH:MM
                    },
                    "previsao": [{"hora": p['t'].split(' ')[1][:5], "altura": float(p['v'])} for p in predictions]
                }
                return tide_data
            else:
                st.error("Nenhum dado de maré encontrado na resposta da NOAA")
                return None
        else:
            st.error(f"Erro ao buscar dados de maré: Status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro de conexão com marés: {e}")
        return None

# Buscar dados
weather = get_weather_data()
tides = get_tide_data()

# Layout com colunas
col1, col2, col3 = st.columns([2, 1, 1])

# Seção de Clima
with col1:
    st.subheader("Condições Atuais")
    if weather:
        now = datetime.now()
        current_hour_index = next((i for i, t in enumerate(weather['hourly']['time']) if datetime.fromisoformat(t) >= now), 0)
        clima_atual = {
            "temperatura": weather['hourly']['temperature_2m'][current_hour_index],
            "precipitacao": weather['hourly']['precipitation'][current_hour_index],
            "umidade": weather['hourly']['relative_humidity_2m'][current_hour_index],
            "vento": weather['hourly']['windspeed_10m'][current_hour_index]
        }
        st.write(f"🌡️ Temperatura: {clima_atual['temperatura']}°C")
        st.write(f"🌧️ Precipitação: {clima_atual['precipitacao']}mm")
        st.write(f"💧 Umidade: {clima_atual['umidade']}%")
        st.write(f"💨 Vento: {clima_atual['vento']}km/h")
    else:
        st.write("Dados de clima indisponíveis")

# Seção de Marés
with col2:
    st.subheader("Marés")
    if tides:
        st.write(f"🌊 Maré Atual: {tides['mare_atual']['altura']}m ({tides['mare_atual']['status']})")
        st.write(f"Próxima Maré: {tides['proxima_mare']['tipo']} {tides['proxima_mare']['altura']}m às {tides['proxima_mare']['hora']}")
    else:
        st.write("Dados de maré indisponíveis")

# Seção de Risco de Alagamento
with col3:
    st.subheader("Risco de Alagamento")
    if weather and tides:
        precipitacao = float(clima_atual['precipitacao'])
        altura_mare = tides['mare_atual']['altura']
        pontos = 0
        motivos = []
        if precipitacao > 30: pontos += 3; motivos.append('🌧️ Chuva alta')
        elif precipitacao > 10: pontos += 1; motivos.append('🌧️ Chuva moderada')
        if altura_mare > 2: pontos += 2; motivos.append('🌊 Maré alta')
        elif altura_mare > 1.5: pontos += 1; motivos.append('🌊 Maré moderada')
        if precipitacao > 10 and altura_mare > 1.5: pontos += 2; motivos.append('🌧️🌊 Combinação de chuva e maré')
        risco = 'alto' if pontos >= 5 else 'moderado' if pontos >= 2 else 'baixo'
        st.write(f"Risco: **{risco.upper()}**")
        if motivos:
            st.write("Motivos:", ", ".join(motivos))
        else:
            st.write("Sem motivos significativos")
    else:
        st.write("Dados insuficientes para calcular o risco")

# Gráfico de Previsão de Maré
st.subheader("Previsão de Maré")
if tides and tides['previsao']:
    df = pd.DataFrame(tides['previsao'])
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M').dt.time
    fig, ax = plt.subplots()
    ax.plot(df['hora'], df['altura'], marker='o', color='#64B5F6')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Altura (m)')
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)
else:
    st.write("Dados de previsão de maré indisponíveis")
