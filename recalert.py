import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="🌊 Previsão de Clima e Marés - Recife", layout="wide")
st.title("🌊 Previsão de Clima e Marés - Recife")

# Função para obter dados de maré via API
def get_tide_data():
    # Define o fuso horário do Recife
    tz = pytz.timezone('America/Recife')
    hoje = datetime.now(tz).strftime("%Y%m%d")
    
    # URL da API com os dados das marés
    url = f"https://pt.tideschart.com/tides/brazil/pernambuco/recife/?period={hoje}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica erros na requisição
        dados = response.json()
        
        # Extrai os dados de maré do dia atual
        data_str = datetime.now(tz).strftime("%Y-%m-%d")
        mare_dia = dados['tides'][data_str]
        
        previsao = []
        for evento in mare_dia:
            hora = evento['time']
            # Remove a unidade 'm' e converte para float
            altura = float(evento['height'].replace('m', ''))
            tipo = evento['type']
            
            previsao.append({
                "hora": hora,
                "altura": altura,
                "tipo": tipo
            })
        
        # Encontra a maré atual e próxima
        agora = datetime.now(tz).strftime("%H:%M")
        mare_atual = None
        proxima_mare = None
        
        for i, evento in enumerate(previsao):
            if evento["hora"] >= agora:
                mare_atual = evento
                if i + 1 < len(previsao):
                    proxima_mare = previsao[i + 1]
                else:
                    # Se não houver próxima maré hoje, busca no próximo dia
                    amanha = (datetime.now(tz) + timedelta(days=1)).strftime("%Y%m%d")
                    url_amanha = f"https://pt.tideschart.com/tides/brazil/pernambuco/recife/?period={amanha}"
                    response_amanha = requests.get(url_amanha)
                    dados_amanha = response_amanha.json()
                    data_amanha_str = (datetime.now(tz) + timedelta(days=1)).strftime("%Y-%m-%d")
                    primeira_mare_amanha = dados_amanha['tides'][data_amanha_str][0]
                    proxima_mare = {
                        "hora": primeira_mare_amanha['time'],
                        "altura": float(primeira_mare_amanha['height'].replace('m', '')),
                        "tipo": primeira_mare_amanha['type']
                    }
                break
        
        return {
            "mare_atual": mare_atual or previsao[-1],
            "proxima_mare": proxima_mare or previsao[0],
            "previsao": previsao
        }
        
    except Exception as e:
        st.error(f"Erro ao obter dados de maré: {str(e)}")
        return None

# Exibição dos dados
tide_data = get_tide_data()

if tide_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌊 Maré Atual")
        if tide_data["mare_atual"]:
            st.metric("Hora", tide_data["mare_atual"]["hora"])
            st.metric("Altura", f"{tide_data['mare_atual']['altura']} m")
            st.metric("Tipo", "Preamar" if tide_data["mare_atual"]["tipo"] == "High" else "Baixa-mar")
        
    with col2:
        st.subheader("⏭️ Próxima Maré")
        if tide_data["proxima_mare"]:
            st.metric("Hora", tide_data["proxima_mare"]["hora"])
            st.metric("Altura", f"{tide_data['proxima_mare']['altura']} m")
            st.metric("Tipo", "Preamar" if tide_data["proxima_mare"]["tipo"] == "High" else "Baixa-mar")
    
    # Gráfico das marés
    st.subheader("📈 Previsão de Marés para Hoje")
    df = pd.DataFrame(tide_data["previsao"])
    df['hora'] = pd.to_datetime(df['hora'], format='%H:%M').dt.time
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['hora'].astype(str), df['altura'], marker='o')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Altura (m)')
    ax.set_title('Variação das Marés')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Tabela detalhada
    st.subheader("📋 Detalhes das Marés")
    df_display = df.copy()
    df_display['Tipo'] = df_display['tipo'].apply(lambda x: "Preamar" if x == "High" else "Baixa-mar")
    st.dataframe(df_display[['hora', 'altura', 'Tipo']].rename(columns={
        'hora': 'Hora',
        'altura': 'Altura (m)',
        'Tipo': 'Tipo de Maré'
    }))
else:
    st.warning("Não foi possível carregar os dados de maré. Tente novamente mais tarde.")
