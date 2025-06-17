#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Funções de visualização para o Monitor de Maré e Clima - Recife (Versão Streamlit)

Este módulo contém funções para criar gráficos e visualizações para a aplicação Streamlit.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_css():
    """Carrega o arquivo CSS personalizado"""
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def create_matplotlib_graphs(forecast_data, tide_data):
    """
    Cria gráficos usando Matplotlib para exibição no Streamlit
    
    Args:
        forecast_data: Dados de previsão meteorológica
        tide_data: Dados de maré
        
    Returns:
        Figure: Figura do Matplotlib com os gráficos
    """
    # Configuração do tema escuro
    plt.style.use('dark_background')
    
    # Cria figura com dois subplots
    fig = Figure(figsize=(10, 8), facecolor='#1E1E1E')
    
    # Gráfico de maré
    ax1 = fig.add_subplot(211)
    
    # Dados de maré
    tide_times = []
    tide_heights = []
    
    # Adiciona marés do dia
    for tide in tide_data.get('mares', []):
        try:
            tide_time = datetime.strptime(tide.get('hora', ''), "%Y-%m-%d %H:%M")
            tide_times.append(tide_time)
            tide_heights.append(tide.get('altura', 0))
        except ValueError:
            continue
    
    # Se temos pelo menos dois pontos, plota o gráfico de maré
    if len(tide_times) >= 2:
        # Adiciona pontos intermediários para suavizar a curva
        smooth_times = []
        smooth_heights = []
        
        for i in range(len(tide_times) - 1):
            # Adiciona o ponto atual
            smooth_times.append(tide_times[i])
            smooth_heights.append(tide_heights[i])
            
            # Adiciona pontos intermediários
            start_time = tide_times[i]
            end_time = tide_times[i + 1]
            start_height = tide_heights[i]
            end_height = tide_heights[i + 1]
            
            # Calcula a diferença de tempo em horas
            time_diff = (end_time - start_time).total_seconds() / 3600
            
            # Adiciona pontos a cada 30 minutos
            for j in range(1, int(time_diff * 2)):
                interp_time = start_time + timedelta(minutes=30 * j)
                # Interpolação linear
                ratio = j / (time_diff * 2)
                interp_height = start_height + ratio * (end_height - start_height)
                
                smooth_times.append(interp_time)
                smooth_heights.append(interp_height)
        
        # Adiciona o último ponto
        if tide_times:
            smooth_times.append(tide_times[-1])
            smooth_heights.append(tide_heights[-1])
        
        # Plota a linha de maré
        ax1.plot(smooth_times, smooth_heights, color='#3498DB', linewidth=2)
        
        # Plota os pontos de maré conhecidos
        ax1.scatter(tide_times, tide_heights, color='#3498DB', s=50, zorder=5)
        
        # Adiciona linha horizontal para maré atual
        current_height = tide_data.get('mare_atual', {}).get('altura', 0)
        ax1.axhline(y=current_height, color='#F39C12', linestyle='--', alpha=0.7)
        
        # Adiciona texto para maré atual
        ax1.text(tide_times[0], current_height, f"Atual: {current_height} m",
                color='#F39C12', ha='left', va='bottom')
    
    # Configura o gráfico de maré
    ax1.set_title("Evolução da Maré", color='#FFFFFF')
    ax1.set_ylabel("Altura (m)", color='#FFFFFF')
    ax1.tick_params(axis='both', colors='#FFFFFF')
    ax1.grid(True, alpha=0.3)
    
    # Formata o eixo x para exibir apenas horas
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Cria subplot para precipitação
    ax2 = fig.add_subplot(212)
    
    # Dados de precipitação
    precip_times = []
    precip_values = []
    
    # Adiciona dados de precipitação das últimas 24h e próximas 24h
    now = datetime.now()
    start_time = now - timedelta(hours=24)
    end_time = now + timedelta(hours=24)
    
    for hour_data in forecast_data.get('horas', []):
        try:
            hour_time = datetime.strptime(hour_data.get('hora', ''), "%Y-%m-%d %H:%M")
            if start_time <= hour_time <= end_time:
                precip_times.append(hour_time)
                precip_values.append(hour_data.get('precipitacao', 0))
        except ValueError:
            continue
    
    # Plota barras de precipitação
    if precip_times:
        # Cores diferentes para passado e futuro
        colors = []
        for time_point in precip_times:
            if time_point <= now:
                colors.append('#2ECC71')  # Verde para passado
            else:
                colors.append('#1ABC9C')  # Verde-água para futuro
        
        ax2.bar(precip_times, precip_values, width=0.02, color=colors, alpha=0.7)
        
        # Adiciona linha vertical para o momento atual
        ax2.axvline(x=now, color='#F39C12', linestyle='--', alpha=0.7)
        ax2.text(now, max(precip_values) * 0.9 if precip_values else 1, "Agora",
                color='#F39C12', ha='center', va='top', rotation=90)
    
    # Configura o gráfico de precipitação
    ax2.set_title("Precipitação", color='#FFFFFF')
    ax2.set_ylabel("Precipitação (mm)", color='#FFFFFF')
    ax2.set_xlabel("Hora", color='#FFFFFF')
    ax2.tick_params(axis='both', colors='#FFFFFF')
    ax2.grid(True, alpha=0.3)
    
    # Formata o eixo x para exibir apenas horas
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Ajusta o layout
    fig.tight_layout()
    
    return fig

