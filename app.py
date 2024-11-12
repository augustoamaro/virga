import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from urllib.parse import quote

# Configuração da página
st.set_page_config(
    page_title="Controle de Equipamentos",
    page_icon="🚛",
    layout="wide"
)

# Título da aplicação
st.title("📊 Sistema de Controle de Equipamentos")

# Upload do arquivo
st.subheader("Upload da Planilha")
arquivo_excel = st.file_uploader(
    "Selecione a planilha de equipamentos (Excel)",
    type=['xlsx', 'xls'],
    help="Faça upload de um arquivo Excel contendo os dados dos equipamentos"
)

# Configurações da API Localiza
API_CONFIG = {
    'token': 'WREPZVgbr6sih8jLgqgPwMo8RgrjhC59zKGObxLLSXb1H3UDaPw5OfHEMFVWoWqi',
    'user': '50282072080',
    'pass': 'HKJ@iu&0#23i*o9iu60T'
}

# Validar configuração da API


def validar_config_api():
    """Valida as configurações da API"""
    for campo in ['token', 'user', 'pass']:
        if not API_CONFIG.get(campo):
            st.error(f"Campo {campo} não configurado na API")
            return False
    return True


@st.cache_data(ttl=300)  # Cache por 5 minutos
def buscar_dados_api():
    """Função para buscar dados da API da Localiza"""
    try:
        # URL base direta
        base_url = 'http://sistema.localizarastreamento.com/integracao/mestre/getVeiculos.php'

        # Headers com os parâmetros de autenticação
        headers = {
            'Accept': 'application/json',
            'token': API_CONFIG['token'],
            'user': API_CONFIG['user'],
            'pass': API_CONFIG['pass']
        }

        # Fazer a requisição com os parâmetros no header
        response = requests.get(
            base_url,
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            st.error(f"Erro na API. Status Code: {response.status_code}")
            return None

        try:
            dados = response.json()
            return dados if isinstance(dados, list) and len(dados) > 0 else None

        except json.JSONDecodeError as e:
            st.error(f"Erro ao decodificar JSON: {str(e)}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição: {str(e)}")
        return None


def atualizar_dados_localizacao(df):
    """Atualiza os dados de localização dos equipamentos"""
    dados_api = buscar_dados_api()

    if dados_api:
        # Criar um dicionário para fácil acesso aos dados da API
        dados_por_placa = {item['placa']: item for item in dados_api}

        # Criar novas colunas se não existirem
        novas_colunas = [
            'Última Atualização', 'Ignição', 'Velocidade', 'Latitude',
            'Longitude', 'Hodômetro API', 'Horímetro API',
            'Status API Localiza', 'Placa API'
        ]

        for coluna in novas_colunas:
            if coluna not in df.columns:
                df[coluna] = ''

        # Atualizar dados usando o Apelido
        for idx, row in df.iterrows():
            try:
                apelido = str(row['Apelido']).strip()
                placa_do_apelido = apelido.split(
                    '|')[1].strip() if '|' in apelido else apelido

                # Procurar pela placa que corresponde ao apelido
                for placa, dados in dados_por_placa.items():
                    if placa.strip().upper() == placa_do_apelido.upper():
                        # Atualizar Status API Localiza baseado no valor de ignição
                        if dados['ignicao'] == '1':
                            df.loc[idx, 'Status API Localiza'] = 'Ligado'
                        elif dados['ignicao'] == '0':
                            df.loc[idx, 'Status API Localiza'] = 'Desligado'
                        else:
                            df.loc[idx, 'Status API Localiza'] = 'Verificar'

                        # Atualizar outros campos
                        df.loc[idx, 'Placa API'] = placa
                        df.loc[idx, 'Ignição'] = 'Ligado' if dados['ignicao'] == '1' else 'Desligado'
                        df.loc[idx, 'Velocidade'] = dados['velocidade']
                        df.loc[idx, 'Latitude'] = dados['latitude']
                        df.loc[idx, 'Longitude'] = dados['longitude']
                        df.loc[idx, 'Hodômetro API'] = dados['odometro']
                        df.loc[idx, 'Horímetro API'] = dados['horimetro']
                        break

            except Exception as e:
                st.warning(f"Erro ao processar Apelido '{apelido}': {str(e)}")
                df.loc[idx, 'Status API Localiza'] = 'Erro'

    return df


# Processamento do arquivo
if arquivo_excel is not None:
    try:
        # Lista de colunas esperadas (adicionando a coluna Apelido)
        colunas_esperadas = [
            'Filial', 'Série', 'Chassis', 'Horômetro', 'Marca', 'Modelo',
            'Tipo', 'Placa', 'Situação', 'Valor Locação',
            'Grupo Equipamento', 'Sub Grupo Equipamento', 'Observações',
            'Apelido'  # Nova coluna adicionada
        ]

        # Agora sim, leitura do arquivo Excel com as colunas específicas
        df = pd.read_excel(arquivo_excel, usecols=colunas_esperadas)

        # Verificar se a coluna Apelido está preenchida
        apelidos_vazios = df['Apelido'].isna().sum()
        if apelidos_vazios > 0:
            st.warning(
                f"⚠️ Existem {apelidos_vazios} equipamentos sem Apelido definido. O Apelido é necessário para integração com a API da Localiza.")

        # Verificar se todas as colunas necessárias estão presentes
        colunas_faltantes = [
            col for col in colunas_esperadas if col not in df.columns]

        if colunas_faltantes:
            st.error(
                f"As seguintes colunas estão faltando na planilha: {', '.join(colunas_faltantes)}")
        else:
            # Exibir estatísticas básicas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Equipamentos", len(df))
            with col2:
                st.metric("Quantidade de Filiais", df['Filial'].nunique())
            with col3:
                st.metric("Tipos de Equipamentos", df['Tipo'].nunique())

            # Adicionar filtros
            st.subheader("Filtros")
            col1, col2, col3 = st.columns(3)

            with col1:
                filial_filtro = st.multiselect(
                    "Filial",
                    options=sorted(df['Filial'].unique())
                )

            with col2:
                tipo_filtro = st.multiselect(
                    "Tipo de Equipamento",
                    options=sorted(df['Tipo'].unique())
                )

            with col3:
                situacao_filtro = st.multiselect(
                    "Situação",
                    options=sorted(df['Situação'].unique())
                )

            # Aplicar filtros
            df_filtrado = df.copy()
            if filial_filtro:
                df_filtrado = df_filtrado[df_filtrado['Filial'].isin(
                    filial_filtro)]
            if tipo_filtro:
                df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(
                    tipo_filtro)]
            if situacao_filtro:
                df_filtrado = df_filtrado[df_filtrado['Situação'].isin(
                    situacao_filtro)]

            # Após carregar o DataFrame, adicionar botão para atualizar dados da API
            if st.button("🔄 Atualizar Dados da Localiza"):
                if validar_config_api():
                    with st.spinner('Buscando dados da API...'):
                        # Atualizar o DataFrame original
                        df = atualizar_dados_localizacao(df)

                        # Garantir que as colunas da API existam no DataFrame filtrado
                        df_filtrado = df.copy()

                        # Reaplicar os filtros
                        if filial_filtro:
                            df_filtrado = df_filtrado[df_filtrado['Filial'].isin(
                                filial_filtro)]
                        if tipo_filtro:
                            df_filtrado = df_filtrado[df_filtrado['Tipo'].isin(
                                tipo_filtro)]
                        if situacao_filtro:
                            df_filtrado = df_filtrado[df_filtrado['Situação'].isin(
                                situacao_filtro)]

                    st.success('Dados atualizados com sucesso!')

                    # Definir ordem específica das colunas
                    colunas_ordenadas = [
                        'Apelido',
                        'Placa',
                        'Status API Localiza',
                        'Placa API',
                        'Ignição',
                        'Velocidade',
                        'Horímetro API',
                        'Latitude',
                        'Longitude',
                        'Filial',
                        'Série',
                        'Chassis',
                        'Horômetro',
                        'Marca',
                        'Modelo',
                        'Tipo',
                        'Situação',
                        'Valor Locação',
                        'Grupo Equipamento',
                        'Sub Grupo Equipamento'
                    ]

                    # Filtrar apenas as colunas que existem no DataFrame
                    colunas_existentes = [
                        col for col in colunas_ordenadas if col in df_filtrado.columns]

                    # Exibir o DataFrame com as colunas ordenadas
                    st.dataframe(
                        df_filtrado[colunas_existentes],
                        use_container_width=True,
                        hide_index=True
                    )

            else:
                # Exibição normal quando não houver atualização
                st.subheader("Lista de Equipamentos")

                # Usar a mesma ordem de colunas para a exibição normal
                colunas_ordenadas = [
                    'Apelido',
                    'Placa',
                    'Filial',
                    'Série',
                    'Chassis',
                    'Horômetro',
                    'Marca',
                    'Modelo',
                    'Tipo',
                    'Situação',
                    'Valor Locação',
                    'Grupo Equipamento',
                    'Sub Grupo Equipamento'
                ]

                # Filtrar apenas as colunas que existem no DataFrame
                colunas_existentes = [
                    col for col in colunas_ordenadas if col in df_filtrado.columns]

                st.dataframe(
                    df_filtrado[colunas_existentes],
                    use_container_width=True,
                    hide_index=True
                )

            # Adicionar botão para download dos dados filtrados
            st.download_button(
                label="📥 Download dos dados filtrados",
                data=df_filtrado.to_csv(index=False).encode('utf-8'),
                file_name="equipamentos_filtrados.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
else:
    st.info("👆 Por favor, faça o upload de uma planilha para começar.")
