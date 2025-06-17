#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor de Maré e Clima - Recife (Versão Streamlit)

Aplicação web para monitoramento em tempo real da previsão de chuvas e tábua de marés
na cidade de Recife, Pernambuco, com avaliação de risco de alagamento e envio de alertas.

Autor: Manus AI
Data: Junho/2025
"""

import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import requests
import json
import datetime
import time
from datetime import datetime, timedelta
import threading
import re
import os
import sys
import random
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="Monitor Maré e Clima - Recife",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        # 'Report a bug': "https://www.extremelycoolapp.com/bug",
        # 'About': "# Monitor de Maré e Clima - Recife\nDesenvolvido por Manus AI"
    }
)

# --- Classes de Gerenciamento de Dados (Adaptadas do Original) ---

# (As classes WeatherDataManager, TideDataManager, RiskAssessor, EmailManager
#  serão copiadas/adaptadas aqui. Por enquanto, placeholders)

class WeatherDataManager:
    """
    Classe para gerenciar a coleta e processamento de dados meteorológicos
    utilizando a WeatherAPI.com ou dados simulados
    """
    
    def __init__(self, api_key: str = None, use_simulated_data: bool = False):
        self.api_key = api_key or "SUA_CHAVE_API_AQUI"
        self.base_url = "http://api.weatherapi.com/v1"
        self.location = "Recife"
        self.weather_data = {}
        self.forecast_data = {}
        self.last_update = None
        self.use_simulated_data = use_simulated_data
    
    # ... (Métodos get_current_weather, get_forecast, _format_*, _get_simulated_*)
    # (Copiar métodos da versão Tkinter aqui, adaptando se necessário)
    # Exemplo simplificado:
    def get_current_weather(self):
        if self.use_simulated_data:
            return self._get_simulated_weather_data()
        # Implementação real da API...
        return self._get_simulated_weather_data() # Placeholder

    def get_forecast(self, days: int = 2):
        if self.use_simulated_data:
             return self._get_simulated_forecast_data()
        # Implementação real da API...
        return self._get_simulated_forecast_data() # Placeholder

    def _get_simulated_weather_data(self):
        # (Copiar implementação da versão Tkinter)
        now = datetime.now()
        return {
            'temperatura': round(28 + (random.random() * 2 - 1) * 4, 1),
            'sensacao_termica': round(29 + (random.random() * 2 - 1) * 4, 1),
            'precipitacao_mm': round(random.uniform(0, 5), 1),
            'pressao_hpa': random.randint(1008, 1018),
            'umidade': random.randint(70, 95),
            'vento_kph': round(random.uniform(5, 25), 1),
            'direcao_vento': random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            'condicao': random.choice(["Parcialmente nublado", "Ensolarado", "Nublado", "Chuva leve"]),
            'icone': "//cdn.weatherapi.com/weather/64x64/day/116.png",
            'ultima_atualizacao': now.strftime("%Y-%m-%d %H:%M"),
            'cidade': "Recife",
            'regiao': "Pernambuco",
            'pais': "Brasil",
            'hora_local': now.strftime("%Y-%m-%d %H:%M")
        }

    def _get_simulated_forecast_data(self):
        # (Copiar implementação da versão Tkinter)
        now = datetime.now()
        horas = []
        precip_24h = 0
        precip_prox_24h = 0
        for i in range(48):
            hora_dt = now - timedelta(hours=24) + timedelta(hours=i)
            precip = round(random.uniform(0, 2), 1) if random.random() < 0.3 else 0
            horas.append({
                'hora': hora_dt.strftime("%Y-%m-%d %H:%M"),
                'temperatura': round(28 + math.sin((hora_dt.hour - 6) * math.pi / 12) * 4 + random.uniform(-1, 1), 1),
                'precipitacao': precip,
                'chance_chuva': random.randint(0, 40),
                'pressao': random.randint(1008, 1018),
                'condicao': "Nublado" if precip > 0 else "Ensolarado",
                'icone': "//cdn.weatherapi.com/weather/64x64/day/119.png"
            })
            if hora_dt <= now and hora_dt >= now - timedelta(hours=24):
                 precip_24h += precip
            if hora_dt >= now and hora_dt <= now + timedelta(hours=24):
                 precip_prox_24h += precip
        return {
            'hoje': {}, # Simplificado
            'amanha': {}, # Simplificado
            'precipitacao_24h': round(precip_24h, 1),
            'precipitacao_proximas_24h': round(precip_prox_24h, 1),
            'horas': horas
        }

class TideDataManager:
    """
    Classe para gerenciar a coleta e processamento de dados de maré
    para o Porto do Recife, com suporte a dados simulados
    """
    def __init__(self, use_simulated_data: bool = False):
        self.use_simulated_data = use_simulated_data
    
    # ... (Métodos get_tide_data, _scrape_tide_data, _get_simulated_tide_data, _calculate_current_tide, _get_next_tide)
    # (Copiar métodos da versão Tkinter aqui, adaptando se necessário)
    # Exemplo simplificado:
    def get_tide_data(self):
        if self.use_simulated_data:
            return self._get_simulated_tide_data()
        # Implementação real (scraping ou API)
        return self._get_simulated_tide_data() # Placeholder

    def _get_simulated_tide_data(self):
        # (Copiar implementação da versão Tkinter)
        now = datetime.now()
        today = now.date()
        day_of_year = today.timetuple().tm_yday
        base_hour = (day_of_year % 12)
        tides = []
        high_tide = 2.0 + 0.3 * math.sin(day_of_year * 2 * math.pi / 29.5) + random.uniform(-0.2, 0.2)
        low_tide = 0.5 + 0.15 * math.sin(day_of_year * 2 * math.pi / 29.5) + random.uniform(-0.1, 0.1)
        tide_heights = [high_tide, low_tide, high_tide + random.uniform(-0.1, 0.1), low_tide + random.uniform(-0.1, 0.1)]
        tide_types = ["alta", "baixa", "alta", "baixa"]
        for i in range(4):
            hour = (base_hour + i * 6) % 24
            minute = random.randint(0, 59)
            tide_time = datetime(today.year, today.month, today.day, hour, minute)
            tides.append({
                'hora': tide_time.strftime("%Y-%m-%d %H:%M"),
                'altura': round(max(0.1, tide_heights[i]), 2),
                'tipo': tide_types[i]
            })
        tides.sort(key=lambda x: datetime.strptime(x['hora'], "%Y-%m-%d %H:%M"))
        current_tide = self._calculate_current_tide(tides) # Precisa da implementação completa
        return {
            'mares': tides,
            'mare_atual': current_tide if current_tide else {'altura': 1.0, 'status': 'desconhecido', 'hora': now.strftime("%Y-%m-%d %H:%M")},
            'mare_maxima': max(tides, key=lambda x: x['altura']) if tides else {},
            'mare_minima': min(tides, key=lambda x: x['altura']) if tides else {},
            'proxima_mare': self._get_next_tide(tides) if tides else {}
        }

    def _calculate_current_tide(self, tides):
         # (Copiar implementação da versão Tkinter)
         # Placeholder simplificado
         if not tides: return None
         now = datetime.now()
         heights = [t['altura'] for t in tides]
         avg_height = sum(heights) / len(heights) if heights else 1.0
         status = 'enchente' if random.random() > 0.5 else 'vazante'
         return {'hora': now.strftime("%Y-%m-%d %H:%M"), 'altura': round(avg_height + random.uniform(-0.5, 0.5), 2), 'status': status}

    def _get_next_tide(self, tides):
        # (Copiar implementação da versão Tkinter)
        # Placeholder simplificado
        if not tides: return None
        now = datetime.now()
        for tide in tides:
            tide_time = datetime.strptime(tide['hora'], "%Y-%m-%d %H:%M")
            if tide_time > now:
                return tide
        return tides[0] # Retorna a primeira do dia se nenhuma for encontrada

class RiskAssessor:
    """
    Classe para avaliar o nível de risco com base nos dados meteorológicos e de maré
    """
    RISK_LOW = "Baixo"
    RISK_MEDIUM = "Moderado"
    RISK_HIGH = "Alto"
    
    @staticmethod
    def assess_risk(weather_data, forecast_data, tide_data):
        # (Copiar implementação da versão Tkinter)
        risk_score = 0
        risk_factors = []
        precip_24h = forecast_data.get('precipitacao_24h', 0)
        precip_next_24h = forecast_data.get('precipitacao_proximas_24h', 0)
        current_tide_height = tide_data.get('mare_atual', {}).get('altura', 0)
        max_tide_height = tide_data.get('mare_maxima', {}).get('altura', 0)
        pressure = weather_data.get('pressao_hpa')

        if precip_24h >= 30: risk_score += 3; risk_factors.append(f"Prec. 24h: {precip_24h:.1f} mm")
        elif precip_24h >= 10: risk_score += 1
        if precip_next_24h >= 30: risk_score += 3; risk_factors.append(f"Prev. Chuva 24h: {precip_next_24h:.1f} mm")
        elif precip_next_24h >= 10: risk_score += 1
        if current_tide_height >= 2.0: risk_score += 2; risk_factors.append(f"Maré Atual: {current_tide_height:.2f} m")
        elif current_tide_height >= 1.5: risk_score += 1
        if max_tide_height >= 2.2: risk_score += 2; risk_factors.append(f"Maré Máx.: {max_tide_height:.2f} m")
        elif max_tide_height >= 1.8: risk_score += 1
        if pressure is not None and pressure < 1000: risk_score += 1; risk_factors.append(f"Pressão Baixa: {pressure} hPa")
        if precip_24h >= 20 and max_tide_height >= 2.0: risk_score += 2; risk_factors.append("Chuva Forte + Maré Alta")

        if risk_score >= 5: risk_level = RiskAssessor.RISK_HIGH
        elif risk_score >= 2: risk_level = RiskAssessor.RISK_MEDIUM
        else: risk_level = RiskAssessor.RISK_LOW
        description = "Fatores: " + ", ".join(risk_factors) if risk_factors else "Sem fatores significativos."
        return (risk_level, description)

class EmailManager:
    """
    Classe para gerenciar o envio de e-mails de alerta
    """
    def __init__(self):
        self.config = self._load_config_from_state()

    def _load_config_from_state(self):
        # Carrega de st.session_state em vez de arquivo
        return {
            "sender_email": st.session_state.get("sender_email", ""),
            "sender_password": st.session_state.get("sender_password", ""),
            "recipient_email": st.session_state.get("recipient_email", ""),
            "smtp_server": st.session_state.get("smtp_server", "smtp.gmail.com"),
            "smtp_port": st.session_state.get("smtp_port", 587)
        }

    def save_config_to_state(self, sender_email, sender_password, recipient_email, smtp_server="smtp.gmail.com", smtp_port=587):
        # Salva em st.session_state
        st.session_state.sender_email = sender_email
        st.session_state.sender_password = sender_password
        st.session_state.recipient_email = recipient_email
        st.session_state.smtp_server = smtp_server
        st.session_state.smtp_port = smtp_port
        self.config = self._load_config_from_state() # Atualiza config interna
        return True

    def send_alert(self, weather_data, forecast_data, tide_data, risk_level, risk_description):
        # (Copiar implementação da versão Tkinter, usando self.config)
        # Placeholder simplificado
        if not self.config["sender_email"] or not self.config["sender_password"] or not self.config["recipient_email"]:
            return (False, "Configurações de e-mail incompletas")
        st.success(f"(Simulado) E-mail de alerta {risk_level} enviado para {self.config['recipient_email']}")
        return (True, "E-mail de alerta enviado com sucesso (simulado)")

    def test_config(self):
        # (Copiar implementação da versão Tkinter, usando self.config)
        # Placeholder simplificado
        if not self.config["sender_email"] or not self.config["sender_password"] or not self.config["recipient_email"]:
            return (False, "Configurações de e-mail incompletas")
        st.success(f"(Simulado) Teste de e-mail enviado para {self.config['recipient_email']}")
        return (True, "Teste de e-mail enviado com sucesso (simulado)")

# --- Funções de Obtenção de Dados com Cache ---

# Usar cache para evitar recarregar dados a cada interação
@st.cache_data(ttl=1800) # Cache por 30 minutos
def fetch_weather_data(use_simulated_data=True):
    """Busca dados meteorológicos atuais e previsão"""
    manager = WeatherDataManager(use_simulated_data=use_simulated_data)
    current = manager.get_current_weather()
    forecast = manager.get_forecast()
    return current, forecast

@st.cache_data(ttl=1800) # Cache por 30 minutos
def fetch_tide_data(use_simulated_data=True):
    """Busca dados de maré"""
    manager = TideDataManager(use_simulated_data=use_simulated_data)
    return manager.get_tide_data()

# --- Inicialização do Estado da Sessão ---

# Usar st.session_state para manter dados entre reruns
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.use_simulated_data = True # Começar com dados simulados
    st.session_state.sender_email = ""
    st.session_state.sender_password = ""
    st.session_state.recipient_email = ""
    st.session_state.smtp_server = "smtp.gmail.com"
    st.session_state.smtp_port = 587
    # Carregar configurações salvas (se implementado)

# --- Interface Principal Streamlit ---

st.title("🌊 Monitor de Maré e Clima - Recife")

# --- Barra Lateral (Sidebar) para Configurações ---
with st.sidebar:
    st.header("Configurações")
    
    # Opção para usar dados simulados
    use_simulated = st.checkbox("Usar Dados Simulados", value=st.session_state.use_simulated_data)
    if use_simulated != st.session_state.use_simulated_data:
        st.session_state.use_simulated_data = use_simulated
        # Limpar cache ao mudar a fonte de dados
        fetch_weather_data.clear()
        fetch_tide_data.clear()
        st.rerun()
        
    st.info("Dados reais requerem configuração de API e podem falhar.")

    # Botão para forçar atualização
    if st.button("Forçar Atualização de Dados"):
        fetch_weather_data.clear()
        fetch_tide_data.clear()
        st.rerun()

    st.markdown("---")
    st.header("Configurações de E-mail")
    
    email_manager = EmailManager() # Instancia para usar métodos de salvar/testar
    
    with st.form("email_config_form"):
        sender_email = st.text_input(
            "E-mail remetente", 
            value=st.session_state.sender_email
        )
        sender_password = st.text_input(
            "Senha/App Password", 
            value=st.session_state.sender_password, 
            type="password"
        )
        recipient_email = st.text_input(
            "E-mail destinatário", 
            value=st.session_state.recipient_email
        )
        
        submitted = st.form_submit_button("Salvar Configurações")
        if submitted:
            success = email_manager.save_config_to_state(sender_email, sender_password, recipient_email)
            if success:
                st.success("Configurações salvas na sessão!")
            else:
                st.error("Erro ao salvar configurações.")
                
    if st.button("Testar Configuração de E-mail"):
        success, message = email_manager.test_config()
        if success:
            st.success(message)
        else:
            st.error(message)

# --- Carregamento dos Dados ---

# Exibe spinner enquanto carrega
with st.spinner("Carregando dados..."):
    try:
        weather_data, forecast_data = fetch_weather_data(st.session_state.use_simulated_data)
        tide_data = fetch_tide_data(st.session_state.use_simulated_data)
        
        # Calcula o risco
        risk_level, risk_description = RiskAssessor.assess_risk(
            weather_data, forecast_data, tide_data
        )
        
        data_loaded = True
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        # Define dados vazios para evitar erros na interface
        weather_data, forecast_data, tide_data = {}, {}, {}
        risk_level, risk_description = "Indisponível", "Erro ao carregar dados."
        data_loaded = False

# --- Exibição dos Dados (Layout Principal) ---

if data_loaded:
    # Layout em colunas para dados atuais
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌦️ Dados Meteorológicos Atuais")
        # (Implementar exibição dos dados weather_data)
        st.metric("Temperatura", f"{weather_data.get('temperatura', 'N/A')}°C", f"{weather_data.get('sensacao_termica', 'N/A')}°C Sensação")
        st.write(f"**Condição:** {weather_data.get('condicao', 'N/A')}")
        st.write(f"**Precipitação (agora):** {weather_data.get('precipitacao_mm', 0)} mm")
        st.write(f"**Pressão:** {weather_data.get('pressao_hpa', 'N/A')} hPa")
        st.write(f"**Umidade:** {weather_data.get('umidade', 'N/A')}%" )
        st.write(f"**Vento:** {weather_data.get('vento_kph', 'N/A')} km/h {weather_data.get('direcao_vento', '')}")
        st.caption(f"Atualizado em: {weather_data.get('ultima_atualizacao', 'N/A')}")

    with col2:
        st.subheader("🌊 Dados de Maré Atuais")
        # (Implementar exibição dos dados tide_data)
        current_tide = tide_data.get('mare_atual', {})
        status_text = "Enchente" if current_tide.get('status') == 'enchente' else "Vazante"
        st.metric("Altura Atual", f"{current_tide.get('altura', 'N/A')} m", status_text)
        
        next_tide = tide_data.get('proxima_mare', {})
        tide_type = "Alta" if next_tide.get('tipo') == 'alta' else "Baixa"
        st.write(f"**Próxima Maré:** {tide_type} de {next_tide.get('altura', 'N/A')} m às {next_tide.get('hora', 'N/A')}")
        
        st.write("**Marés do Dia:**")
        for tide in tide_data.get('mares', []):
             tide_type_day = "Alta" if tide.get('tipo') == 'alta' else "Baixa"
             st.write(f"- {tide.get('hora', '')}: {tide_type_day} de {tide.get('altura', 'N/A')} m")
        st.caption(f"Atualizado em: {current_tide.get('hora', 'N/A')}")

    st.markdown("---")

    # --- Avaliação de Risco ---
    st.subheader("🚨 Avaliação de Risco")
    
    if risk_level == RiskAssessor.RISK_HIGH:
        st.error(f"**Nível de Risco: {risk_level}**")
    elif risk_level == RiskAssessor.RISK_MEDIUM:
        st.warning(f"**Nível de Risco: {risk_level}**")
    else:
        st.success(f"**Nível de Risco: {risk_level}**")
        
    st.write(risk_description)
    
    # Botão de Alerta
    if risk_level == RiskAssessor.RISK_HIGH:
        if st.button("Enviar Alerta por E-mail", type="primary"):
            email_manager = EmailManager() # Recarrega config do state
            success, message = email_manager.send_alert(
                weather_data, forecast_data, tide_data, risk_level, risk_description
            )
            if success:
                st.success(message)
            else:
                st.error(message)

    st.markdown("---")

    # --- Gráficos ---
    st.subheader("📊 Gráficos")
    
    with st.spinner("Gerando gráficos..."):
        # (Implementar função para criar e exibir gráficos com matplotlib ou plotly)
        # Placeholder:
        st.write("Gráficos serão exibidos aqui.")
        # Exemplo com Matplotlib (requer implementação da função create_graphs)
        # fig = create_graphs(forecast_data, tide_data)
        # st.pyplot(fig)

else:
    st.warning("Não foi possível carregar os dados. Verifique as configurações ou tente novamente mais tarde.")

# --- Rodapé ---
st.markdown("---")
st.caption("Monitor de Maré e Clima - Recife | Desenvolvido por Manus AI")

