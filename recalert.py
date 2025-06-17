import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="🌊 Previsão de Clima e Marés - Recife", layout="wide")
st.title("🌊 Previsão de Clima e Marés - Recife")

@st.cache_data(ttl=3600)
def get_weather_data():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=-8.05&longitude=-34.88"
        "&hourly=temperature_2m,precipitation,relative_humidity_2m,windspeed_10m"
        "&timezone=America%2FSao_Paulo"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Erro ao buscar clima: {e}")
        return None

@st.cache_data(ttl=3600)
def get_tide_data():
    url = "https://luisaraujo.github.io/API-Tabua-Mare/portos/recife.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        hoje = datetime.now().strftime("%Y-%m-%d")
        previsoes = [p for p in data if p["data"] == hoje]
        if not previsoes:
            st.warning("Sem dados de maré para hoje.")
            return None
        previsao = []
        now = datetime.now().strftime("%H:%M")
        mare_atual = None
        proxima_mare = None
        for p in previsoes[0]["mare"]:
            previsao.append({
                "hora": p["hora"],
                "altura": float(p["altura"].replace(",", "."))
            })
            if not mare_atual and p["hora"] >= now:
                mare_atual = p
        if mare_atual:
            proxima_idx = previsoes[0]["mare"].index(mare_atual) + 1
            if proxima_idx < len(previsoes[0]["mare"]):
                proxima_mare = previsoes[0]["mare"][proxima_idx]
            else:
                proxima_mare = mare_atual
        else:
            mare_atual = previsoes[0]["mare"][-1]
            proxima_mare = mare_atual

        return {
            "mare_atual": {
                "altura": float(mare_atual["altura"].replace(",", ".")),
                "hora": mare_atual["hora"],
                "tipo": mare_atual["tipo"]
            },
            "proxima_mare": {
                "altura": float(proxima_mare["altura"].replace(",", ".")),
                "hora": proxima_mare["hora"],
                "tipo": proxima_mare["tipo"]
            },
            "previsao": previsao
        }
    except Exception as e:
        st.error(f"Erro ao buscar maré: {e}")
        return None

def calcula_risco(precip, altura_mare):
    pts, reasons = 0, []
    if precip > 30: 
        pts += 3
        reasons.append("🌧️ Chuva alta")
    elif precip > 10: 
        pts += 1
        reasons.append("🌧️ Chuva moderada")
    if altura_mare > 2: 
        pts += 2
        reasons.append("🌊 Maré alta")
    elif altura_mare > 1.5: 
        pts += 1
        reasons.append("🌊 Maré moderada")
    if precip > 10 and altura_mare > 1.5: 
        pts += 2
        reasons.append("🌧️🌊 Combinado")
    if pts >= 5: 
        return "ALTO", reasons
    if pts >= 2: 
        return "MODERADO", reasons
    return "BAIXO", reasons

# Busca os dados
weather = get_weather_data()
tides = get_tide_data()

# Layout
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("Condições Atuais")
    if weather:
        now = datetime.now()
        hora_atual = now.strftime("%Y-%m-%dT%H:00")
        if hora_atual in weather["hourly"]["time"]:
            idx = weather["hourly"]["time"].index(hora_atual)
        else:
            idx = 0
        st.write(f"🌡️ Temperatura: {weather['hourly']['temperature_2m'][idx]}°C")
        st.write(f"🌧️ Precipitação: {weather['hourly']['precipitation'][idx]} mm")
        st.write(f"💧 Umidade: {weather['hourly']['relative_humidity_2m'][idx]}%")
        st.write(f"💨 Vento: {weather['hourly']['windspeed_10m'][idx]} km/h")
    else:
        st.warning("Dados de clima indisponíveis.")

with col2:
    st.subheader("Marés")
    if tides:
        st.write(f"🌊 Maré atual: {tides['mare_atual']['altura']}m ({tides['mare_atual']['tipo']}) às {tides['mare_atual']['hora']}")
        st.write(f"Próxima maré: {tides['proxima_mare']['altura']}m ({tides['proxima_mare']['tipo']}) às {tides['proxima_mare']['hora']}")
    else:
        st.warning("Dados de maré indisponíveis.")

with col3:
    st.subheader("Risco de Alagamento")
    if weather and tides:
        idx = 0
        hora_atual = datetime.now().strftime("%Y-%m-%dT%H:00")
        if hora_atual in weather["hourly"]["time"]:
            idx = weather["hourly"]["time"].index(hora_atual)
        precip = weather["hourly"]["precipitation"][idx]
        altura_mare = tides["mare_atual"]["altura"]
        risco, motivos = calcula_risco(precip, altura_mare)
        st.write(f"Risco: **{risco}**")
        if motivos:
            st.write("Motivos: " + ", ".join(motivos))
        else:
            st.write("Sem fatores de risco.")
    else:
        st.warning("Dados insuficientes para calcular o risco.")

st.subheader("Previsão de Maré")
if tides and tides["previsao"]:
    df = pd.DataFrame(tides["previsao"])
    fig, ax = plt.subplots()
    ax.plot(df["hora"], df["altura"], marker="o", color="#2196F3")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Altura (m)")
    ax.grid(True, linestyle="--", alpha=0.7)
    st.pyplot(fig)
else:
    st.warning("Sem previsão de maré disponível.")
