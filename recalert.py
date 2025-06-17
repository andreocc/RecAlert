import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

st.set_page_config(page_title="🌊 Previsão de Clima e Marés - Recife", layout="wide")
st.title("🌊 Previsão de Clima e Marés - Recife")

def get_tide_data_selenium():
    url = "https://pt.tideschart.com/Brazil/Pernambuco/Recife/"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 15)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tide-chart-table")))
    except TimeoutException:
        st.error("Timeout: tabela de marés não carregou na página.")
        driver.quit()
        return None
    except NoSuchElementException:
        st.error("Erro: tabela de marés não encontrada na página.")
        driver.quit()
        return None

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

    driver.quit()

    if not previsao:
        st.warning("Tabela de marés está vazia.")
        return None

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

# Chamando no Streamlit

tide_data = get_tide_data_selenium()

if tide_data:
    st.subheader("Marés")
    st.write(f"Maré Atual: {tide_data['mare_atual']['altura']}m ({tide_data['mare_atual']['tipo']}) às {tide_data['mare_atual']['hora']}")
    st.write(f"Próxima Maré: {tide_data['proxima_mare']['altura']}m ({tide_data['proxima_mare']['tipo']}) às {tide_data['proxima_mare']['hora']}")

    df = pd.DataFrame(tide_data['previsao'])
    df['hora_dt'] = pd.to_datetime(df['hora'], format='%H:%M')
    fig, ax = plt.subplots()
    ax.plot(df['hora_dt'], df['altura'], marker='o', linestyle='-', color='blue')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Altura (m)')
    ax.set_title('Previsão de Maré')
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)
else:
    st.warning("Não foi possível obter dados de maré.")
