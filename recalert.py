import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from bs4 import BeautifulSoup

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
        st.error(f"Erro ao buscar dados de clima: {e}")
        return None

@st.cache_data(ttl=3600)
def get_tide_data():
    url = "https://pt.tideschart.com/Brazil/Pernambuco/Recife/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # A tabela das marés tem o atributo class "tide-table"
        table = soup.find("table", class_="tide-table")
        if not table:
            st.warning("Tabela de marés não encontrada no site.")
            return None

        rows = table.find_all("tr")[1:]  # Ignora cabeçalho

        previsao = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            hora = cols[0].text.strip()
            altura_str = cols[1].text.strip().replace(",", ".").replace("m", "")
            tipo = cols[2].text.strip()
            try:
                altura = float(altura_str)
                previsao.append({"hora": hora, "altura": altura, "tipo": tipo})
            except:
                continue

        if not previsao:
            st.warning("Sem dados válidos de maré.")
            return None

        now_str = datetime.now().strftime("%H:%M")
        mare_atual = None
        proxima_mare = None

        for i, p in enumerate(previsao):
            if p["hora"] >= now_str:
                mare_atual = p
                if i+1 < len(previsao):
                    proxima_mare = previsao[i+1]
                else:
                    proxima_mare = p
                break
        if not mare_atual:
            mare_atual = previsao[-1]
            proxima_mare = mare_atual

        return {
            "mare_atual": mare_atual,
            "proxima_mare": proxima_mare,
            "previsao": previsao
        }
    except Exception as e:
        st.error(f"Erro ao buscar dados de maré: {e}")
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

# Buscar dados
weather = get_weather_data()
tides = get_tide_data()

# Layout colunas
col1, col2, col3 = st.columns([2,1,1])

with col1:
    st.subheader("Condições Atuais")
    if weather:
        now = datetime.now()
        hourly = weather.get('hourly', {})
        times = hourly.get('time', [])
        idx = next((i for i,t in enumerate(times) if datetime.fromisoformat(t) >= now), 0)

        clima_atual = {
            "temperatura": hourly.get("temperature_2m", [None])[idx],
            "precipitacao": hourly.get("precipitation", [0])[idx],
            "umidade": hourly.get("relative_humidity_2m", [None])[idx],
            "vento": hourly.get("windspeed_10m", [None])[idx]
        }

        st.write(f"🌡️ Temperatura: {clima_atual['temperatura']} °C")
        st.write(f"🌧️ Precipitação: {clima_atual['precipitacao']} mm")
        st.write(f"💧 Umidade: {clima_atual['umidade']} %")
        st.write(f"💨 Vento: {clima_atual['vento']} km/h")
    else:
        st.write("Dados de clima indisponíveis")

with col2:
    st.subheader("Marés")
    if tides:
        st.write(f"🌊 Maré Atual: {tides['mare_atual']['altura']} m às {tides['mare_atual']['hora']} ({tides['mare_atual']['tipo']})")
        st.write(f"Próxima Maré: {tides['proxima_mare']['altura']} m às {tides['proxima_mare']['hora']} ({tides['proxima_mare']['tipo']})")
    else:
        st.write("Dados de maré indisponíveis")

with col3:
    st.subheader("Risco de Alagamento")
    if weather and tides:
        precip = float(clima_atual['precipitacao'])
        altura_mare = tides['mare_atual']['altura']
        risco, motivos = calcula_risco(precip, altura_mare)
        st.write(f"Risco: **{risco}**")
        if motivos:
            st.write("Motivos: " + ", ".join(motivos))
        else:
            st.write("Sem motivos significativos")
    else:
        st.write("Dados insuficientes para cálculo de risco")

st.subheader("Previsão de Maré")
if tides and tides.get('previsao'):
    df = pd.DataFrame(tides['previsao'])
    df['hora_dt'] = pd.to_datetime(df['hora'], format="%H:%M").dt.time

    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df['hora_dt'], df['altura'], marker='o', color='#0645AD')
    ax.set_xlabel("Hora")
    ax.set_ylabel("Altura (m)")
    ax.set_title("Previsão de Maré para Hoje")
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)
else:
    st.write("Dados de previsão de maré indisponíveis")
