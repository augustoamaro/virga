import streamlit as st
import pandas as pd

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

# Processamento do arquivo
if arquivo_excel is not None:
    try:
        # Lista de colunas esperadas (definida ANTES de ler o arquivo)
        colunas_esperadas = [
            'Filial', 'Série', 'Chassis', 'Horômetro', 'Marca', 'Modelo',
            'Tipo', 'Placa', 'Situação', 'Valor Locação',
            'Grupo Equipamento', 'Sub Grupo Equipamento', 'Observações'
        ]

        # Agora sim, leitura do arquivo Excel com as colunas específicas
        df = pd.read_excel(arquivo_excel, usecols=colunas_esperadas)

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

            # Exibir os dados em uma tabela
            st.subheader("Lista de Equipamentos")

            # Adicionar contador de registros
            total_filtrado = len(df_filtrado)
            total_geral = len(df)

            if filial_filtro or tipo_filtro or situacao_filtro:
                st.write(
                    f"Exibindo {total_filtrado} de {total_geral} equipamentos")
            else:
                st.write(f"Total de {total_geral} equipamentos")

            # Exibir a tabela
            st.dataframe(
                df_filtrado,
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