def create_plotly_graphs(forecast_data, tide_data):
    """
    Cria gráficos interativos usando Plotly para exibição no Streamlit
    
    Args:
        forecast_data: Dados de previsão meteorológica
        tide_data: Dados de maré
        
    Returns:
        go.Figure: Figura do Plotly com os gráficos
    """
    # Cria figura com dois subplots
    fig = make_subplots(
        rows=2, 
        cols=1,
        subplot_titles=("Evolução da Maré", "Precipitação"),
        vertical_spacing=0.15
    )
    
    # Configuração de tema escuro
    template = 'plotly_dark'
    
    # Dados de maré
    tide_times = []
    tide_heights = []
    tide_types = []
    
    # Adiciona marés do dia
    for tide in tide_data.get('mares', []):
        try:
            tide_time = datetime.strptime(tide.get('hora', ''), "%Y-%m-%d %H:%M")
            tide_times.append(tide_time)
            tide_heights.append(tide.get('altura', 0))
            tide_types.append(tide.get('tipo', ''))
        except ValueError:
            continue
    
    # Se temos pelo menos dois pontos, plota o gráfico de maré
    if len(tide_times) >= 2:
        # Adiciona pontos intermediários para suavizar a curva
        smooth_times = []
        smooth_heights = []
        
        for i in range(len(tide_times) - 1):
            # Adiciona o ponto atual
            smooth_times.append(tide_times[i])
            smooth_heights.append(tide_heights[i])
            
            # Adiciona pontos intermediários
            start_time = tide_times[i]
            end_time = tide_times[i + 1]
            start_height = tide_heights[i]
            end_height = tide_heights[i + 1]
            
            # Calcula a diferença de tempo em horas
            time_diff = (end_time - start_time).total_seconds() / 3600
            
            # Adiciona pontos a cada 30 minutos
            for j in range(1, int(time_diff * 2)):
                interp_time = start_time + timedelta(minutes=30 * j)
                # Interpolação linear
                ratio = j / (time_diff * 2)
                interp_height = start_height + ratio * (end_height - start_height)
                
                smooth_times.append(interp_time)
                smooth_heights.append(interp_height)
        
        # Adiciona o último ponto
        if tide_times:
            smooth_times.append(tide_times[-1])
            smooth_heights.append(tide_heights[-1])
        
        # Plota a linha de maré
        fig.add_trace(
            go.Scatter(
                x=smooth_times, 
                y=smooth_heights,
                mode='lines',
                name='Maré',
                line=dict(color='#3498DB', width=3)
            ),
            row=1, col=1
        )
        
        # Plota os pontos de maré conhecidos
        hover_texts = []
        for i, tide_type in enumerate(tide_types):
            type_text = "Alta" if tide_type == "alta" else "Baixa"
            hover_texts.append(f"Maré {type_text}: {tide_heights[i]} m")
            
        fig.add_trace(
            go.Scatter(
                x=tide_times, 
                y=tide_heights,
                mode='markers',
                name='Pontos de Maré',
                marker=dict(color='#3498DB', size=10),
                text=hover_texts,
                hoverinfo='text+x'
            ),
            row=1, col=1
        )
        
        # Adiciona linha horizontal para maré atual
        current_height = tide_data.get('mare_atual', {}).get('altura', 0)
        current_status = tide_data.get('mare_atual', {}).get('status', '')
        status_text = "Enchente" if current_status == "enchente" else "Vazante"
        
        fig.add_trace(
            go.Scatter(
                x=[tide_times[0], tide_times[-1]],
                y=[current_height, current_height],
                mode='lines',
                name=f'Atual: {current_height} m ({status_text})',
                line=dict(color='#F39C12', width=2, dash='dash')
            ),
            row=1, col=1
        )
    
    # Dados de precipitação
    precip_times = []
    precip_values = []
    precip_hover = []
    
    # Adiciona dados de precipitação das últimas 24h e próximas 24h
    now = datetime.now()
    start_time = now - timedelta(hours=24)
    end_time = now + timedelta(hours=24)
    
    for hour_data in forecast_data.get('horas', []):
        try:
            hour_time = datetime.strptime(hour_data.get('hora', ''), "%Y-%m-%d %H:%M")
            if start_time <= hour_time <= end_time:
                precip_times.append(hour_time)
                precip_value = hour_data.get('precipitacao', 0)
                precip_values.append(precip_value)
                
                # Texto para hover
                time_str = hour_time.strftime("%H:%M")
                precip_hover.append(f"Hora: {time_str}<br>Precipitação: {precip_value} mm")
        except ValueError:
            continue
    
    # Plota barras de precipitação
    if precip_times:
        # Cores diferentes para passado e futuro
        past_times = []
        past_values = []
        past_hover = []
        future_times = []
        future_values = []
        future_hover = []
        
        for i, time_point in enumerate(precip_times):
            if time_point <= now:
                past_times.append(time_point)
                past_values.append(precip_values[i])
                past_hover.append(precip_hover[i])
            else:
                future_times.append(time_point)
                future_values.append(precip_values[i])
                future_hover.append(precip_hover[i])
        
        # Precipitação passada
        if past_times:
            fig.add_trace(
                go.Bar(
                    x=past_times,
                    y=past_values,
                    name='Últimas 24h',
                    marker_color='#2ECC71',
                    text=past_hover,
                    hoverinfo='text'
                ),
                row=2, col=1
            )
        
        # Precipitação futura
        if future_times:
            fig.add_trace(
                go.Bar(
                    x=future_times,
                    y=future_values,
                    name='Próximas 24h',
                    marker_color='#1ABC9C',
                    text=future_hover,
                    hoverinfo='text'
                ),
                row=2, col=1
            )
        
        # Adiciona linha vertical para o momento atual
        fig.add_trace(
            go.Scatter(
                x=[now, now],
                y=[0, max(precip_values) * 1.1 if precip_values else 1],
                mode='lines',
                name='Agora',
                line=dict(color='#F39C12', width=2, dash='dash')
            ),
            row=2, col=1
        )
    
    # Configurações de layout
    fig.update_layout(
        template=template,
        height=700,
        plot_bgcolor='#2D2D2D',
        paper_bgcolor='#1E1E1E',
        font=dict(color='#FFFFFF'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # Configurações dos eixos
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255,255,255,0.2)',
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Altura (m)",
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255,255,255,0.2)',
        row=1, col=1
    )
    fig.update_xaxes(
        title_text="Hora",
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255,255,255,0.2)',
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="Precipitação (mm)",
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255,255,255,0.2)',
        row=2, col=1
    )
    
    return fig

