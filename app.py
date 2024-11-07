import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# Configurações da API
LOCALIZA_CONFIG = {
    'api_url': 'http://sistema.localizarastreamento.com/integracao/mestre/getVeiculos.php',
    'token': 'WREPZVgbr6sih8jLgqgPwMo8RgrjhC59zKGObxLLSXb1H3UDaPw5OfHEMFVWoWqi',
    'user': '50282072080',
    'password': 'HKJ@iu&0#23i*o9iu60T'
}


def clean_localiza_data(data):
    """Limpa e padroniza os dados da Localiza"""
    for veiculo in data:
        # Converte campos vazios para None
        for key in veiculo:
            if veiculo[key] == "":
                veiculo[key] = None

        # Converte campos numéricos
        numeric_fields = ['odometro', 'horimetro',
                          'velocidade', 'latitude', 'longitude']
        for field in numeric_fields:
            if veiculo[field]:
                try:
                    veiculo[field] = float(veiculo[field])
                except (ValueError, TypeError):
                    veiculo[field] = None

        # Padroniza status de ignição
        if veiculo['ignicao']:
            veiculo['ignicao'] = 'ON' if veiculo['ignicao'] == '1' else 'OFF'
    return data


def fetch_localiza_data():
    """Busca dados da API da Localiza"""
    try:
        headers = {
            'Accept': 'application/json',
            'token': LOCALIZA_CONFIG['token'],
            'user': LOCALIZA_CONFIG['user'],
            'pass': LOCALIZA_CONFIG['password']
        }
        response = requests.get(
            LOCALIZA_CONFIG['api_url'], headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return clean_localiza_data(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar dados da Localiza: {str(e)}")
        return None


def check_vehicle_status(df_localiza):
    """Verifica status dos veículos na Localiza"""
    if df_localiza is None or df_localiza.empty:
        return pd.DataFrame()

    status = []
    for _, veiculo in df_localiza.iterrows():
        status_item = {
            'placa': veiculo['placa'],
            'status': [],
            'ignicao': veiculo['ignicao'],
            'velocidade': veiculo['velocidade'],
            'odometro': veiculo['odometro'],
            'horimetro': veiculo['horimetro'],
            'latitude': veiculo['latitude'],
            'longitude': veiculo['longitude']
        }

        # Verifica dados ausentes
        if pd.isna(veiculo['ignicao']) or pd.isna(veiculo['velocidade']):
            status_item['status'].append('Sem Comunicação')

        # Verifica coordenadas
        if pd.isna(veiculo['latitude']) or pd.isna(veiculo['longitude']):
            status_item['status'].append('Sem Posição')

        # Verifica velocidade com ignição
        if veiculo['ignicao'] == 'OFF' and veiculo['velocidade'] > 0:
            status_item['status'].append('Inconsistência Velocidade/Ignição')

        # Se não houver problemas
        if not status_item['status']:
            status_item['status'] = ['Normal']

        status_item['status'] = ', '.join(status_item['status'])
        status.append(status_item)

    return pd.DataFrame(status)


def main():
    st.title("Sistema de Monitoramento de Rastreadores")

    # Sidebar para uploads
    with st.sidebar:
        st.header("Arquivos de Dados")
        crti_file = st.file_uploader("Planilha CRTI (Excel)", type=['xlsx'])
        status_file = st.file_uploader(
            "Planilha de Status (Excel)", type=['xlsx'])

        if st.button("Atualizar Dados da Localiza"):
            with st.spinner("Buscando dados..."):
                localiza_data = fetch_localiza_data()
                if localiza_data:
                    st.session_state['localiza_data'] = localiza_data
                    st.success("Dados atualizados com sucesso!")

    # Tabs principais
    tab1, tab2 = st.tabs(["Status Rastreadores", "Comparação"])

    # Tab 1: Status dos Rastreadores
    with tab1:
        st.header("Status dos Rastreadores")
        if 'localiza_data' in st.session_state:
            df_localiza = pd.DataFrame(st.session_state['localiza_data'])
            status_df = check_vehicle_status(df_localiza)

            # Filtra problemas
            problemas = status_df[status_df['status'] != 'Normal']

            # Métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Veículos", len(status_df))
            with col2:
                st.metric("Com Problemas", len(problemas))
            with col3:
                st.metric("Operando Normal", len(status_df) - len(problemas))

            if not problemas.empty:
                st.error("Veículos com Problemas:")
                st.dataframe(problemas, use_container_width=True)

                # Mapa dos veículos com problema
                problemas_mapa = problemas[problemas['latitude'].notna()]
                if not problemas_mapa.empty:
                    st.map(problemas_mapa[['latitude', 'longitude']])
            else:
                st.success("Todos os rastreadores operando normalmente")

    # Tab 2: Comparação
    with tab2:
        st.header("Comparação de Dados")
        if 'localiza_data' in st.session_state:
            df_localiza = pd.DataFrame(st.session_state['localiza_data'])

            # Exibe dados da Localiza
            st.subheader("Dados dos Rastreadores")
            st.dataframe(df_localiza, use_container_width=True)

            # Gráficos
            if not df_localiza.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.pie(df_localiza,
                                  names='ignicao',
                                  title="Status de Ignição")
                    st.plotly_chart(fig1)

                with col2:
                    fig2 = px.histogram(df_localiza,
                                        x='velocidade',
                                        title="Distribuição de Velocidades")
                    st.plotly_chart(fig2)


if __name__ == "__main__":
    main()
