import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="🌊 Previsão de Clima e Marés - Recife", layout="wide")
st.title("🌊 Previsão de Clima e Marés - Recife")

# --- Funções para dados ---
@st.cache_data(ttl=3600)
def get_weather_data():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=-8.05&longitude=-34.88"
        "&hourly=temperature_2m,precipitation,relative_humidity_2m,windspeed_10m"
        "&timezone=America%2FSao_Paulo"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao buscar dados de clima: {e}")
        return None

@st.cache_data(ttl=3600)
def get_tide_data():
    # Substitua por estação válida!
    station_id = "your-station-id"  # Exemplo: 8735180 (Fernando de Noronha)
    url = (
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
        f"?station={station_id}&date=latest&units=metric&product=predictions"
        f"&interval=hilo&format=json"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("predictions"):
            st.error("Dados de maré não encontrados.")
            return None
        predictions = data["predictions"]
        return {
            "mare_atual": {
                "altura": float(predictions[0]["v"]),
                "status": "subindo" if predictions[0]["type"] == "H" else "descendo"
            },
            "proxima_mare": {
                "tipo": "Alta" if predictions[1]["type"] == "H" else "Baixa",
                "altura": float(predictions[1]["v"]),
                "hora": predictions[1]["t"].split()[1][:5]
            },
            "previsao": [
                {"hora": p["t"].split()[1][:5], "altura": float(p["v"])}
                for p in predictions
            ]
        }
    except requests.RequestException as e:
        st.error(f"Erro ao buscar dados de maré: {e}")
        return None

def calcula_risco(precip, mare):
    pontos, motivos = 0, []
    if precip > 30:
        pontos += 3
        motivos.append("🌧️ Chuva alta")
    elif precip > 10:
        pontos += 1
        motivos.append("🌧️ Chuva moderada")
    if mare > 2:
        pontos += 2
        motivos.append("🌊 Maré alta")
    elif mare > 1.5:
        pontos += 1
        motivos.append("🌊 Maré moderada")
    if precip > 10 and mare > 1.5:
        pontos += 2
        motivos.append("🌧️🌊 Chuva + Maré")
    if pontos >= 5:
        risco = "ALTO"
    elif pontos >= 2:
        risco = "MODERADO"
    else:
        risco = "BAIXO"
    return risco, motivos

# --- Carregar dados ---
weather = get_weather_data()
tides = get_tide_data()

# --- Layout ---
col1, col2, col3 = st.columns([2, 1, 1])

# --- Clima ---
with col1:
    st.subheader("Condições Atuais")
    if weather:
        now = datetime.now()
        horas = weather["hourly"]["time"]
        idx = next((i for i, t in enumerate(horas) if datetime.fromisoformat(t) >= now), 0)
        clima = {
            "🌡️ Temperatura (°C)": weather["hourly"]["temperature_2m"][idx],
            "🌧️ Precipitação (mm)": weather["hourly"]["precipitation"][idx],
            "💧 Umidade (%)": weather["hourly"]["relative_humidity_2m"][idx],
            "💨 Vento (km/h)": weather["hourly"]["windspeed_10m"][idx]
        }
        st.metric("🌡️ Temperatura", f"{clima['🌡️ Temperatura (°C)']} °C")
        st.metric("🌧️ Precipitação", f"{clima['🌧️ Precipitação (mm)']} mm")
        st.metric("💧 Umidade", f"{clima['💧 Umidade (%)']} %")
        st.metric("💨 Vento", f"{clima['💨 Vento (km/h)']} km/h")
    else:
        st.warning("Dados de clima indisponíveis.")

# --- Marés ---
with col2:
    st.subheader("Marés")
    if tides:
        st.metric("Maré Atual", f"{tides['mare_atual']['altura']} m", tides['mare_atual']['status'].capitalize())
        st.metric("Próxima Maré", f"{tides['proxima_mare']['tipo']} {tides['proxima_mare']['altura']} m às {tides['proxima_mare']['hora']}")
    else:
        st.warning("Dados de maré indisponíveis.")

# --- Risco ---
with col3:
    st.subheader("Risco de Alagamento")
    if weather and tides:
        risco, motivos = calcula_risco(clima['🌧️ Precipitação (mm)'], tides['mare_atual']['altura'])
        st.write(f"**Risco: {risco}**")
        if motivos:
            st.write(", ".join(motivos))
        else:
            st.write("Sem fatores críticos no momento.")
    else:
        st.warning("Dados insuficientes para avaliação de risco.")

# --- Gráfico de Maré ---
st.subheader("📈 Previsão de Maré")
if tides and tides["previsao"]:
    df = pd.DataFrame(tides["previsao"])
    fig, ax = plt.subplots()
    ax.plot(df["hora"], df["altura"], marker="o", color="#007acc")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Altura (m)")
    ax.set_title("Variação da Maré")
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("Dados de previsão de maré indisponíveis.")
