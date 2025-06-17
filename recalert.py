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
        st.error(f"Erro ao buscar clima: {e}")
        return None

@st.cache_data(ttl=3600)
def get_tide_data():
    url = "https://pt.tideschart.com/Brazil/Pernambuco/Recife/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Extrair dados da tabela de maré
        table = soup.find("table", {"class": "tide-chart-table"})
        if not table:
            st.warning("Tabela de maré não encontrada na página.")
            return None

        previsao = []
        for row in table.tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            hora = cols[0].text.strip()
            altura_str = cols[1].text.strip().replace(",", ".")
            tipo = cols[2].text.strip()
            try:
                altura = float(altura_str)
            except ValueError:
                continue
            previsao.append({
                "hora": hora,
                "altura": altura,
                "tipo": tipo
            })

        # Definir mare atual e próxima com base na hora atual
        now = datetime.now().strftime("%H:%M")
        mare_atual = None
        proxima_mare = None
        for i, p in enumerate(previsao):
            if p["hora"] >= now:
                mare_atual = p
                proxima_mare = previsao[i + 1] if i + 1 < len(previsao) else p
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
    if precip > 30: pts += 3; reasons.append("🌧️ Chuva alta")
    elif precip > 10: pts += 1; reasons.append("🌧️ Chuva moderada")
    if altura_mare > 2: pts += 2; reasons.append("🌊 Maré alta")
    elif altura_mare > 1.5: pts += 1; reasons.append("🌊 Maré moderada")
    if precip > 10 and altura_mare > 1.5: pts += 2; reasons.append("🌧️🌊 Combinado")
    if pts >= 5: return "ALTO", reasons
    if pts >= 2: return "MODERADO", reasons
    return "BAIXO", reasons

# Busca os dados
weather = get_weather_data()
tides = get_tide_data()

col1, col2, col3 = st.columns([2, 1, 1])

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

with col2:
    st.subheader("Marés")
    if tides:
        st.write(f"🌊 Maré Atual: {tides['mare_atual']['altura']}m ({tides['mare_atual']['tipo']}) às {tides['mare_atual']['hora']}")
        st.write(f"Próxima Maré: {tides['proxima_mare']['altura']}m ({tides['proxima_mare']['tipo']}) às {tides['proxima_mare']['hora']}")
    else:
        st.write("Dados de maré indisponíveis")

with col3:
    st.subheader("Risco de Alagamento")
    if weather and tides:
        precipitacao = float(clima_atual['precipitacao'])
        altura_mare = tides['mare_atual']['altura']
        risco, motivos = calcula_risco(precipitacao, altura_mare)
        st.write(f"Risco: **{risco}**")
        if motivos:
            st.write("Motivos:", ", ".join(motivos))
        else:
            st.write("Sem motivos significativos")
    else:
        st.write("Dados insuficientes para calcular o risco")

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