def display_risk_indicator(risk_level, risk_description):
    """
    Exibe o indicador de risco com estilo apropriado
    
    Args:
        risk_level: Nível de risco (Baixo, Moderado, Alto)
        risk_description: Descrição do risco
    """
    if risk_level == "Alto":
        color = "#E74C3C"
        text_color = "white"
        icon = "🚨"
    elif risk_level == "Moderado":
        color = "#F39C12"
        text_color = "black"
        icon = "⚠️"
    else:
        color = "#2ECC71"
        text_color = "black"
        icon = "✅"
    
    # Cria um container estilizado para o nível de risco
    st.markdown(f"""
    <div style="background-color:{color}; padding:15px; border-radius:5px; margin-bottom:15px;">
        <h2 style="color:{text_color}; margin:0;">{icon} Nível de Risco: {risk_level}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibe a descrição do risco
    st.write(risk_description)

def create_weather_card(weather_data):
    """
    Cria um card estilizado para exibir dados meteorológicos
    
    Args:
        weather_data: Dados meteorológicos
    """
    st.markdown("""
    <div class="data-card">
        <h3>🌦️ Dados Meteorológicos</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.metric(
            "Temperatura", 
            f"{weather_data.get('temperatura', 'N/A')}°C", 
            f"{weather_data.get('sensacao_termica', 'N/A')}°C Sensação"
        )
    
    with col2:
        st.write(f"**Condição:** {weather_data.get('condicao', 'N/A')}")
        st.write(f"**Precipitação (agora):** {weather_data.get('precipitacao_mm', 0)} mm")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.write(f"**Pressão:**")
        st.write(f"{weather_data.get('pressao_hpa', 'N/A')} hPa")
    
    with col4:
        st.write(f"**Umidade:**")
        st.write(f"{weather_data.get('umidade', 'N/A')}%")
    
    with col5:
        st.write(f"**Vento:**")
        st.write(f"{weather_data.get('vento_kph', 'N/A')} km/h {weather_data.get('direcao_vento', '')}")
    
    st.caption(f"Atualizado em: {weather_data.get('ultima_atualizacao', 'N/A')}")

def create_tide_card(tide_data):
    """
    Cria um card estilizado para exibir dados de maré
    
    Args:
        tide_data: Dados de maré
    """
    st.markdown("""
    <div class="data-card">
        <h3>🌊 Dados de Maré</h3>
    </div>
    """, unsafe_allow_html=True)
    
    current_tide = tide_data.get('mare_atual', {})
    status_text = "Enchente" if current_tide.get('status') == 'enchente' else "Vazante"
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.metric(
            "Altura Atual", 
            f"{current_tide.get('altura', 'N/A')} m", 
            status_text
        )
    
    with col2:
        next_tide = tide_data.get('proxima_mare', {})
        tide_type = "Alta" if next_tide.get('tipo') == 'alta' else "Baixa"
        st.write(f"**Próxima Maré:** {tide_type} de {next_tide.get('altura', 'N/A')} m")
        st.write(f"**Horário:** {next_tide.get('hora', 'N/A')}")
    
    st.write("**Marés do Dia:**")
    
    # Cria uma tabela para as marés do dia
    tides = tide_data.get('mares', [])
    if tides:
        # Divide em duas colunas para melhor visualização
        col_left, col_right = st.columns(2)
        half = len(tides) // 2 + len(tides) % 2
        
        with col_left:
            for tide in tides[:half]:
                tide_type_day = "Alta" if tide.get('tipo') == 'alta' else "Baixa"
                st.write(f"- {tide.get('hora', '')}: {tide_type_day} de {tide.get('altura', 'N/A')} m")
        
        with col_right:
            for tide in tides[half:]:
                tide_type_day = "Alta" if tide.get('tipo') == 'alta' else "Baixa"
                st.write(f"- {tide.get('hora', '')}: {tide_type_day} de {tide.get('altura', 'N/A')} m")
    else:
        st.write("Dados de maré não disponíveis")
    
    st.caption(f"Atualizado em: {current_tide.get('hora', 'N/A')}")

def create_precipitation_summary(forecast_data):
    """
    Cria um resumo da precipitação
    
    Args:
        forecast_data: Dados de previsão
    """
    st.markdown("""
    <div class="data-card">
        <h3>🌧️ Resumo de Precipitação</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        precip_24h = forecast_data.get('precipitacao_24h', 0)
        st.metric(
            "Últimas 24h", 
            f"{precip_24h} mm",
            delta=None
        )
    
    with col2:
        precip_next_24h = forecast_data.get('precipitacao_proximas_24h', 0)
        delta = round(precip_next_24h - precip_24h, 1)
        delta_color = "inverse" if delta < 0 else "normal"
        
        st.metric(
            "Próximas 24h", 
            f"{precip_next_24h} mm",
            delta=f"{delta} mm" if delta != 0 else None,
            delta_color=delta_color
        )
