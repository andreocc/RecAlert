import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Tenta achar a tabela com as marés
        table = soup.find("table", class_="tide-chart-table")
        if not table:
            st.warning("Tabela de maré não encontrada na página. Pode estar carregada via JavaScript.")
            return None
        
        rows = table.find_all("tr")[1:]  # Pula o cabeçalho
        previsao = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            hora = cols[0].get_text(strip=True)
            altura_str = cols[1].get_text(strip=True).replace(",", ".")
            tipo = cols[2].get_text(strip=True)
            try:
                altura = float(altura_str)
            except:
                continue
            previsao.append({"hora": hora, "altura": altura, "tipo": tipo})
        
        if not previsao:
            st.warning("Nenhum dado válido encontrado na tabela.")
            return None
        
        now = datetime.now().strftime("%H:%M")
        mare_atual = None
        proxima_mare = None
        
        for i, p in enumerate(previsao):
            if p["hora"] >= now:
                mare_atual = p
                proxima_mare = previsao[i+1] if i+1 < len(previsao) else p
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

weather = get_weather_data()
tide = get_tide_data()

if weather:
    st.subheader("Previsão Climática (hoje)")
    df_weather = pd.DataFrame({
        "Hora": weather["hourly"]["time"],
        "Temperatura (°C)": weather["hourly"]["temperature_2m"],
        "Precipitação (mm)": weather["hourly"]["precipitation"],
        "Umidade (%)": weather["hourly"]["relative_humidity_2m"],
        "Vento (km/h)": weather["hourly"]["windspeed_10m"],
    })
    df_weather["Hora"] = pd.to_datetime(df_weather["Hora"]).dt.strftime("%H:%M")
    st.dataframe(df_weather.head(24))

if tide:
    st.subheader("Previsão de Maré - Hoje")
    st.write(f"Mare atual: {tide['mare_atual']['hora']} - {tide['mare_atual']['altura']}m ({tide['mare_atual']['tipo']})")
    st.write(f"Próxima mare: {tide['proxima_mare']['hora']} - {tide['proxima_mare']['altura']}m ({tide['proxima_mare']['tipo']})")

    df_tide = pd.DataFrame(tide["previsao"])
    st.line_chart(df_tide.set_index("hora")["altura"])

    # Risco combinando chuva e maré
    try:
        precip_now = weather["hourly"]["precipitation"][0]
        altura_now = tide['mare_atual']['altura']
        nivel_risco, motivos = calcula_risco(precip_now, altura_now)
        st.subheader(f"Nível de risco: {nivel_risco}")
        st.write(", ".join(motivos))
    except Exception:
        pass
else:
    st.warning("Dados de maré indisponíveis.")
