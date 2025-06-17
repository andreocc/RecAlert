import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

st.set_page_config(page_title="🌊 Previsão de Clima e Marés - Recife", layout="wide")
st.title("🌊 Previsão de Clima e Marés - Recife")

def get_tide_data_selenium():
    url = "https://pt.tideschart.com/Brazil/Pernambuco/Recife/"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # Dá tempo para o JS carregar a tabela

    try:
        table = driver.find_element(By.CLASS_NAME, "tide-chart-table")
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # pula o cabeçalho

        previsao = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
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
    finally:
        driver.quit()

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

# Aqui você integra essa função ao seu app Streamlit igual antes, substituindo a chamada do get_tide_data

