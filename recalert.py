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
    api = "https://luisaraujo.github.io/API-Tabua-Mare/idfixed"
    params = {"code":12}  # 12 = Porto do Recife
    try:
        resp = requests.get(api, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # espera array com objetos {"hora": "HH:MM", "altura": float}
        previsao = data
        # definir maré atual e próxima com base no tempo:
        now = datetime.now().strftime("%H:%M")
        atual = previsao[0]
        proxima = previsao[1] if len(previsao)>1 else atual
        return {
            "mare_atual": {"altura":float(atual["altura"]), "hora": atual["hora"]},
            "previsao": [{"hora":p["hora"], "altura": float(p["altura"])} for p in previsao],
            "proxima_mare": {"hora": proxima["hora"], "altura": float(proxima["altura"])}
        }
    except Exception as e:
        st.error(f"Erro ao buscar dados de maré: {e}")
        return None

def calcula_risco(precip, altura_mare):
    pts, reasons = 0, []
    if precip>30: pts+=3; reasons.append("🌧️ Chuva alta")
    elif precip>10: pts+=1; reasons.append("🌧️ Chuva moderada")
    if altura_mare>2: pts+=2; reasons.append("🌊 Maré alta")
    elif altura_mare>1.5: pts+=1; reasons.append("🌊 Maré moderada")
    if precip>10 and altura_mare>1.5: pts+=2; reasons.append("🌧️🌊 Combinado")
    if pts>=5: return "ALTO", reasons
    if pts>=2: return "MODERADO", reasons
    return "BAIXO", reasons

weather = get_weather_data()
tides = get_tide_data()

col1, col2, col3 = st.columns([2,1,1])

with col1:
    st.subheader("Clima Atual")
    if weather:
        now = datetime.now()
        idx = next((i for i,t in enumerate(weather["hourly"]["time"]) if datetime.fromisoformat(t)>=now),0)
        temp = weather["hourly"]["temperature_2m"][idx]
        prec = weather["hourly"]["precipitation"][idx]
        umid = weather["hourly"]["relative_humidity_2m"][idx]
        vento = weather["hourly"]["windspeed_10m"][idx]
        st.metric("🌡️ Temperatura", f"{temp} °C")
        st.metric("🌧️ Precipitação", f"{prec} mm")
        st.metric("💧 Umidade", f"{umid} %")
        st.metric("💨 Vento", f"{vento} km/h")
    else:
        st.warning("Clima indisponível.")

with col2:
    st.subheader("Marés – Porto do Recife")
    if tides:
        st.metric("Maré Atual", f"{tides['mare_atual']['altura']} m", tides['mare_atual']['hora'])
        st.metric("Próxima Maré", f"{tides['proxima_mare']['altura']} m", tides['proxima_mare']['hora'])
    else:
        st.warning("Maré indisponível.")

with col3:
    st.subheader("Risco de Alagamento")
    if weather and tides:
        risco, motivos = calcula_risco(prec, tides["mare_atual"]["altura"])
        st.write(f"**Risco: {risco}**")
        if motivos: st.write(" • ".join(motivos))
        else: st.write("Sem fatores críticos")
    else:
        st.warning("Dados insuficientes.")

st.subheader("📈 Previsão de Maré")
if tides and tides["previsao"]:
    df = pd.DataFrame(tides["previsao"])
    fig, ax = plt.subplots()
    ax.plot(df["hora"], df["altura"], marker="o", color="#007acc")
    ax.set_xlabel("Hora"); ax.set_ylabel("Altura (m)")
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("Sem previsão de maré.")
