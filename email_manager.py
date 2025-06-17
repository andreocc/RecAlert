#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de gerenciamento de e-mail para o Monitor de Maré e Clima - Recife (Versão Streamlit)

Este módulo contém funções para configuração, teste e envio de e-mails de alerta.
"""

import streamlit as st
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailConfig:
    """Classe para gerenciar configurações de e-mail no Streamlit"""
    
    def __init__(self):
        """Inicializa a configuração de e-mail"""
        self.config_file = "email_config.json"
        self._initialize_session_state()
        
    def _initialize_session_state(self):
        """Inicializa o estado da sessão para configurações de e-mail"""
        if 'email_config_initialized' not in st.session_state:
            # Tenta carregar do arquivo primeiro
            config = self._load_from_file()
            
            # Inicializa o estado da sessão
            st.session_state.sender_email = config.get("sender_email", "")
            st.session_state.sender_password = config.get("sender_password", "")
            st.session_state.recipient_email = config.get("recipient_email", "")
            st.session_state.smtp_server = config.get("smtp_server", "smtp.gmail.com")
            st.session_state.smtp_port = config.get("smtp_port", 587)
            st.session_state.email_config_initialized = True
    
    def _load_from_file(self):
        """Carrega configurações de e-mail do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar configurações de e-mail: {e}")
        return {}
    
    def save_to_file(self):
        """Salva configurações de e-mail em arquivo"""
        try:
            config = {
                "sender_email": st.session_state.sender_email,
                "sender_password": st.session_state.sender_password,
                "recipient_email": st.session_state.recipient_email,
                "smtp_server": st.session_state.smtp_server,
                "smtp_port": st.session_state.smtp_port
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar configurações de e-mail: {e}")
            return False
    
    def get_config(self):
        """Obtém configurações atuais de e-mail"""
        return {
            "sender_email": st.session_state.sender_email,
            "sender_password": st.session_state.sender_password,
            "recipient_email": st.session_state.recipient_email,
            "smtp_server": st.session_state.smtp_server,
            "smtp_port": st.session_state.smtp_port
        }
    
    def update_config(self, sender_email, sender_password, recipient_email, 
                     smtp_server="smtp.gmail.com", smtp_port=587):
        """Atualiza configurações de e-mail"""
        st.session_state.sender_email = sender_email
        st.session_state.sender_password = sender_password
        st.session_state.recipient_email = recipient_email
        st.session_state.smtp_server = smtp_server
        st.session_state.smtp_port = smtp_port
        return self.save_to_file()

def render_email_config_form():
    """Renderiza o formulário de configuração de e-mail"""
    email_config = EmailConfig()
    
    with st.expander("⚙️ Configurações de E-mail", expanded=False):
        with st.form("email_config_form"):
            st.write("Configure o envio de alertas por e-mail:")
            
            sender_email = st.text_input(
                "E-mail remetente", 
                value=st.session_state.sender_email,
                help="Endereço de e-mail que enviará os alertas"
            )
            
            sender_password = st.text_input(
                "Senha/App Password", 
                value=st.session_state.sender_password, 
                type="password",
                help="Para Gmail, use uma App Password (https://support.google.com/accounts/answer/185833)"
            )
            
            recipient_email = st.text_input(
                "E-mail destinatário", 
                value=st.session_state.recipient_email,
                help="Endereço de e-mail que receberá os alertas"
            )
            
            advanced = st.checkbox("Configurações avançadas")
            
            if advanced:
                smtp_server = st.text_input(
                    "Servidor SMTP", 
                    value=st.session_state.smtp_server
                )
                
                smtp_port = st.number_input(
                    "Porta SMTP", 
                    value=st.session_state.smtp_port,
                    min_value=1,
                    max_value=65535
                )
            else:
                smtp_server = st.session_state.smtp_server
                smtp_port = st.session_state.smtp_port
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_button = st.form_submit_button("Salvar Configurações")
            
            with col2:
                test_button = st.form_submit_button("Testar Configuração")
        
        # Processamento do formulário
        if save_button:
            success = email_config.update_config(
                sender_email, sender_password, recipient_email, smtp_server, smtp_port
            )
            if success:
                st.success("✅ Configurações salvas com sucesso!")
            else:
                st.error("❌ Erro ao salvar configurações.")
        
        if test_button:
            if not sender_email or not sender_password or not recipient_email:
                st.error("❌ Preencha todos os campos obrigatórios.")
            else:
                with st.spinner("Testando configuração de e-mail..."):
                    success, message = test_email_config(
                        sender_email, sender_password, recipient_email, smtp_server, smtp_port
                    )
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")

def test_email_config(sender_email, sender_password, recipient_email, 
                     smtp_server="smtp.gmail.com", smtp_port=587):
    """
    Testa as configurações de e-mail
    
    Args:
        sender_email: E-mail do remetente
        sender_password: Senha ou app password do remetente
        recipient_email: E-mail do destinatário
        smtp_server: Servidor SMTP
        smtp_port: Porta SMTP
        
    Returns:
        Tuple: (sucesso, mensagem)
    """
    try:
        # Cria a mensagem de teste
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Teste de Configuração - Monitor de Maré e Clima Recife"
        
        body = """
        <html>
        <body>
            <h2>Teste de Configuração</h2>
            <p>Este é um e-mail de teste para verificar as configurações do Monitor de Maré e Clima - Recife.</p>
            <p>Se você recebeu este e-mail, as configurações estão corretas.</p>
            <p>Enviado em: {}</p>
        </body>
        </html>
        """.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        msg.attach(MIMEText(body, 'html'))
        
        # Conecta ao servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Envia o e-mail
        server.send_message(msg)
        server.quit()
        
        return (True, "Teste de e-mail enviado com sucesso")
    except Exception as e:
        return (False, f"Erro ao testar configurações de e-mail: {e}")

def send_alert_email(weather_data, forecast_data, tide_data, risk_level, risk_description):
    """
    Envia e-mail de alerta
    
    Args:
        weather_data: Dados meteorológicos atuais
        forecast_data: Dados de previsão
        tide_data: Dados de maré
        risk_level: Nível de risco
        risk_description: Descrição do risco
        
    Returns:
        Tuple: (sucesso, mensagem)
    """
    # Obtém configurações de e-mail
    email_config = EmailConfig().get_config()
    
    # Verifica se as configurações estão completas
    if not email_config["sender_email"] or not email_config["sender_password"] or not email_config["recipient_email"]:
        return (False, "Configurações de e-mail incompletas")
    
    try:
        # Cria a mensagem
        msg = MIMEMultipart()
        msg['From'] = email_config["sender_email"]
        msg['To'] = email_config["recipient_email"]
        msg['Subject'] = f"ALERTA: Risco {risk_level} de Alagamento em Recife"
        
        # Corpo do e-mail
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #E74C3C; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 15px; }}
                .section {{ margin-bottom: 20px; }}
                .risk-high {{ color: #E74C3C; font-weight: bold; }}
                .risk-medium {{ color: #F39C12; font-weight: bold; }}
                .risk-low {{ color: #2ECC71; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Alerta de Risco de Alagamento - Recife</h2>
                <p>Gerado em {now}</p>
            </div>
            <div class="content">
                <div class="section">
                    <h3>Nível de Risco: <span class="risk-high">{risk_level}</span></h3>
                    <p>{risk_description}</p>
                </div>
                
                <div class="section">
                    <h3>Condições Meteorológicas Atuais</h3>
                    <table>
                        <tr><th>Temperatura</th><td>{weather_data.get('temperatura')}°C</td></tr>
                        <tr><th>Condição</th><td>{weather_data.get('condicao')}</td></tr>
                        <tr><th>Precipitação</th><td>{weather_data.get('precipitacao_mm')} mm</td></tr>
                        <tr><th>Pressão</th><td>{weather_data.get('pressao_hpa')} hPa</td></tr>
                        <tr><th>Umidade</th><td>{weather_data.get('umidade')}%</td></tr>
                    </table>
                </div>
                
                <div class="section">
                    <h3>Previsão de Chuva</h3>
                    <table>
                        <tr><th>Últimas 24h</th><td>{forecast_data.get('precipitacao_24h')} mm</td></tr>
                        <tr><th>Próximas 24h</th><td>{forecast_data.get('precipitacao_proximas_24h')} mm</td></tr>
                    </table>
                </div>
                
                <div class="section">
                    <h3>Condições de Maré</h3>
                    <table>
                        <tr><th>Maré Atual</th><td>{tide_data.get('mare_atual', {}).get('altura')} m ({tide_data.get('mare_atual', {}).get('status')})</td></tr>
                        <tr><th>Próxima Maré</th><td>{tide_data.get('proxima_mare', {}).get('tipo')} de {tide_data.get('proxima_mare', {}).get('altura')} m às {tide_data.get('proxima_mare', {}).get('hora')}</td></tr>
                        <tr><th>Maré Máxima do Dia</th><td>{tide_data.get('mare_maxima', {}).get('altura')} m às {tide_data.get('mare_maxima', {}).get('hora')}</td></tr>
                    </table>
                </div>
                
                <div class="section">
                    <p>Este é um alerta automático gerado pelo Monitor de Maré e Clima - Recife.</p>
                    <p>Por favor, tome as precauções necessárias e acompanhe os canais oficiais de informação.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Conecta ao servidor SMTP
        server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
        server.starttls()
        server.login(email_config["sender_email"], email_config["sender_password"])
        
        # Envia o e-mail
        server.send_message(msg)
        server.quit()
        
        return (True, "E-mail de alerta enviado com sucesso")
    except Exception as e:
        return (False, f"Erro ao enviar e-mail: {e}")

def render_alert_button(weather_data, forecast_data, tide_data, risk_level, risk_description):
    """
    Renderiza o botão de alerta por e-mail quando o risco é alto
    
    Args:
        weather_data: Dados meteorológicos atuais
        forecast_data: Dados de previsão
        tide_data: Dados de maré
        risk_level: Nível de risco
        risk_description: Descrição do risco
    """
    if risk_level == "Alto":
        st.markdown("""
        <div style="background-color: rgba(231, 76, 60, 0.1); padding: 15px; border-radius: 5px; border-left: 5px solid #E74C3C; margin-top: 20px;">
            <h3 style="color: #E74C3C; margin-top: 0;">⚠️ Alerta de Risco Alto</h3>
            <p>O nível de risco atual é <strong>ALTO</strong>. Considere enviar um alerta por e-mail.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📧 Enviar Alerta por E-mail", type="primary"):
            with st.spinner("Enviando alerta por e-mail..."):
                success, message = send_alert_email(
                    weather_data, forecast_data, tide_data, risk_level, risk_description
                )
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
                    
                    # Se o erro for de configuração, sugere configurar o e-mail
                    if "configurações" in message.lower():
                        st.info("ℹ️ Configure seu e-mail nas configurações para enviar alertas.")
    else:
        st.info(f"ℹ️ O nível de risco atual ({risk_level}) não justifica um alerta por e-mail.")
