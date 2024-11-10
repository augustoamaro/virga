import streamlit as st
import pandas as pd


def load_equipment_data(file):
    """Carrega e processa dados da planilha de equipamentos CRTI"""
    try:
        df = pd.read_excel(file)
        st.write("Número total de equipamentos CRTI:", len(df))
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha CRTI: {str(e)}")
        return pd.DataFrame()


def load_medicoes_data(file):
    """Carrega e processa dados da planilha de medições"""
    try:
        # Lê a planilha pulando as primeiras linhas que são cabeçalho
        df = pd.read_excel(file, skiprows=4)  # Pula as 4 primeiras linhas

        # Debug: mostra número de colunas
        st.write("Número de colunas na planilha:", len(df.columns))
        st.write("Colunas originais:", df.columns.tolist())

        # Cria lista de nomes de colunas com o tamanho exato do DataFrame
        num_cols = len(df.columns)
        colunas_base = [
            'Placa', 'Chassi', 'Modelo', 'Cliente', 'Cidade', 'Status',
            'Col7', 'Col8', 'Col9', 'Col10', 'Horimetro_Atual',
            'Data_Anterior', 'Horimetro_Anterior', 'Data_Atual',
            'Col15', 'Diferenca_Horimetro', 'Col17', 'Media_Diaria',
            'Col19', 'Ultima_Atualizacao', 'Status_Atualizacao'
        ]

        # Estende a lista de colunas se necessário
        while len(colunas_base) < num_cols:
            colunas_base.append(f'Col{len(colunas_base)+1}')

        # Usa apenas o número necessário de colunas
        colunas = colunas_base[:num_cols]

        # Debug: mostra nomes das colunas que serão usadas
        st.write("Nomes das colunas que serão aplicados:", colunas)

        # Atribui os nomes das colunas
        df.columns = colunas

        # Remove linhas vazias
        df = df.dropna(how='all')

        # Remove a primeira linha que contém os nomes originais
        df = df.iloc[1:].reset_index(drop=True)

        # Seleciona apenas as colunas relevantes que existem no DataFrame
        colunas_desejadas = [
            'Placa', 'Chassi', 'Modelo', 'Cliente', 'Cidade',
            'Horimetro_Atual', 'Data_Atual', 'Diferenca_Horimetro',
            'Media_Diaria', 'Ultima_Atualizacao', 'Status_Atualizacao'
        ]

        # Filtra apenas as colunas que existem
        colunas_existentes = [
            col for col in colunas_desejadas if col in df.columns]
        df_clean = df[colunas_existentes]

        # Debug: mostra informações do DataFrame processado
        st.write("Número total de medições:", len(df_clean))
        st.write("Colunas após processamento:", df_clean.columns.tolist())
        st.write("Primeiras linhas após processamento:", df_clean.head())

        return df_clean

    except Exception as e:
        st.error(f"Erro ao carregar planilha de medições: {str(e)}")
        st.write("Erro detalhado:", str(e))
        return pd.DataFrame()


def combine_data(df_crti, df_medicoes):
    """Combina os dados das duas planilhas usando Placa e Chassi"""
    try:
        # Cria cópias dos DataFrames para não modificar os originais
        df_crti = df_crti.copy()
        df_medicoes = df_medicoes.copy()

        # Padroniza os nomes das colunas para o merge
        df_crti['placa'] = df_crti['Placa:'].astype(str).str.strip()
        df_crti['chassi'] = df_crti['Chassis:'].astype(str).str.strip()

        # Padroniza os dados da planilha de medições
        df_medicoes['placa'] = df_medicoes['Placa'].astype(str).str.strip()
        df_medicoes['chassi'] = df_medicoes['Chassi'].astype(str).str.strip()

        # Realiza o merge usando placa e chassi
        merged_df = pd.merge(
            df_crti,
            df_medicoes,
            how='left',
            left_on=['placa', 'chassi'],
            right_on=['placa', 'chassi']
        )

        # Adiciona coluna de status de medição
        merged_df['Status_Medicao'] = merged_df['Horimetro_Atual'].notna().map(
            {True: 'COM MEDIÇÃO', False: 'SEM MEDIÇÃO'})

        # Adiciona informações de medição
        merged_df['Horimetro'] = merged_df['Horimetro_Atual']
        merged_df['Ultima_Medicao'] = merged_df['Data_Atual']
        merged_df['Media_Diaria'] = merged_df['Media_Diaria']

        return merged_df

    except Exception as e:
        st.error(f"Erro ao combinar dados: {str(e)}")
        st.write("Detalhes do erro:", str(e))
        return pd.DataFrame()


def main():
    st.title("Sistema de Monitoramento de Equipamentos")

    # Sidebar para uploads
    with st.sidebar:
        st.header("Arquivos de Dados")
        crti_file = st.file_uploader(
            "Planilha de Equipamentos (CRTI)",
            type=['xlsx'],
            help="Carregue a planilha base do CRTI"
        )

        medicoes_file = st.file_uploader(
            "Planilha de Medições",
            type=['xlsx'],
            help="Carregue a planilha de medições"
        )

    # Processa e exibe dados se tiver as planilhas
    if crti_file is not None:
        df_crti = load_equipment_data(crti_file)

        if medicoes_file is not None:
            df_medicoes = load_medicoes_data(medicoes_file)

            if not df_crti.empty and not df_medicoes.empty:
                # Combina os dados
                combined_df = combine_data(df_crti, df_medicoes)

                if not combined_df.empty:
                    # Adiciona filtros
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        cidade_filter = st.multiselect(
                            "Filtrar por Localização/Filial",
                            options=sorted(
                                combined_df['Localização/Filial Atual*:'].unique())
                        )
                    with col2:
                        cliente_filter = st.multiselect(
                            "Filtrar por Proprietário/Locador",
                            options=sorted(
                                combined_df['Proprietário ou Locador*:'].unique())
                        )
                    with col3:
                        medicao_filter = st.multiselect(
                            "Filtrar por Status de Medição",
                            options=['COM MEDIÇÃO', 'SEM MEDIÇÃO']
                        )

                    # Aplica os filtros
                    filtered_df = combined_df.copy()
                    if cidade_filter:
                        filtered_df = filtered_df[filtered_df['Localização/Filial Atual*:'].isin(
                            cidade_filter)]
                    if cliente_filter:
                        filtered_df = filtered_df[filtered_df['Proprietário ou Locador*:'].isin(
                            cliente_filter)]
                    if medicao_filter:
                        filtered_df = filtered_df[filtered_df['Status_Medicao'].isin(
                            medicao_filter)]

                    # Exibe o DataFrame
                    st.dataframe(filtered_df, use_container_width=True)

                    # Adiciona métricas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_equipamentos = len(filtered_df)
                        st.metric("Total de Equipamentos", total_equipamentos)
                    with col2:
                        total_clientes = filtered_df['Proprietário ou Locador*:'].nunique()
                        st.metric("Total de Clientes", total_clientes)
                    with col3:
                        com_medicao = len(
                            filtered_df[filtered_df['Status_Medicao'] == 'COM MEDIÇÃO'])
                        st.metric("Equipamentos com Medição", com_medicao)


if __name__ == "__main__":
    main()
