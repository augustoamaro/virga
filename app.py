import streamlit as st
import pandas as pd
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="Controle de Equipamentos",
    page_icon="🚛",
    layout="wide"
)

st.title("📊 Sistema de Controle de Equipamentos")

# Upload do arquivo
st.subheader("Upload da Planilha")
arquivo_excel = st.file_uploader(
    "Selecione a planilha de equipamentos (Excel)",
    type=['xlsx', 'xls'],
    help="Faça upload de um arquivo Excel contendo os dados dos equipamentos"
)


def validar_config_api():
    """Valida as configurações da API nos secrets do Streamlit."""
    required_configs = ['token', 'user', 'pass']
    try:
        api_secrets = st.secrets['api_localiza']
    except KeyError:
        st.error("As configurações da API não foram encontradas nos secrets.")
        return False

    missing_configs = [
        config for config in required_configs if config not in api_secrets]
    if missing_configs:
        st.error(
            f"As seguintes configurações estão faltando nos secrets da API: {', '.join(missing_configs)}")
        return False
    return True


@st.cache_data(ttl=300)  # Cache por 5 minutos
def buscar_dados_api():
    """Busca dados da API da Localiza."""
    base_url = 'http://sistema.localizarastreamento.com/integracao/mestre/getVeiculos.php'

    headers = {
        'Accept': 'application/json',
        'token': st.secrets['api_localiza']['token'],
        'user': st.secrets['api_localiza']['user'],
        'pass': st.secrets['api_localiza']['pass']
    }

    try:
        response = requests.get(
            base_url,
            headers=headers,
            # Atenção: verify=False desabilita a verificação SSL. Use com cuidado.
            verify=False,
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição da API: {e}")
        return None

    try:
        dados = response.json()
        if isinstance(dados, list) and dados:
            return dados
        else:
            st.warning("A resposta da API não contém dados válidos.")
            return None
    except json.JSONDecodeError as e:
        st.error(f"Erro ao decodificar a resposta JSON: {e}")
        return None


def extrair_placa_do_apelido(apelido):
    """
    Extrai a placa de um Apelido.

    O Apelido pode ser no formato 'BT0002 | RDT-0A85' ou apenas 'RDT-0A85'.
    Retorna a placa sem hífens e caracteres especiais.
    """
    apelido = str(apelido).strip()
    if '|' in apelido:
        # Se tem pipe, pega o valor depois do pipe
        placa = apelido.split('|')[1].strip().upper()
    else:
        placa = apelido.strip().upper()
    # Remover hífens e caracteres especiais
    placa = ''.join(c for c in placa if c.isalnum())
    return placa


def atualizar_dados_localizacao(df):
    """Atualiza os dados de localização dos equipamentos usando os dados da API."""
    dados_api = buscar_dados_api()
    if dados_api is None:
        st.warning("Nenhum dado foi retornado da API.")
        return df

    if 'Apelido' not in df.columns:
        st.error("A coluna 'Apelido' não está presente na planilha.")
        return df

    # Criar um dicionário para fácil acesso aos dados da API
    dados_por_placa = {
        item['placa'].strip().upper().replace('-', ''): item for item in dados_api
    }

    # Garantir que as colunas da API existam no dataframe
    df['Status API Localiza'] = None
    df['Horímetro API Localiza'] = None

    status_list = []
    horimetro_list = []

    for idx, row in df.iterrows():
        apelido = row['Apelido']
        try:
            placa_busca = extrair_placa_do_apelido(apelido)
            dados = dados_por_placa.get(placa_busca)
            if dados:
                ignicao = dados.get('ignicao')
                if ignicao == '1':
                    status = 'Ligado'
                elif ignicao == '0':
                    status = 'Desligado'
                else:
                    status = 'Verificar'
                horimetro = dados.get('horimetro')
            else:
                status = 'Não Encontrado'
                horimetro = None
        except Exception as e:
            st.warning(f"Erro ao processar Apelido '{apelido}': {e}")
            status = 'Erro'
            horimetro = None

        status_list.append(status)
        horimetro_list.append(horimetro)

    df['Status API Localiza'] = status_list
    df['Horímetro API Localiza'] = horimetro_list

    return df


# Processamento do arquivo
if arquivo_excel is not None:
    try:
        # Lista de colunas esperadas
        colunas_esperadas = [
            'Filial', 'Série', 'Chassis', 'Horômetro', 'Marca', 'Modelo',
            'Tipo', 'Placa', 'Situação', 'Valor Locação',
            'Grupo Equipamento', 'Sub Grupo Equipamento', 'Observações',
            'Apelido'
        ]

        # Leitura do arquivo Excel
        df = pd.read_excel(arquivo_excel, usecols=colunas_esperadas)

        # Verificar colunas faltantes
        colunas_faltantes = [
            col for col in colunas_esperadas if col not in df.columns]
        if colunas_faltantes:
            st.error(
                f"As seguintes colunas estão faltando na planilha: {', '.join(colunas_faltantes)}")
            st.stop()

        # Verificar se a coluna Apelido está preenchida
        apelidos_vazios = df['Apelido'].isna().sum()
        if apelidos_vazios > 0:
            st.warning(
                f"⚠️ Existem {apelidos_vazios} equipamentos sem Apelido definido. O Apelido é necessário para integração com a API da Localiza."
            )

        # Buscar dados da API
        if validar_config_api():
            with st.spinner('Buscando dados da API...'):
                df = atualizar_dados_localizacao(df)
            st.success('Dados da API carregados com sucesso!')

        # Exibir estatísticas básicas
        st.subheader("Estatísticas Básicas")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Equipamentos", len(df))
        col2.metric("Quantidade de Filiais", df['Filial'].nunique())
        col3.metric("Tipos de Equipamentos", df['Tipo'].nunique())

        # Adicionar filtros
        st.subheader("Filtros")
        col1, col2, col3, col4 = st.columns(4)

        filial_filtro = col1.multiselect(
            "Filial",
            options=sorted(df['Filial'].dropna().unique())
        )

        tipo_filtro = col2.multiselect(
            "Tipo de Equipamento",
            options=sorted(df['Tipo'].dropna().unique())
        )

        situacao_filtro = col3.multiselect(
            "Situação",
            options=sorted(df['Situação'].dropna().unique())
        )

        status_existentes = df['Status API Localiza'].dropna().unique()
        status_options = sorted(status_existentes) if len(
            status_existentes) > 0 else []

        status_api_filtro = col4.multiselect(
            "Status API Localiza",
            options=status_options
        )

        # Aplicar filtros
        df_filtrado = df.copy()
        if filial_filtro:
            df_filtrado = df_filtrado[df_filtrado['Filial'].isin(
                filial_filtro)]
        if tipo_filtro:
            df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(tipo_filtro)]
        if situacao_filtro:
            df_filtrado = df_filtrado[df_filtrado['Situação'].isin(
                situacao_filtro)]
        if status_api_filtro:
            df_filtrado = df_filtrado[df_filtrado['Status API Localiza'].isin(
                status_api_filtro)]

        # Definir ordem das colunas
        colunas_ordenadas = [
            'Apelido', 'Placa', 'Status API Localiza', 'Horímetro API Localiza',
            'Horômetro', 'Série', 'Chassis', 'Filial', 'Marca', 'Modelo',
            'Tipo', 'Situação', 'Valor Locação', 'Grupo Equipamento',
            'Sub Grupo Equipamento', 'Observações'
        ]

        # Filtrar colunas existentes
        colunas_existentes = [
            col for col in colunas_ordenadas if col in df_filtrado.columns]

        # Exibir o DataFrame
        st.subheader("Dados dos Equipamentos")
        st.dataframe(
            df_filtrado[colunas_existentes],
            use_container_width=True,
            hide_index=True
        )

        # Botão de download
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download dos dados filtrados",
            data=csv,
            file_name="equipamentos_filtrados.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("👆 Por favor, faça o upload de uma planilha para começar.")
